import os

import requests

from cc_py_commons.bids.bid_schema import BidSchema
from cc_py_commons.utils import json_logger
from cc_py_commons.utils.bid_utils import parse_dates_in_bid

BOOKING_AGENT_URL = os.environ.get('BOOKING_AGENT_URL')
BOOKING_AGENT_TOKEN = os.environ.get("BOOKING_AGENT_TOKEN")


def execute(account_id, filters_dict):
    url = f"{BOOKING_AGENT_URL}/bid/match"
    token = f"Bearer {BOOKING_AGENT_TOKEN}"
    headers = {
        "Authorization": token
    }
    json_logger.debug(account_id, f"Requesting bids from booking-agent", url=url, filters=filters_dict)
    response = requests.get(url, headers=headers, params=filters_dict)
    bids = []
    if response.status_code == 200:
        bids = response.json()['content']
        for bid in bids:
            parse_dates_in_bid(bid)
    return BidSchema().load(bids, many=True)
