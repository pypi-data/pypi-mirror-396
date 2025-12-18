
from retry import retry
import requests
import json
import urllib

@retry(tries=5, delay=2, backoff=2)
def get_marketing_emails(api_key, app_private_token, after=None):
    url = "https://api.hubapi.com/marketing/v3/emails?"
    if api_key is not None:
        parameter_dict = {"hapikey": api_key, "limit": 100}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
    else:
        parameter_dict = {"limit": 100}
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }

    if after is not None:
        parameter_dict["after"] = after

    parameter_dict["includeStats"] = "true"

    parameters = urllib.parse.urlencode(parameter_dict)

    url = url + parameters
    
    r = requests.get(url=url, headers=headers)
    r.raise_for_status()
    response_dict = json.loads(r.text)
    return response_dict


def get_all_marketing_emails(api_key, app_private_token):
    has_more = True
    after = None
    while has_more:
        resp = get_marketing_emails(api_key, app_private_token, after)
        
        if "paging" in resp and "next" in resp["paging"]:
            after = resp["paging"]["next"]["after"]
            has_more = True
        else:
            has_more = False
        
        yield resp["results"]