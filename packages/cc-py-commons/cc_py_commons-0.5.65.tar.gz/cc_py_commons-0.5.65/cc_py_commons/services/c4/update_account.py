import traceback

import requests

from cc_py_commons.utils import json_logger
from .constants import C4_API_AUTH_TOKEN, C4_API_URL


def execute(account_id, update_request_dict):
    if not update_request_dict:
        return None
    url = f"{C4_API_URL}/accounts"
    token = f"Bearer {C4_API_AUTH_TOKEN}"
    headers = {
        "Authorization": token
    }
    json_logger.debug(account_id, 'Updating account', url=url, update_request=update_request_dict)
    try:
        response = requests.patch(url, json=update_request_dict, headers=headers, timeout=10)
        if response.status_code != 200:
            json_logger.warning(account_id, 'Request to update account failed',
                                response_status_code=response.status_code, response_text=response.text,
                                update_request_dict=update_request_dict)
            return None
        return response.json()
    except requests.exceptions.RequestException as e:
        json_logger.warning(account_id, 'Request to update account failed', error=str(e),
                            update_request_dict=update_request_dict, stacktrace=traceback.format_exc())
        return None
    except ValueError as e:  # JSONDecodeError is a subclass of ValueError
        json_logger.warning(account_id, 'Failed to parse response JSON', error=str(e),
                            update_request_dict=update_request_dict, stacktrace=traceback.format_exc())
        return None
