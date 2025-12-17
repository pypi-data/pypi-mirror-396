from dateutil.parser import parse


def parse_dates_in_bid(bid):
    if bid:
        bid['pickupDate'] = parse(bid['pickupDate']).strftime('%Y-%m-%d')
        bid['deliveryDate'] = parse(bid['deliveryDate']).strftime('%Y-%m-%d')
        if bid.get('inviteEmailedAt'):
            bid['inviteEmailedAt'] = parse(bid['inviteEmailedAt']).isoformat()
        for bid_history in bid.get('bidHistories', []):
            bid_history['pickupDate'] = parse(bid_history['pickupDate']).strftime('%Y-%m-%d')
            bid_history['deliveryDate'] = parse(bid_history['deliveryDate']).strftime('%Y-%m-%d')
