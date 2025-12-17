import requests

from cc_py_commons.bids.bid_schema import BidSchema
from cc_py_commons.utils import json_logger
from cc_py_commons.utils.bid_utils import parse_dates_in_bid
from .constants import BOOKING_AGENT_URL, BOOKING_AGENT_TOKEN


def execute(account_id, bid_id):
    url = f"{BOOKING_AGENT_URL}/quote/-/bid/{bid_id}"
    token = f"Bearer {BOOKING_AGENT_TOKEN}"
    headers = {
        "Authorization": token
    }
    json_logger.debug(account_id, f'Requesting bid from booking-agent', url=url)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        bid_dict = response.json()
        parse_dates_in_bid(bid_dict)
        return BidSchema().load(bid_dict)
    else:
        json_logger.warning(account_id, 'Could not find bid from booking-agent',
                            response_status_code=response.status_code, response_text=response.text)
    return None
