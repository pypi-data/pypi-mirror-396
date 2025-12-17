import os

import requests

from cc_py_commons.utils import json_logger

FREIGHT_HUB_URL = os.environ.get('FREIGHT_HUB_URL')
FREIGHT_HUB_TOKEN = os.environ.get("FREIGHT_HUB_TOKEN")


def execute(load_dict, account_id=None):
    load_id = load_dict.get('id')
    url = f"{FREIGHT_HUB_URL}/freight/{load_id}"
    token = f"Bearer {FREIGHT_HUB_TOKEN}"
    headers = {
        "Authorization": token
    }
    try:
        json_logger.debug(account_id, "Updating load on freight-hub", url=url, load_id=load_id)
        response = requests.post(url, json=load_dict, headers=headers, timeout=30)
        if response.status_code not in (200, 201, 204):
            json_logger.warning(account_id, 'FreightHub update returned non-success status',
                                response_status_code=response.status_code,
                                response_text=response.text,
                                load_id=load_id,
                                load_dict=load_dict)
        return response
    except Exception as e:
        json_logger.error(account_id, 'Error calling FreightHub API for update',
            error=str(e), load_id=load_id)
        return None
