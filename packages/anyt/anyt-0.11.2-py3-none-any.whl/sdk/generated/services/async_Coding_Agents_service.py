from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

async def listCodingAgents(api_config_override : Optional[APIConfig] = None) -> List[CodingAgentCatalogEntry]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/coding-agents'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            'get',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'listCodingAgents failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return [CodingAgentCatalogEntry(**item) for item in body]