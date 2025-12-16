"""
Main ABRomics client for API interactions.
"""

import requests
from typing import Optional, Dict, Any, List
from .auth.api_key import ApiKeyAuth
from .models.project import Project, ProjectManager
from .models.sample import Sample, SampleManager
from .models.experiment import Experiment, ExperimentManager
from .models.template import Template, TemplateManager
from .upload.tus_client import TusUploader, UploadManager
from .batch.processor import BatchProcessor
from .exceptions import AbromicsAPIError


class AbromicsClient:
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "https://analysis.abromics.fr",
        timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        self.auth = ApiKeyAuth(api_key)
        
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        self.projects = ProjectManager(self)
        self.samples = SampleManager(self)
        self.experiments = ExperimentManager(self)
        self.templates = TemplateManager(self)
        self.upload = UploadManager(self)
        
        self.batch = BatchProcessor(self)
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            message = f"API request failed: {str(e)}"
            resp = getattr(e, 'response', None)
            if resp is not None:
                try:
                    payload = resp.json()
                    api_error = payload.get('error') if isinstance(payload, dict) else None
                    if api_error:
                        message = f"API returned {resp.status_code}: {api_error}"
                    else:
                        message = f"API returned {resp.status_code}: {payload}"
                except Exception:
                    try:
                        message = f"API returned {resp.status_code}: {resp.text}"
                    except Exception:
                        pass

            err = AbromicsAPIError(message)
            setattr(err, 'response', resp)
            raise err from e
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self._request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self._request('POST', endpoint, data=data)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self._request('PUT', endpoint, data=data)
    
    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self._request('PATCH', endpoint, data=data)
    
    def delete(self, endpoint: str) -> requests.Response:
        return self._request('DELETE', endpoint)
