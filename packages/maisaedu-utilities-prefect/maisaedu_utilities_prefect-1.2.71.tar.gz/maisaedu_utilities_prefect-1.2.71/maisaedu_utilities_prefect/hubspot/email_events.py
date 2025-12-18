import requests
import json
import urllib
import time
from retry import retry

def get_events(
    api_key,
    app_private_token,
    start_timestamp=None,
    end_timestamp=None,
    offset=None,
    limit=1000,
):
    url = "https://api.hubapi.com/email/public/v1/events?"
    if api_key is not None:
        parameter_dict = {"hapikey": api_key, "limit": limit}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
    else:
        parameter_dict = {"limit": limit}
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }

    if offset is not None:
        parameter_dict["offset"] = offset

    if start_timestamp is not None:
        parameter_dict["startTimestamp"] = start_timestamp

    if end_timestamp is not None:
        parameter_dict["endTimestamp"] = end_timestamp

    parameters = urllib.parse.urlencode(parameter_dict)

    url = url + parameters

    r = requests.get(url=url, headers=headers, timeout=35)
    response_dict = json.loads(r.text)
    return response_dict


@retry(tries=5, delay=30)
def get_data(api_key, app_private_token, start_timestamp, end_timestamp, offset, limit):
    resp = get_events(
            api_key, app_private_token, start_timestamp, end_timestamp, offset, limit
        )

    return resp["events"], resp['hasMore'], resp['offset']


def get_all_email_events(
    api_key, app_private_token, start_timestamp=None, end_timestamp=None, limit=1000
):
    offset = None
    has_more = True
    attempts = 0
    while has_more:
            events, has_more, offset = get_data(api_key, app_private_token, start_timestamp, end_timestamp, offset, limit)

            yield events
            if has_more:
                offset = offset