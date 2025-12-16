import os
import time
from typing import Optional, Dict, Any, Callable, List
import requests

try:
    from tusclient import client as _tus_client_module
    from tusclient import uploader as _tus_uploader_module
    from tusclient.exceptions import TusUploadFailed, TusCommunicationError
    TusClient = _tus_client_module.TusClient
    TusUploaderImpl = _tus_uploader_module.Uploader
    TUSPY_AVAILABLE = True
except ImportError:
    TUSPY_AVAILABLE = False
    class TusClient:
        def __init__(self, *args, **kwargs):
            raise ImportError("tuspy is not installed. Install it with: pip install tuspy")
    
    class TusUploadFailed(Exception):
        pass
    
    class TusCommunicationError(Exception):
        pass


class TusUploader:
    def __init__(
        self, 
        base_url: str,
        chunk_size: int = 10 * 1024 * 1024,  # 10MB chunks (same as frontend)
        retry_delay: float = 1.0,
        max_retries: int = 5
    ):
        if not TUSPY_AVAILABLE:
            raise ImportError("tuspy is not installed. Install it with: pip install tuspy")
        
        self.base_url = base_url.rstrip('/')
        self.tus_endpoint = f"{self.base_url}/files/"
        self.chunk_size = chunk_size
        self.retry_delay = retry_delay
        self.max_retries = max_retries
        
        # Initialize TUS client
        self.tus_client = TusClient(self.tus_endpoint)
    
    def upload_file(
        self,
        file_path: str,
        metadata: Optional[Dict[str, str]] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        **kwargs
    ) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        upload_metadata = metadata or {}
        upload_metadata.update({
            'filename': os.path.basename(file_path),
            'filetype': self._get_file_type(file_path)
        })
        
        tus_options = {
            'chunk_size': self.chunk_size,
            'metadata': upload_metadata,
            'retry_delay': self.retry_delay,
            'max_retries': self.max_retries,
            **kwargs
        }
        
        if progress_callback:
            tus_options['on_progress'] = progress_callback
        
        try:
            uploader = TusUploaderImpl(
                client=self.tus_client,
                file_path=file_path,
                chunk_size=self.chunk_size,
                metadata=upload_metadata,
                retries=self.max_retries,
                retry_delay=self.retry_delay,
            )
            uploader.upload()
            return uploader.url
        except (TusUploadFailed, TusCommunicationError) as e:
            raise TusUploadFailed(f"TUS upload failed: {str(e)}") from e
        except Exception as e:
            raise TusUploadFailed(f"TUS upload failed: {str(e)}") from e
    
    def upload_files(
        self,
        files: List[Dict[str, Any]],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        results = []
        total_files = len(files)
        
        for i, file_info in enumerate(files):
            file_path = file_info['path']
            metadata = file_info.get('metadata', {})
            
            if progress_callback:
                progress_callback(i, total_files, os.path.basename(file_path))
            
            try:
                tus_url = self.upload_file(
                    file_path=file_path,
                    metadata=metadata,
                    progress_callback=lambda uploaded, total: progress_callback(
                        i, total_files, f"{os.path.basename(file_path)} ({uploaded}/{total})"
                    ) if progress_callback else None,
                    **kwargs
                )
                
                results.append({
                    'file_path': file_path,
                    'tus_url': tus_url,
                    'success': True,
                    'error': None
                })
            except Exception as e:
                results.append({
                    'file_path': file_path,
                    'tus_url': None,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def _get_file_type(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.fastq':
            return 'FASTQ'
        elif ext == '.fq':
            return 'FASTQ'
        elif ext == '.fastq.gz':
            return 'FASTQ_GZ'
        elif ext == '.fq.gz':
            return 'FASTQ_GZ'
        elif ext == '.fa':
            return 'FASTA'
        elif ext == '.fasta':
            return 'FASTA'
        elif ext == '.fna':
            return 'FASTA'
        else:
            return 'UNKNOWN'


class UploadManager:
    def __init__(self, client):
        self.client = client
    
    def create_uploader(self, base_url: str = None, **kwargs) -> TusUploader:
        if base_url is None:
            base_url = self.client.base_url
        
        if self._is_local_dev(base_url):
            if '://' in base_url:
                scheme, rest = base_url.split('://', 1)
                if ':' in rest and not rest.startswith('['):  
                    host = rest.split(':')[0]
                else:
                    host = rest.rstrip('/')
                base_url = f"{scheme}://{host}:1080"
        
        return TusUploader(
            base_url=base_url,
            **kwargs
        )
    
    def _is_local_dev(self, base_url: str) -> bool:
        local_indicators = [
            'localhost',
            '127.0.0.1',
            '0.0.0.0',
            '::1',
            'host.docker.internal',
        ]
        
        if '://' in base_url:
            hostname = base_url.split('://')[1].split(':')[0].split('/')[0]
        else:
            hostname = base_url.split(':')[0].split('/')[0]
        
        return any(indicator in hostname.lower() for indicator in local_indicators)
    
    def upload_sample_files(
        self,
        sample_id: int,
        files: List[Dict[str, Any]],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        tus_base_url: str = None,
        raw_input_file_ids: List[int] = None,
    ) -> List[Dict[str, Any]]:
        uploader = self.create_uploader(base_url=tus_base_url)
        
        upload_results = uploader.upload_files(files, progress_callback)
        
        linked_results = []
        for i, result in enumerate(upload_results):
            if result['success']:
                if raw_input_file_ids and i < len(raw_input_file_ids):
                    # Link the uploaded file to the raw input file via PATCH
                    try:
                        raw_input_file_id = raw_input_file_ids[i]
                        patch_data = {
                            'tus_file': result['tus_url'],
                            'original_name': os.path.basename(result['file_path'])
                        }
                        
                        response = self.client.patch(f'/api/raw_input_file/{raw_input_file_id}/', data=patch_data)
                        raw_input_file = response.json()
                        
                        linked_results.append({
                            **result,
                            'raw_input_file_id': raw_input_file_id,
                            'linked': True
                        })
                    except Exception as e:
                        error_message = str(e)
                        if hasattr(e, 'response') and e.response is not None:
                            try:
                                error_data = e.response.json()
                                if 'error' in error_data:
                                    error_message = error_data['error']
                            except (ValueError, KeyError):
                                pass
                        
                        linked_results.append({
                            **result,
                            'raw_input_file_id': raw_input_file_ids[i] if i < len(raw_input_file_ids) else None,
                            'linked': False,
                            'link_error': error_message
                        })
                else:
                    linked_results.append({
                        **result,
                        'raw_input_file_id': None,
                        'linked': False,
                        'link_error': 'No raw input file ID provided for linking'
                    })
            else:
                linked_results.append({
                    **result,
                    'raw_input_file_id': None,
                    'linked': False
                })
        
        return linked_results
