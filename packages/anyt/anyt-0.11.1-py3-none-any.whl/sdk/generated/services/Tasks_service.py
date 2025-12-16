from typing import *
import httpx


from ..models import *
from ..api_config import APIConfig, HTTPException

def bulkUpdateTasks(api_config_override : Optional[APIConfig] = None, *, workspace_id : int, data : BulkUpdateTasksRequest, X_API_Key : Optional[Union[str,None]] = None) -> BulkUpdateTasksResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/bulk-tasks'
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
            'patch',
        httpx.URL(path),
        headers=headers,
        params=query_params,
                        json = data.model_dump(exclude_none=True)
                    )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'bulkUpdateTasks failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return BulkUpdateTasksResponse(**body) if body is not None else BulkUpdateTasksResponse()
def listTasks(api_config_override : Optional[APIConfig] = None, *, workspace_id : int, project : Optional[Union[int,None]] = None, status : Optional[Union[str,None]] = None, priority : Optional[Union[int,None]] = None, priority_gte : Optional[Union[int,None]] = None, priority_lte : Optional[Union[int,None]] = None, owner : Optional[Union[str,None]] = None, creator : Optional[Union[str,None]] = None, parent : Optional[Union[str,None]] = None, assigned_coding_agent : Optional[Union[str,None]] = None, created_after : Optional[Union[str,None]] = None, updated_after : Optional[Union[str,None]] = None, completed_after : Optional[Union[str,None]] = None, completed_before : Optional[Union[str,None]] = None, limit : Optional[int] = None, offset : Optional[int] = None, sort_by : Optional[str] = None, order : Optional[str] = None, X_API_Key : Optional[Union[str,None]] = None) -> TaskListResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'X-API-Key' : X_API_Key
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
            'project' : project,
'status' : status,
'priority' : priority,
'priority_gte' : priority_gte,
'priority_lte' : priority_lte,
'owner' : owner,
'creator' : creator,
'parent' : parent,
'assigned_coding_agent' : assigned_coding_agent,
'created_after' : created_after,
'updated_after' : updated_after,
'completed_after' : completed_after,
'completed_before' : completed_before,
'limit' : limit,
'offset' : offset,
'sort_by' : sort_by,
'order' : order
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
        raise HTTPException(response.status_code, f'listTasks failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return TaskListResponse(**body) if body is not None else TaskListResponse()
def createTask(api_config_override : Optional[APIConfig] = None, *, workspace_id : int, data : CreateTaskRequest, X_API_Key : Optional[Union[str,None]] = None) -> Task:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks'
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
        raise HTTPException(response.status_code, f'createTask failed with status code: {response.status_code}')
    else:
                body = None if 201 == 204 else response.json()

    return Task(**body) if body is not None else Task()
def getTask(api_config_override : Optional[APIConfig] = None, *, workspace_id : int, task_identifier : str, X_API_Key : Optional[Union[str,None]] = None) -> Task:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks/{task_identifier}'
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
        raise HTTPException(response.status_code, f'getTask failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return Task(**body) if body is not None else Task()
def deleteTask(api_config_override : Optional[APIConfig] = None, *, workspace_id : int, task_identifier : str, X_API_Key : Optional[Union[str,None]] = None) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks/{task_identifier}'
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
        raise HTTPException(response.status_code, f'deleteTask failed with status code: {response.status_code}')
    else:
                body = None if 204 == 204 else response.json()

    return None

def updateTask(api_config_override : Optional[APIConfig] = None, *, workspace_id : int, task_identifier : str, data : TaskUpdate, If_Match : Optional[Union[int,None]] = None, X_API_Key : Optional[Union[str,None]] = None) -> Task:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f'/v1/workspaces/{workspace_id}/tasks/{task_identifier}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer { api_config.get_access_token() }',
        'If-Match' : If_Match,
'X-API-Key' : X_API_Key
    }
    headers = {key:value for (key,value) in headers.items() if value is not None and not (key == 'Authorization' and value == 'Bearer None')}
    query_params : Dict[str,Any] = {
        }

    query_params = {key:value for (key,value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            'patch',
        httpx.URL(path),
        headers=headers,
        params=query_params,
                        json = data.model_dump(exclude_none=True)
                    )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f'updateTask failed with status code: {response.status_code}')
    else:
                body = None if 200 == 204 else response.json()

    return Task(**body) if body is not None else Task()