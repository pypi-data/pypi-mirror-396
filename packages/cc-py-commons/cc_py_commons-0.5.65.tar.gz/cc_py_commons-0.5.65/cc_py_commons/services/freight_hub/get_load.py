import os

import requests

from cc_py_commons.loads.map_load_response import execute as map_load_response
from cc_py_commons.utils import json_logger

FREIGHT_HUB_URL = os.environ.get('FREIGHT_HUB_URL')
FREIGHT_HUB_TOKEN = os.environ.get("FREIGHT_HUB_TOKEN")


def execute(load_id, account_id=None):
    if not load_id:
        json_logger.error(account_id, 'Invalid load_id provided', load_id=load_id)
        return None
    
    url = f"{FREIGHT_HUB_URL}/freight/{load_id}"
    token = f"Bearer {FREIGHT_HUB_TOKEN}"
    headers = {
        "Authorization": token
    }
    load = None
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            json = response.json()
            load = map_load_response(json)
        else:
            json_logger.warning(account_id, 'Failed to get load from FreightHub',
                                response_status_code=response.status_code, response_text=response.text)

    except Exception as e:
        json_logger.error(account_id, 'Error calling FreightHub API', error=str(e))

    return load
