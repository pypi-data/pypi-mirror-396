import requests
from typing import Optional


class ApiKeyAuth(requests.auth.AuthBase): 
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        if not api_key.startswith('abk_'):
            raise ValueError("API key must start with 'abk_'")
        
        self.api_key = api_key
    
    def __call__(self, request: requests.Request) -> requests.Request:
        request.headers['Authorization'] = f'Api-Key {self.api_key}'
        return request




