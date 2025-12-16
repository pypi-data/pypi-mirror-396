from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from ..exceptions import AbromicsAPIError


@dataclass
class Experiment:
    id: int
    project_id: int
    sample_id: int
    name: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Experiment':
        return cls(
            id=data['id'],
            project_id=data['project'],
            sample_id=data['sample'],
            name=data.get('name'),
            status=data.get('status'),
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data.get('updated_at') else None
        )


class ExperimentManager:
    def __init__(self, client):
        self.client = client
    
    def get(self, experiment_id: int) -> Experiment:
        response = self.client.get(f'/api/experiment/{experiment_id}/')
        return Experiment.from_dict(response.json())
    
    def list(
        self,
        project_id: Optional[int] = None,
        sample_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Experiment]:
        params = {}
        if project_id:
            params['project'] = project_id
        if sample_id:
            params['sample'] = sample_id
        if status:
            params['status'] = status
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        
        response = self.client.get('/api/experiment/', params=params)
        data = response.json()
        
        # Handle paginated response
        if 'results' in data:
            experiments = data['results']
        else:
            experiments = data if isinstance(data, list) else [data]
        
        return [Experiment.from_dict(experiment) for experiment in experiments]
    
    def delete(self, experiment_id: int) -> bool:
        self.client.delete(f'/api/experiment/{experiment_id}/')
        return True
