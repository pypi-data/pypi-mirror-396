from typing import List, Dict, Any, Optional, Callable
from .tsv_processor import TsvProcessor
from .batch_uploader import BatchUploader


class BatchProcessor:

    def __init__(self, client):
       
        self.client = client
        self.tsv_processor = TsvProcessor(client)
        self.batch_uploader = BatchUploader(client)
    
    def process_tsv_and_upload(
        self,
        project_id: int,
        tsv_file: str,
        files_directory: str,
        file_pattern: str = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, Any]:
        import os
        import glob
        
        # Auto-detect file pattern if not provided
        if file_pattern is None:
            fastq_files = glob.glob(os.path.join(files_directory, "*.fastq.gz")) + glob.glob(os.path.join(files_directory, "*.fq.gz"))
            fasta_files = glob.glob(os.path.join(files_directory, "*.fasta")) + glob.glob(os.path.join(files_directory, "*.fa"))
            
            if fastq_files and fasta_files:
                raise ValueError("Mixed file types detected (both FASTQ and FASTA). Please separate them into different directories.")
            elif fastq_files:
                file_pattern = "*.fastq.gz"
            elif fasta_files:
                file_pattern = "*.fasta"
            else:
                raise ValueError("No supported sequence files found (*.fastq.gz, *.fq.gz, *.fasta, *.fa)")
        
        results = {
            'tsv_processing': None,
            'file_upload': None,
            'success': False,
            'error': None
        }
        
        try:
            # Step 1: Process TSV and create samples
            if progress_callback:
                progress_callback("Creating samples from TSV", 0, 1)
            
            tsv_results = self.tsv_processor.create_samples_from_tsv(
                project_id=project_id,
                tsv_file=tsv_file,
                progress_callback=lambda current, total, sample_name: progress_callback(
                    f"Creating sample: {sample_name}", current, total
                ) if progress_callback else None
            )
            
            results['tsv_processing'] = tsv_results
            
            successful_samples = [
                r for r in tsv_results if r['success']
            ]
            
            if not successful_samples:
                results['error'] = "No samples were created successfully"
                return results
            
            # Step 2: Upload files
            if progress_callback:
                progress_callback("Uploading files", 0, 1)
            
            upload_results = self.batch_uploader.upload_files_for_project(
                project_id=project_id,
                files_directory=files_directory,
                file_pattern=file_pattern,
                progress_callback=lambda current, total, filename: progress_callback(
                    f"Uploading: {filename}", current, total
                ) if progress_callback else None
            )
            
            results['file_upload'] = upload_results
            results['success'] = True
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def validate_tsv(self, tsv_file: str) -> Dict[str, Any]:
        return self.tsv_processor.validate_tsv(tsv_file)
    
    def create_samples_from_tsv(
        self,
        project_id: int,
        tsv_file: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict[str, Any]]:
      
        return self.tsv_processor.create_samples_from_tsv(
            project_id=project_id,
            tsv_file=tsv_file,
            progress_callback=progress_callback
        )
    
    def upload_files_for_project(
        self,
        project_id: int,
        files_directory: str,
        file_pattern: str = "*.fastq.gz",
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        tsv_data: Optional[List[Dict[str, Any]]] = None,
        exclude_sample_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
       
        return self.batch_uploader.upload_files_for_project(
            project_id=project_id,
            files_directory=files_directory,
            file_pattern=file_pattern,
            progress_callback=progress_callback,
            tsv_data=tsv_data,
            exclude_sample_names=exclude_sample_names or []
        )


