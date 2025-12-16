import csv
import os
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from ..exceptions import AbromicsAPIError


class TsvProcessor:
    
    def __init__(self, client):
       
        self.client = client
    
    def create_samples_from_tsv(
        self,
        project_id: int,
        tsv_file: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict[str, Any]]:
       
        if not os.path.exists(tsv_file):
            raise FileNotFoundError(f"TSV file not found: {tsv_file}")
        
        # Parse TSV file
        samples_data = self._parse_tsv(tsv_file)
        
        if not samples_data:
            raise ValueError("No data found in TSV file")
        
        results = []
        total_samples = len(samples_data)
        
        for i, sample_data in enumerate(samples_data):
            sample_id = sample_data.get('original_sample_id', sample_data.get('sample_name', f'sample_{i+1}'))
            
            if progress_callback:
                progress_callback(i, total_samples, sample_id)
            
            try:
                # Create sample
                sample = self.client.samples.create(
                    project_id=project_id,
                    metadata=sample_data
                )
                
                results.append({
                    'sample_name': sample_id,
                    'sample_id': sample.id,
                    'success': True,
                    'error': None
                })
                
            except Exception as e:
                results.append({
                    'sample_name': sample_id,
                    'sample_id': None,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def _parse_tsv(self, tsv_file: str) -> List[Dict[str, Any]]:

        samples_data = []
        
        with open(tsv_file, 'r', encoding='utf-8') as file:
            if tsv_file.endswith('.tsv'):
                delimiter = '\t'
            else:
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(file, delimiter=delimiter)

            def normalize_header(header: str) -> str:
                key = (header or '').strip()
                if key.endswith('*'):
                    key = key[:-1]
                key = ' '.join(key.split())
                key = key.lower()
                key = key.replace(' ', '_').replace('/', '_')
                return key

            def map_header(header: str) -> str:
                h = normalize_header(header)
                mappings = {
                    'project_name': 'project',
                    'project': 'project',
                    'sample_id': 'original_sample_id',
                    'sample_name': 'sample_name',
                    'strain_id': 'strain_id',
                    'microorganism_scientific_name': 'scientific_name',
                    'collected_date': 'collected_date',
                    'host_species': 'species',
                    'instrument_model': 'instrument',
                    'sample_type': 'type',
                    'sample_source': 'name',
                    'country': 'country_id',
                    'region': 'country_level1_id',
                    'place': 'place_id',
                    'travel_countries': 'travel_countries',
                    'accession_number': 'accession_number',
                    'sample_comment': 'comments',
                    'r1_fastq_filename': 'r1_fastq_filename',
                    'r2_fastq_filename': 'r2_fastq_filename',
                    'fasta_filename': 'fasta_filename',
                }
                return mappings.get(h, h)
            
            for row in reader:
                sample_data = {}
                for key, value in row.items():
                    mapped_key = map_header(key)
                    if value and str(value).strip():
                        clean_value = str(value).strip()
                        if clean_value.isdigit():
                            sample_data[mapped_key] = int(clean_value)
                        else:
                            sample_data[mapped_key] = clean_value
                
                if 'sample_name' not in sample_data and 'sample_id' in sample_data:
                    sample_data['sample_name'] = str(sample_data['sample_id'])
                
                if not sample_data.get('species'):
                    alt_species = sample_data.get('organism') or sample_data.get('species_name')
                    if alt_species:
                        sample_data['species'] = alt_species
                    else:
                        continue 
                
                if 'sample_name' not in sample_data:
                    sample_data['sample_name'] = f"sample_{len(samples_data) + 1}"
                
                samples_data.append(sample_data)
        
        return samples_data
    


