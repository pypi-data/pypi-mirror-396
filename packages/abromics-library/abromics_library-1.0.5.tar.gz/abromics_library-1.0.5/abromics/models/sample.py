import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from ..exceptions import AbromicsAPIError


@dataclass
class Sample:
    id: int  
    project_id: int
    metadata: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    sample_id: Optional[int] = None  
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Sample':
        return cls(
            id=data['id'],
            project_id=data['project'],
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data.get('updated_at') else None,
            sample_id=data.get('sample_id')
        )


class SampleManager:
    def __init__(self, client):
        self.client = client
    
    # --- mirror frontend XLSX validation logic ---
    def _validate_country(self, country_name: str) -> Optional[Dict[str, Any]]:
        if not country_name or not isinstance(country_name, str):
            return None
        try:
            response = self.client.get('/api/geocoding/search_country/', params={'name': country_name})
            data = response.json()
            if isinstance(data, list):
                return data[0] if data else None
            if isinstance(data, dict):
                results = data.get('results')
                if isinstance(results, list) and results:
                    return results[0]
            return None
        except Exception:
            return None

    def _validate_region(self, region_name: str, country_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        if not region_name or not isinstance(region_name, str):
            return None
        try:
            params: Dict[str, Any] = {'search': region_name}
            if country_id:
                params['country__id'] = country_id
            response = self.client.get('/api/geocoding/search_countrylevel1/', params=params)
            data = response.json()
            if isinstance(data, list):
                return data[0] if data else None
            if isinstance(data, dict):
                results = data.get('results')
                if isinstance(results, list) and results:
                    return results[0]
            return None
        except Exception:
            return None

    def _validate_place(self, place_name: str, country_id: Optional[int] = None, region_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        if not place_name or not isinstance(place_name, str):
            return None
        try:
            params: Dict[str, Any] = {'search': place_name}
            if country_id:
                params['country__id'] = country_id
            if region_id:
                params['country_level1__id'] = region_id
            response = self.client.get('/api/geocoding/search_place/', params=params)
            data = response.json()
            if isinstance(data, list):
                return data[0] if data else None
            if isinstance(data, dict):
                results = data.get('results')
                if isinstance(results, list) and results:
                    return results[0]
            return None
        except Exception:
            return None

    def _transform_location_fields(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        transformed = dict(metadata)
        geocode_errors: List[str] = []

        country_obj: Optional[Dict[str, Any]] = None
        if isinstance(transformed.get('country_id'), str):
            original_country = transformed['country_id']
            country_obj = self._validate_country(original_country)
            if country_obj and 'id' in country_obj:
                transformed['country_id'] = int(country_obj['id'])
            else:
                geocode_errors.append(f"Unknown country '{original_country}'")

        region_obj: Optional[Dict[str, Any]] = None
        if isinstance(transformed.get('country_level1_id'), str):
            original_region = transformed['country_level1_id']
            resolved_country_id_for_region = None
            if isinstance(transformed.get('country_id'), int):
                resolved_country_id_for_region = transformed['country_id']
            region_obj = self._validate_region(original_region, resolved_country_id_for_region)
            if region_obj and 'id' in region_obj:
                transformed['country_level1_id'] = int(region_obj['id'])
            else:
                if isinstance(transformed.get('country_id'), int):
                    geocode_errors.append(
                        f"Region '{original_region}' not found for the selected country"
                    )
                else:
                    geocode_errors.append(f"Unknown region '{original_region}'")

        if isinstance(transformed.get('place_id'), str):
            original_place = transformed['place_id']
            resolved_country_id = None
            resolved_region_id = None
            if isinstance(transformed.get('country_id'), int):
                resolved_country_id = transformed['country_id']
            if isinstance(transformed.get('country_level1_id'), int):
                resolved_region_id = transformed['country_level1_id']

            place_obj = self._validate_place(original_place, resolved_country_id, resolved_region_id)
            if place_obj and 'id' in place_obj:
                transformed['place_id'] = int(place_obj['id'])
            else:
                context_bits: List[str] = []
                if isinstance(transformed.get('country_id'), int):
                    context_bits.append("country")
                if isinstance(transformed.get('country_level1_id'), int):
                    context_bits.append("region")
                if context_bits:
                    geocode_errors.append(
                        f"Place '{original_place}' not found for the selected {' and '.join(context_bits)}"
                    )
                else:
                    geocode_errors.append(f"Unknown place '{original_place}'")

        if isinstance(transformed.get('travel_countries'), str):
            raw = transformed['travel_countries']
            parts = [p.strip() for p in raw.replace(';', ',').split(',') if p.strip()]
            resolved_ids: List[int] = []
            for name in parts:
                c = self._validate_country(name)
                if c and 'id' in c:
                    try:
                        resolved_ids.append(int(c['id']))
                    except Exception:
                        continue
            if resolved_ids:
                transformed['travel_countries'] = ','.join(str(i) for i in resolved_ids)

        # If we could not resolve some of the textual location fields, fail early with a clear message
        if geocode_errors:
            raise AbromicsAPIError(
                "; ".join(
                    [
                        "Invalid location association: " + ", ".join(geocode_errors)
                    ]
                )
            )

        return transformed

    def create(
        self,
        project_id: int,
        metadata: Dict[str, Any]
    ) -> Sample:
        project_response = self.client.get(f'/api/project/{project_id}/')
        project_data = project_response.json()
        template_id = project_data['template']['id'] if isinstance(project_data['template'], dict) else project_data['template']
        
        
        metadata_templates_response = self.client.get(f'/api/metadata_template/?template={template_id}')
        metadata_templates = metadata_templates_response.json()
        
        
        field_mapping = {}
        for template in metadata_templates:
            field_name = template['field_name']
            template_id = template['id']
            field_number = template['field_number']
            field_public_name = template['field_public_name']
            
            if field_name == 'original_name':
                if field_number == 3: 
                    if 'fasta' in field_public_name.lower():
                        field_mapping['fasta_filename'] = template_id
                    else:
                        field_mapping['r1_fastq_filename'] = template_id
                elif field_number == 4:  
                    field_mapping['r2_fastq_filename'] = template_id
                else:
                    field_mapping[field_name] = template_id
            else:
                field_mapping[field_name] = template_id
            
        
        
        metadata = self._transform_location_fields(metadata)

        data_array = []
        for field_name, value in metadata.items():
            if field_name in field_mapping and value is not None:
                data_array.append({
                    "metadata_template": field_mapping[field_name],
                    "value": str(value)
                })
        
        data = {
            'project': str(project_id),  
            'data': [data_array]
        }
        
        try:
            response = self.client.session.post(
                f"{self.client.base_url}/api/upload_data/",
                json=data,
                timeout=self.client.timeout
            )
            
            if response.status_code not in [200, 201]:
                raise AbromicsAPIError(f"API returned {response.status_code}: {response.text}")
            
            result = response.json()
            
            if 'error' in result:
                raise AbromicsAPIError(f"Sample creation failed: {result['error']}")
            
            if isinstance(result, list) and len(result) > 0:
                sample_data = result[0]
                if 'error' in sample_data and sample_data['error']:
                    raise AbromicsAPIError(f"Sample creation failed: {sample_data['error']}")
                
                experiment_data = sample_data['data']
                experiment_id = experiment_data['experiment_id']
                
                try:
                    exp_response = self.client.get(f'/api/experiment/{experiment_id}/')
                    exp_details = exp_response.json()
                    
                    real_sample_id = None
                    if 'samples' in exp_details and isinstance(exp_details['samples'], list):
                        if len(exp_details['samples']) > 0:
                            real_sample_id = exp_details['samples'][0].get('id')
                except Exception:
                    
                    real_sample_id = None
                
                mock_sample_data = {
                    'id': experiment_id,
                    'project': project_id,
                    'metadata': metadata,
                    'created_at': None,
                    'updated_at': None,
                    'raw_input_file_ids': experiment_data.get('raw_input_files', []),
                    'sample_id': real_sample_id
                }
                
                return Sample.from_dict(mock_sample_data)
            else:
                raise AbromicsAPIError("Unexpected response format from sample creation")
        except requests.exceptions.HTTPError as e:
            raise AbromicsAPIError(f"API returned {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise e
    
    def get(self, sample_id: int) -> Sample:
        response = self.client.get(f'/api/sample/{sample_id}/')
        return Sample.from_dict(response.json())
    
    def list(
        self,
        project_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Sample]:
        params = {}
        if project_id:
            params['project'] = project_id
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        
        response = self.client.get('/api/sample/', params=params)
        data = response.json()
        
        if 'results' in data:
            samples = data['results']
        else:
            samples = data if isinstance(data, list) else [data]
        
        return [Sample.from_dict(sample) for sample in samples]
    
    def update(
        self,
        sample_id: int,
        metadata: Dict[str, Any]
    ) -> Sample:
        data = {
            'data': [metadata]
        }
        
        response = self.client.patch(f'/api/upload_data/{sample_id}/', data=data)
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            sample_data = result[0]
            if 'error' in sample_data and sample_data['error']:
                raise AbromicsAPIError(f"Sample update failed: {sample_data['error']}")
            
            return Sample.from_dict(sample_data['data'])
        else:
            raise AbromicsAPIError("Unexpected response format from sample update")
    
    def delete(self, sample_id: int) -> bool:
        self.client.delete(f'/api/sample/{sample_id}/')
        return True
