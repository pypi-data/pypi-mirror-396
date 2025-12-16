import json
from typing import Optional, Dict, Any, TYPE_CHECKING
from .asset_utils import create_json_request

if TYPE_CHECKING:
    from .sdk import NanoSDK

async def allocate_resource(
    server_uid: str,
    resource_id: str,
    type: str,
    name: str,
    vram_usage: int = 0,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict:
    """
    Notify NanoCore that a resource has been allocated.
    """
    payload = {
        "serverUid": server_uid,
        "action": "ALLOCATE",
        "data": {
            "resourceId": resource_id,
            "type": type,
            "name": name,
            "vramUsage": vram_usage,
            "metadata": metadata or {}
        }
    }
    return await create_json_request('/resources', method='POST', data=json.dumps(payload), headers={'Content-Type': 'application/json'})

async def free_resource(
    server_uid: str,
    resource_id: str
) -> Dict:
    """
    Notify NanoCore that a resource has been freed.
    """
    payload = {
        "serverUid": server_uid,
        "action": "FREE",
        "data": {
            "resourceId": resource_id
        }
    }
    return await create_json_request('/resources', method='POST', data=json.dumps(payload), headers={'Content-Type': 'application/json'})

