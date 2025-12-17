import requests

from cc_py_commons.utils import json_logger
from .constants import BOOKING_AGENT_TOKEN, BOOKING_AGENT_URL


def execute(quote_id, payload, account_id=None):
    url = f"{BOOKING_AGENT_URL}/quote/{quote_id}"
    token = f"Bearer {BOOKING_AGENT_TOKEN}"
    headers = {
        "Authorization": token
    }
    json_logger.debug(account_id, 'Updating quote in booking-agent', url=url, payload=payload)
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        json_logger.warning(account_id, 'Failed to update quote', response_status_code=response.status_code,
                       response_text=response.text)
    return None
