import os
import glob
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from ..upload.tus_client import TusUploader
from ..exceptions import AbromicsAPIError


class BatchUploader:

    def __init__(self, client):
       
        self.client = client
    
    def upload_files_for_project(
        self,
        project_id: int,
        files_directory: str,
        file_pattern: str = "*.fastq.gz",
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        tsv_data: Optional[List[Dict[str, Any]]] = None,
        exclude_sample_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        
        if not os.path.exists(files_directory):
            raise FileNotFoundError(f"Directory not found: {files_directory}")
        
        all_experiments = []
        page = 1
        page_size = 100
        
        while True:
            response = self.client.get(
                f'/api/experiment/informations/?project_id={project_id}&ordering=-create_time&page_size={page_size}&page={page}'
            )
            experiments_data = response.json()
            
            if 'results' in experiments_data:
                experiments = experiments_data['results']
                if not experiments:  
                    break
                all_experiments.extend(experiments)
                if experiments_data.get('next'):
                    page += 1
                else:
                    break
            else:
                experiments = experiments_data if isinstance(experiments_data, list) else [experiments_data]
                all_experiments.extend(experiments)
                break
        
        all_samples = []
        for experiment in all_experiments:
            for sample in experiment.get('samples', []):
                all_samples.append(sample)
        
        if not all_samples:
            raise ValueError(f"No samples found for project {project_id}")
        
        project_name = None
        if all_experiments and tsv_data:
            first_experiment = all_experiments[0]
            if 'project' in first_experiment and isinstance(first_experiment['project'], dict):
                project_name = first_experiment['project'].get('name')
            elif 'project_name' in first_experiment:
                project_name = first_experiment['project_name']
            
            if not project_name:
                try:
                    from ..models.project import ProjectManager
                    project_manager = ProjectManager(self.client)
                    project = project_manager.get(project_id)
                    project_name = project.name
                except Exception:
                    pass
        
        filtered_tsv_data = None
        if tsv_data and project_name:
            filtered_tsv_data = []
            for tsv_row in tsv_data:
                tsv_project = tsv_row.get('project') or tsv_row.get('Project Name') or tsv_row.get('Project Name*')
                if tsv_project and str(tsv_project).strip().lower() == str(project_name).strip().lower():
                    filtered_tsv_data.append(tsv_row)
        elif tsv_data:
            filtered_tsv_data = tsv_data
        
        samples = []
        for sample_data in all_samples:
            class SampleObj:
                def __init__(self, data):
                    self.id = data.get('id')
                    self.sample_name = data.get('original_sample_id', f'sample_{self.id}')
                    self.raw_sample_data = data
            
            samples.append(SampleObj(sample_data))
        
        files_pattern = os.path.join(files_directory, file_pattern)
        file_paths = glob.glob(files_pattern)
        
        # If TSV data is provided, restrict uploads strictly to filenames listed in TSV
        if filtered_tsv_data:
            allowed_basenames = set()
            for sd in filtered_tsv_data:
                for key in ('r1_fastq_filename', 'r2_fastq_filename', 'fasta_filename'):
                    fn = sd.get(key)
                    if fn:
                        allowed_basenames.add(os.path.basename(str(fn)))
            if allowed_basenames:
                file_paths = [p for p in file_paths if os.path.basename(p) in allowed_basenames]
        
        if not file_paths:
            raise ValueError(f"No files found matching pattern: {files_pattern}")
        
        file_sample_matches = self._match_files_to_samples(
            file_paths, samples, exclude_sample_names or [], filtered_tsv_data
        )
        
        file_type_mapping = {}
        if filtered_tsv_data:
            for sample_data in filtered_tsv_data:
                r1_filename = sample_data.get('r1_fastq_filename', '')
                r2_filename = sample_data.get('r2_fastq_filename', '')
                fasta_filename = sample_data.get('fasta_filename', '')
                
                if r1_filename:
                    file_type_mapping[os.path.basename(r1_filename)] = 'paired_r1'
                if r2_filename:
                    file_type_mapping[os.path.basename(r2_filename)] = 'paired_r2'
                if fasta_filename:
                    file_type_mapping[os.path.basename(fasta_filename)] = 'fasta'
        
        filtered_matches = []
        for file_path, sample_id, sample_name, file_info in file_sample_matches:
            filename = os.path.basename(file_path)
            sample_obj = None
            for sample in samples:
                if sample.id == sample_id:
                    sample_obj = sample
                    break
            
            if sample_obj:
                raw_input_files = sample_obj.raw_sample_data.get('rawinputfiles', [])
                
                expected_type = file_type_mapping.get(filename)
                if not expected_type:
                    if filename.endswith('.fasta') or filename.endswith('.fa'):
                        expected_type = 'fasta'
                    else:
                        expected_type = 'paired_r1'  
                
                matching_file = None
                for f in raw_input_files:
                    if f.get('type') == expected_type and (not f.get('tus_file') or f.get('tus_file', '') == ''):
                        matching_file = f
                        break
                
                if matching_file:
                    filtered_matches.append((file_path, sample_id, sample_name, file_info))
        
        results = []
        total_files = len(filtered_matches)
        skipped_count = len(file_sample_matches) - len(filtered_matches)
        
        if skipped_count > 0:
            for file_path, sample_id, sample_name, file_info in file_sample_matches:
                if (file_path, sample_id, sample_name, file_info) not in filtered_matches:
                    filename = os.path.basename(file_path)
                    sample_obj = None
                    for sample in samples:
                        if sample.id == sample_id:
                            sample_obj = sample
                            break
                    
                    expected_type = file_type_mapping.get(filename)
                    if not expected_type:
                        if filename.endswith('.fasta') or filename.endswith('.fa'):
                            expected_type = 'fasta'
                        else:
                            expected_type = 'paired_r1'
                    
                    error_msg = f'No available {expected_type} slot for sample {sample_name}'
                    if sample_obj:
                        raw_input_files = sample_obj.raw_sample_data.get('rawinputfiles', [])
                        slots_of_type = [f for f in raw_input_files if f.get('type') == expected_type]
                        if slots_of_type:
                            filled = [f for f in slots_of_type if f.get('tus_file') and f.get('tus_file', '').strip() != '']
                            error_msg += f' ({len(filled)}/{len(slots_of_type)} slots already have files uploaded)'
                    
                    results.append({
                        'file_path': file_path,
                        'sample_id': sample_id,
                        'sample_name': sample_name,
                        'tus_url': None,
                        'raw_input_file_id': None,
                        'success': False,
                        'error': error_msg
                    })
        
        for i, (file_path, sample_id, sample_name, file_info) in enumerate(filtered_matches):
            filename = os.path.basename(file_path)
            
            if progress_callback:
                progress_callback(i, total_files, filename)
            
            try:
                sample_obj = None
                for sample in samples:
                    if sample.id == sample_id:
                        sample_obj = sample
                        break
                
                if not sample_obj:
                    results.append({
                        'file_path': file_path,
                        'sample_id': sample_id,
                    'tus_url': None,
                        'raw_input_file_id': None,
                        'success': False,
                    'error': f'Sample {sample_id} not found',
                    'sample_name': sample_name
                    })
                    continue
                
                raw_input_files = sample_obj.raw_sample_data.get('rawinputfiles', [])
                
                expected_type = file_type_mapping.get(filename)
                if not expected_type:
                    if filename.endswith('.fasta') or filename.endswith('.fa'):
                        expected_type = 'fasta'
                    else:
                        expected_type = 'paired_r1' 
                
                matching_file = None
                for f in raw_input_files:
                    if f.get('type') == expected_type and (not f.get('tus_file') or f.get('tus_file', '') == ''):
                        matching_file = f
                        break
                
                if not matching_file:
                    slots_of_type = [f for f in raw_input_files if f.get('type') == expected_type]
                    if not slots_of_type:
                        error_msg = f'No {expected_type} slot exists for sample {sample_name} (sample may need to be created with this file type)'
                    else:
                        filled_slots = [f for f in slots_of_type if f.get('tus_file') and f.get('tus_file', '').strip() != '']
                        if filled_slots:
                            error_msg = f'No available {expected_type} slot for sample {sample_name} ({len(filled_slots)}/{len(slots_of_type)} slots already have files uploaded)'
                        else:
                            error_msg = f'No available {expected_type} slot for sample {sample_name} (all {len(slots_of_type)} slot(s) are reserved or in use)'
                    
                    results.append({
                        'file_path': file_path,
                        'sample_id': sample_id,
                        'sample_name': sample_name,
                        'tus_url': None,
                        'raw_input_file_id': None,
                        'success': False,
                        'error': error_msg
                    })
                    continue
                
                raw_input_file_id = matching_file['id']
                
                uploader = self.client.upload.create_uploader()
                tus_url = uploader.upload_file(
                    file_path=file_path,
                    metadata=file_info['metadata']
                )
                
                patch_data = {
                    'tus_file': tus_url,
                    'original_name': filename
                }
                
                try:
                    response = self.client.patch(f'/api/raw_input_file/{raw_input_file_id}/', data=patch_data)
                    updated_raw_input_file = response.json()
                    
                    results.append({
                        'file_path': file_path,
                        'sample_id': sample_id,
                        'sample_name': sample_name,
                        'tus_url': tus_url,
                        'raw_input_file_id': raw_input_file_id,
                        'success': True,
                        'error': None
                    })
                except Exception as patch_error:
                    error_message = str(patch_error)
                    if hasattr(patch_error, 'response') and patch_error.response is not None:
                        try:
                            error_data = patch_error.response.json()
                            if 'error' in error_data:
                                error_message = error_data['error']
                        except (ValueError, KeyError):
                            pass
                    
                    results.append({
                        'file_path': file_path,
                        'sample_id': sample_id,
                        'sample_name': sample_name,
                        'tus_url': tus_url,
                        'raw_input_file_id': raw_input_file_id,
                        'success': False,
                        'error': error_message
                    })
                    continue
                
                for f in raw_input_files:
                    if f['id'] == raw_input_file_id:
                        f['tus_file'] = tus_url
                        break
                
            except Exception as e:
                results.append({
                    'file_path': file_path,
                    'sample_id': sample_id,
                    'sample_name': sample_name,
                    'tus_url': None,
                    'raw_input_file_id': None,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def upload_files_for_samples(
        self,
        samples: List[Dict[str, Any]],
        files_directory: str,
        file_pattern: str = "*.fastq.gz",
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict[str, Any]]:
        if not os.path.exists(files_directory):
            raise FileNotFoundError(f"Directory not found: {files_directory}")
        
        files_pattern = os.path.join(files_directory, file_pattern)
        file_paths = glob.glob(files_pattern)
        
        if not file_paths:
            raise ValueError(f"No files found matching pattern: {files_pattern}")
        
        file_sample_matches = self._match_files_to_samples(file_paths, samples, [])
        
        results = []
        total_files = len(file_sample_matches)
        
        for i, (file_path, sample_id, file_info) in enumerate(file_sample_matches):
            filename = os.path.basename(file_path)
            
            if progress_callback:
                progress_callback(i, total_files, filename)
            
            try:
                uploader = self.client.upload.create_uploader()
                tus_url = uploader.upload_file(
                    file_path=file_path,
                    metadata=file_info['metadata']
                )
                
                raw_input_data = {
                    'tus_file': tus_url,
                    'original_name': filename,
                    'file_type': file_info['file_type'],
                    'type': file_info['type'],
                    'sample': sample_id
                }
                
                response = self.client.post('/api/raw_input_file/', data=raw_input_data)
                raw_input_file = response.json()
                
                results.append({
                    'file_path': file_path,
                    'sample_id': sample_id,
                    'tus_url': tus_url,
                    'raw_input_file_id': raw_input_file['id'],
                    'success': True,
                    'error': None
                })
                
            except Exception as e:
                results.append({
                    'file_path': file_path,
                    'sample_id': sample_id,
                    'tus_url': None,
                    'raw_input_file_id': None,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def _match_files_to_samples(
        self, 
        file_paths: List[str], 
        samples: List[Any],
        exclude_sample_names: List[str],
        tsv_data: Optional[List[Dict[str, Any]]] = None
    ) -> List[tuple]:

        matches = []
        
        sample_lookup = {}
        for sample in samples:
            if hasattr(sample, 'id'):
                sample_id = sample.id
                sample_name = getattr(sample, 'sample_name', f'sample_{sample.id}')
            else:
                sample_id = sample['id']
                sample_name = sample.get('sample_name', f'sample_{sample_id}')
            
            sample_lookup[sample_name] = sample_id
        
        DEMO_FILES = {'ARDIG49_1.fastq.gz', 'ARDIG49_2.fastq.gz', 'ARDIG49.fasta'}
        
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            
            matched_sample_id = None
            matched_sample_name = None
            matched_filename_col = None
            
            is_demo_file = filename in DEMO_FILES
            
            if tsv_data and not is_demo_file:
                # Determine file_info from TSV column instead of filename patterns
                for tsv_row in tsv_data:
                    for filename_col in ('r1_fastq_filename', 'r2_fastq_filename', 'fasta_filename'):
                        tsv_filename = tsv_row.get(filename_col)
                        if tsv_filename:
                            if os.path.basename(str(tsv_filename)) == filename:
                                matched_sample_name = tsv_row.get('original_sample_id') or tsv_row.get('sample_name')
                                if matched_sample_name and matched_sample_name in sample_lookup:
                                    matched_sample_id = sample_lookup[matched_sample_name]
                                    matched_filename_col = filename_col
                                    break
                    
                    if matched_sample_id:
                        break
                
                # Determine file_info from the matched TSV column
                if matched_filename_col:
                    file_info = self._get_file_info_from_tsv_column(matched_filename_col, filename)
                else:
                    # File not found in TSV, skip it
                    continue
            else:
                # No TSV data or demo file - use filename analysis
                file_info = self._analyze_file(filename)
            
            if is_demo_file:
                if tsv_data:
                    for tsv_row in tsv_data:
                        sample_name = tsv_row.get('original_sample_id') or tsv_row.get('sample_name')
                        if sample_name and sample_name not in set(exclude_sample_names) and sample_name in sample_lookup:
                            sample_id = sample_lookup[sample_name]
                            matches.append((file_path, sample_id, sample_name, file_info))
                else:
                    for sample_name in sample_lookup.keys():
                        if sample_name not in set(exclude_sample_names):
                            sample_id = sample_lookup[sample_name]
                            matches.append((file_path, sample_id, sample_name, file_info))
            elif matched_sample_id:
                # Skip excluded sample names
                if matched_sample_name in set(exclude_sample_names):
                    continue
                matches.append((file_path, matched_sample_id, matched_sample_name, file_info))
        
        return matches
    
    def _get_file_info_from_tsv_column(self, filename_col: str, filename: str) -> Dict[str, Any]:
        file_info = {
            'metadata': {
                'filename': filename,
            }
        }
        
        if filename_col == 'r1_fastq_filename':
            file_info['file_type'] = 'fastqsanger.gz'
            file_info['type'] = 'paired_r1'
        elif filename_col == 'r2_fastq_filename':
            file_info['file_type'] = 'fastqsanger.gz'
            file_info['type'] = 'paired_r2'
        elif filename_col == 'fasta_filename':
            file_info['file_type'] = 'fasta'
            file_info['type'] = 'fasta'
        else:
            # Fallback
            file_info['file_type'] = 'fastqsanger.gz'
            file_info['type'] = 'single'
        
        file_info['metadata']['filetype'] = file_info['file_type']
        
        return file_info
    
    def _analyze_file(self, filename: str) -> Dict[str, Any]:
        file_info = {
            'file_type': 'fastqsanger.gz',
            'type': 'single',
            'metadata': {}
        }
        
        if filename.endswith('.fastq.gz') or filename.endswith('.fq.gz'):
            file_info['file_type'] = 'fastqsanger.gz'
        elif filename.endswith('.fastq') or filename.endswith('.fq'):
            file_info['file_type'] = 'fastq'
        elif filename.endswith('.fa') or filename.endswith('.fasta'):
            file_info['file_type'] = 'fasta'
        
        if 'R1' in filename or '_1' in filename:
            file_info['type'] = 'paired_r1'
        elif 'R2' in filename or '_2' in filename:
            file_info['type'] = 'paired_r2'
        elif 'assembly' in filename.lower():
            file_info['type'] = 'single'
        
        file_info['metadata'] = {
            'filename': filename,
            'filetype': file_info['file_type']
        }
        
        return file_info



