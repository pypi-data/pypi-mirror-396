from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

def auth_check_v1_auth_get(api_config_override : Optional[APIConfig] = None, *, X_API_Key : Optional[Union[str,None]] = None) -> AuthResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/auth'
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

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            'get',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'auth_check_v1_auth_get failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return AuthResponse(**body) if body is not None else AuthResponse()