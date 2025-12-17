import os

import requests

from cc_py_commons.utils import json_logger

MERCURY_URL = os.environ.get("MERCURY_URL")
MERCURY_TOKEN = os.environ.get("MERCURY_TOKEN")


def execute(mc=None, dot=None):
    if not MERCURY_URL or not MERCURY_TOKEN:
        json_logger.error(None, 'MERCURY_URL or MERCURY_TOKEN environment variables not set')
        return None
    if not mc and not dot:
        return None
    params = {}
    if mc:
        params['mc'] = mc
    if dot:
        params['dot'] = dot
    url = f"{MERCURY_URL}/fmcsa/carrier"
    token = f"Bearer {MERCURY_TOKEN}"
    headers = {
        "Authorization": token
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=(5, 30))
    except requests.RequestException as e:
        json_logger.error(None, 'Request to FMCSA failed', mc=mc, dot=dot, error=str(e))
        return None

    if response.status_code != 200:
        json_logger.error(None, 'Could not search from FMCSA', mc=mc, dot=dot,
                          response_status_code=response.status_code, response_text=response.text)
        return None
    try:
        return response.json()
    except ValueError as e:
        json_logger.error(None, 'Invalid JSON response from FMCSA', mc=mc, dot=dot, error=str(e))
        return None
