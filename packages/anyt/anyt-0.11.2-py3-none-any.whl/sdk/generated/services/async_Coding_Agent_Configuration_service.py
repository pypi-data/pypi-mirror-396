from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

async def listWorkspaceCodingAgentConfigs(api_config_override : Optional[APIConfig] = None, *, workspace_id : int, X_API_Key : Optional[Union[str,None]] = None) -> List[CodingAgentConfig]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/coding-agent-configs'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key
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
        raise HTTPException(response.status_code, f'listWorkspaceCodingAgentConfigs failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return [CodingAgentConfig(**item) for item in body]
async def getWorkspaceCodingAgentConfig(api_config_override : Optional[APIConfig] = None, *, workspace_id : int, agent_type : CodingAgentType, X_API_Key : Optional[Union[str,None]] = None) -> CodingAgentConfig:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/coding-agent-configs/{agent_type}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key
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
        raise HTTPException(response.status_code, f'getWorkspaceCodingAgentConfig failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return CodingAgentConfig(**body) if body is not None else CodingAgentConfig()
async def upsertWorkspaceCodingAgentConfig(api_config_override : Optional[APIConfig] = None, *, workspace_id : int, agent_type : CodingAgentType, data : CodingAgentConfigUpdate, X_API_Key : Optional[Union[str,None]] = None) -> CodingAgentConfig:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/coding-agent-configs/{agent_type}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            'put',
        httpx.URL(path),
        headers=headers,
        params=query_params,
                        json = data.model_dump(exclude_none=True)
                    )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'upsertWorkspaceCodingAgentConfig failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return CodingAgentConfig(**body) if body is not None else CodingAgentConfig()
async def deleteWorkspaceCodingAgentConfig(api_config_override : Optional[APIConfig] = None, *, workspace_id : int, agent_type : CodingAgentType, X_API_Key : Optional[Union[str,None]] = None) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/coding-agent-configs/{agent_type}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            'delete',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 204:
        raise HTTPException(response.status_code, f'deleteWorkspaceCodingAgentConfig failed with status code: {response.status_code}')
    else:
                body = None if 204 == 204 else response.json()

    return None
