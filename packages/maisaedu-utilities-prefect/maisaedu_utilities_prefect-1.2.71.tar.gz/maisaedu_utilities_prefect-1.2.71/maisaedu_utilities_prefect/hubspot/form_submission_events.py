import requests
import json
import urllib
from time import sleep
from retry import retry


def get_hubspot_form_submission_events(
        hapikey, app_private_token, occurred_after, occurred_before, after, limit
):
    url = "https://api.hubapi.com/events/v3/events?"

    parameter_dict = {
        "eventType": "e_form_submission_v2",
        "occurredAfter": occurred_after,
        "limit": limit
    }

    if occurred_before:
        parameter_dict["occurredBefore"] = occurred_before

    if after:
        parameter_dict["after"] = after

    if hapikey is not None:
        parameter_dict = {"hapikey": hapikey}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
    else:
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }

    parameters = urllib.parse.urlencode(parameter_dict)

    url += parameters
    try:
        response = requests.get(url=url, headers=headers)
        response_dict = json.loads(response.text)
        return response_dict
    except Exception as e:
        print(e)


@retry(tries=5, delay=30)
def get_data(hapikey, app_private_token, occurred_after, occurred_before, after, limit):
    resp = get_hubspot_form_submission_events(
            hapikey, app_private_token, occurred_after, occurred_before, after, limit
        )

    if "paging" in resp:
        if "next" in resp["paging"]:
          if "after" in resp["paging"]["next"]:
            after = resp["paging"]["next"]["after"]
          else:
            after = None
        else:
            after = None
    else:
        after = None

    if after is None:
        has_more = False
    else:
        has_more = True

    return resp["results"], has_more, after


def get_form_submission_events(
    hapikey, app_private_token, occurred_after, occurred_before=None, limit=100
):
    after = None
    has_more = True
    while has_more:
            results, has_more, after = get_data(hapikey, app_private_token, occurred_after, occurred_before, after, limit)

            yield results
            if has_more:
                after = after
