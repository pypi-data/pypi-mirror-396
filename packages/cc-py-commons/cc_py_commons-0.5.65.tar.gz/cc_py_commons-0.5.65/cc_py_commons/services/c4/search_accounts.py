import traceback

import requests

from cc_py_commons.utils import json_logger
from .constants import C4_API_AUTH_TOKEN, C4_API_URL


def execute(search_request_dict):
    empty_response = { 'data': [], 'nextPage': False}
    if not search_request_dict:
        return empty_response
    url = f"{C4_API_URL}/accounts/search"
    token = f"Bearer {C4_API_AUTH_TOKEN}"
    headers = {
        "Authorization": token
    }
    json_logger.debug(None, 'Searching accounts', url=url, search_request=search_request_dict)
    try:
        response = requests.post(url, json=search_request_dict, headers=headers, timeout=10)
        if response.status_code != 200:
            json_logger.warning(None, 'Request to search accounts failed',
                                response_status_code=response.status_code, response_text=response.text,
                                search_request_dict=search_request_dict)
            return empty_response
        return response.json()
    except requests.exceptions.RequestException as e:
        json_logger.warning(None, 'Request to search accounts failed', error=str(e),
                            search_request_dict=search_request_dict, stacktrace=traceback.format_exc())
        return empty_response
    except ValueError as e:  # JSONDecodeError is a subclass of ValueError
        json_logger.warning(None, 'Failed to parse response JSON', error=str(e),
                            search_request_dict=search_request_dict, stacktrace=traceback.format_exc())
        return empty_response
