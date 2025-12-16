from typing import List, Optional, Dict, Any
from ..exceptions import AbromicsAPIError


class Template:    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.name = data.get('name')
        self.description = data.get('description', '')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        self.fields = data.get('fields', [])
        self._data = data
    
    def __repr__(self):
        return f"Template(id={self.id}, name='{self.name}')"


class TemplateManager:
    
    def __init__(self, client):
        self.client = client
    
    def list(self) -> List[Template]:
        try:
            response = self.client.get('/api/templates/')
            templates_data = response.json()
            
            if isinstance(templates_data, dict) and 'results' in templates_data:
                templates_data = templates_data['results']
            
            return [Template(template_data) for template_data in templates_data]
        except Exception as e:
            raise AbromicsAPIError(f"Failed to list templates: {str(e)}") from e
    
    def get(self, template_id: int) -> Template:
        try:
            response = self.client.get(f'/api/templates/{template_id}/')
            return Template(response.json())
        except Exception as e:
            raise AbromicsAPIError(f"Failed to get template {template_id}: {str(e)}") from e
    
    def get_tsv_template(self, template_id: int) -> str:
        try:
            response = self.client.get(f'/api/templates/{template_id}/tsv/')
            return response.text
        except Exception as e:
            raise AbromicsAPIError(f"Failed to get TSV template for template {template_id}: {str(e)}") from e




