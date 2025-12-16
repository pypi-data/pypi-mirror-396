from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from ..exceptions import AbromicsAPIError


@dataclass
class Project:
    id: int
    name: str
    description: Optional[str] = None
    template: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            template=data.get('template'),
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data.get('updated_at') else None
        )


class ProjectManager:
    
    def __init__(self, client):
        self.client = client
    
    def create(
        self,
        name: str,
        template: int,
        description: Optional[str] = None
    ) -> Project:
        data = {
            'name': name,
            'template': template,
            'description': description or "Project generated via abromics library"
        }
        
        response = self.client.post('/api/project/', data=data)
        return Project.from_dict(response.json())
    
    def get(self, project_id: int) -> Project:
        response = self.client.get(f'/api/project/{project_id}/')
        return Project.from_dict(response.json())
    
    def list(
        self,
        name: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Project]:
        params = {}
        if name:
            params['name'] = name
        if search:
            params['search'] = search
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        
        response = self.client.get('/api/project/', params=params)
        data = response.json()
        
        if 'results' in data:
            projects = data['results']
        else:
            projects = data if isinstance(data, list) else [data]
        
        return [Project.from_dict(project) for project in projects]
    
    def update(
        self,
        project_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Project:
        data = {}
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        
        response = self.client.patch(f'/api/project/{project_id}/', data=data)
        return Project.from_dict(response.json())
    
    def delete(self, project_id: int) -> bool:
        self.client.delete(f'/api/project/{project_id}/')
        return True
