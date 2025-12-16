from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

def getMyGitHubInstallation(api_config_override : Optional[APIConfig] = None, *, X_API_Key : Optional[Union[str,None]] = None) -> Union[GitHubInstallation,None]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/github/installations'
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
        raise HTTPException(response.status_code, f'getMyGitHubInstallation failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return Union[GitHubInstallation,None](**body) if body is not None else Union[GitHubInstallation,None]()
def createGitHubInstallation(api_config_override : Optional[APIConfig] = None, *, data : CreateInstallationRequest, X_API_Key : Optional[Union[str,None]] = None) -> GitHubInstallation:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/github/installations'
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
            'post',
        httpx.URL(path),
        headers=headers,
        params=query_params,
                        json = data.model_dump(exclude_none=True)
                    )

    if response.status_code != 201:
        raise HTTPException(response.status_code, f'createGitHubInstallation failed with status code: {response.status_code}')
    else:
                body = None if 201 == 204 else response.json()

    return GitHubInstallation(**body) if body is not None else GitHubInstallation()
def deleteGitHubInstallation(api_config_override : Optional[APIConfig] = None, *, installation_db_id : int, X_API_Key : Optional[Union[str,None]] = None) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/github/installations/{installation_db_id}'
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
            'delete',
        httpx.URL(path),
        headers=headers,
        params=query_params,
            )

    if response.status_code != 204:
        raise HTTPException(response.status_code, f'deleteGitHubInstallation failed with status code: {response.status_code}')
    else:
                body = None if 204 == 204 else response.json()

    return None

def listInstallationRepos(api_config_override : Optional[APIConfig] = None, *, page : Optional[int] = None, per_page : Optional[int] = None, X_API_Key : Optional[Union[str,None]] = None) -> InstallationReposResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/github/installations/repos'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
            'page' : page,
'per_page' : per_page
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
        raise HTTPException(response.status_code, f'listInstallationRepos failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return InstallationReposResponse(**body) if body is not None else InstallationReposResponse()
def createGitHubRepository(api_config_override : Optional[APIConfig] = None, *, data : CreateRepositoryRequest, X_API_Key : Optional[Union[str,None]] = None) -> ExternalRepo:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/github/repositories'
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
            'post',
        httpx.URL(path),
        headers=headers,
        params=query_params,
                        json = data.model_dump(exclude_none=True)
                    )

    if response.status_code != 201:
        raise HTTPException(response.status_code, f'createGitHubRepository failed with status code: {response.status_code}')
    else:
                body = None if 201 == 204 else response.json()

    return ExternalRepo(**body) if body is not None else ExternalRepo()