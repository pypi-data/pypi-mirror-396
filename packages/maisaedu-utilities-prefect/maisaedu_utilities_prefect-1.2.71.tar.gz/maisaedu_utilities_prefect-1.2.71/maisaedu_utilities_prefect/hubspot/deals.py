from datetime import datetime
import pytz
import prefect
import requests
import json
import urllib
from time import sleep


def get_deals_v1(hapikey, app_private_token, properties, offset, extraparams, tries=5):
    url = "https://api.hubapi.com/deals/v1/deal/paged?"
    if hapikey is not None:
        parameter_dict = {
            "hapikey": hapikey,
            "count": "250",
            "includeAssociations": "true",
        }
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
    else:
        parameter_dict = {"count": "250", "includeAssociations": "true"}
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }
    if offset > 0:
        parameter_dict["offset"] = offset

    parameters = urllib.parse.urlencode(parameter_dict)

    for i in properties:
        parameters = parameters + "&properties=" + i
    if extraparams != "":
        parameters = parameters + "&" + extraparams

    get_url = url + parameters
    for i in range(tries):
        try:
            r = requests.get(url=get_url, headers=headers)
            response_dict = json.loads(r.text)
            return response_dict
        except Exception as e:
            prefect.get_run_logger().error(e)


def get_deals_v1_recent_modified(
    hapikey, app_private_token, properties, offset, extraparams, since, tries=5
):
    url = "https://api.hubapi.com/deals/v1/deal/recent/modified?"
    if hapikey is not None:
        parameter_dict = {
            "hapikey": hapikey,
            "count": "250",
            "includeAssociations": "true",
        }
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
    else:
        parameter_dict = {"count": "250", "includeAssociations": "true"}
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }

    if offset > 0:
        parameter_dict["offset"] = offset

    parameters = urllib.parse.urlencode(parameter_dict)

    for i in properties:
        parameters = parameters + "&properties=" + i
    if extraparams != "":
        parameters = parameters + "&" + extraparams

    parameters = parameters + "&since=" + since

    parameters = parameters + "&includePropertyVersions=true"

    get_url = url + parameters
    for i in range(tries):
        try:
            r = requests.get(url=get_url, headers=headers)
            response_dict = json.loads(r.text)
            return response_dict
        except Exception as e:
            prefect.get_run_logger().error(e)


def get_all_deals_v1(hapikey, app_private_token, properties, extraparams):
    data = list()
    hasmore = True
    offset = 0
    attempts = 0
    while hasmore:
        resp = get_deals_v1(hapikey, app_private_token, properties, offset, extraparams)
        try:
            yield resp["deals"]
            hasmore = resp["hasMore"]
            offset = resp["offset"]
            attempts = 0
        except KeyError as e:
            attempts += 1
            sleep(10)
            if attempts > 2:
                prefect.get_run_logger().error(resp)
                raise Exception(e)
    return data


def get_all_deals_v1_recent_modified(
    hapikey, app_private_token, properties, extraparams, since
):
    data = list()
    hasmore = True
    offset = 0
    attempts = 0
    while hasmore:
        resp = get_deals_v1_recent_modified(
            hapikey, app_private_token, properties, offset, extraparams, since
        )
        try:
            yield resp["results"]
            if len(resp["results"]) == 0 and offset < 10000:
                hasmore = False
            else:
                lasttimestamp = list(resp["results"])[0]["properties"][
                    "hs_lastmodifieddate"
                ]["timestamp"]
                attempts = 0
                hasmore = resp["hasMore"]
                offset = resp["offset"]
                attempts = 0
        except KeyError as e:
            if offset >= 10000:
                since = str(lasttimestamp)
                offset = 0

            attempts += 1
            sleep(10)
            if attempts > 2:
                prefect.get_run_logger().error(resp)
                raise Exception(e)
    return data

def get_deal_v3_with_history(
    app_private_token,
    deal_id,
    properties_with_history,
    tries=5,
):
    logger = prefect.get_run_logger()
    base_url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}"

    params = {}

    if properties_with_history:
        params["propertiesWithHistory"] = ",".join(properties_with_history)

    headers = {
        "content-type": "application/json",
        "cache-control": "no-cache",
        "Authorization": f"Bearer {app_private_token}",
    }

    for i in range(tries):
        try:
            r = requests.get(url=base_url, headers=headers, params=params)
            r.raise_for_status()
            response_dict = r.json()
            return response_dict
        except Exception as e:
            logger.error(f"Error to fetch deal v3 with history (attempt {i+1}/{tries}): {e}")
            if i == tries - 1:
                raise


def chunk_list(values, chunk_size):
    values = list(values)
    for i in range(0, len(values), chunk_size):
        yield values[i:i + chunk_size]

def get_deals_v3_batch_with_history(
    app_private_token,
    deal_ids,
    properties_with_history=None,
    properties=None,
    batch_size=50,
    tries=5,
):
    """
    Lê deals em lote na API v3 usando:
      POST /crm/v3/objects/deals/batch/read

    - deal_ids: iterável de IDs de deals
    - properties_with_history: lista de propriedades com histórico
    - properties: lista de propriedades atuais
    - batch_size: máximo 50 por causa da API da HubSpot

    Retorna: dict {deal_id: payload_json_completo}
    """
    logger = prefect.get_run_logger()
    url = "https://api.hubapi.com/crm/v3/objects/deals/batch/read"

    # garantia extra: nunca passa de 50
    if batch_size > 50:
        batch_size = 50

    headers = {
        "content-type": "application/json",
        "cache-control": "no-cache",
        "Authorization": f"Bearer {app_private_token}",
    }

    results_by_id = {}

    # garante lista de strings
    deal_ids = [str(d) for d in deal_ids]

    for ids_chunk in chunk_list(deal_ids, batch_size):
        if not ids_chunk:
            continue

        # LOG para você ver o tamanho do chunk
        logger.info(f"Chamando batch/read para {len(ids_chunk)} deals "
                    f"({ids_chunk[0]} .. {ids_chunk[-1]})")

        body = {
            "inputs": [{"id": did} for did in ids_chunk]
        }

        if properties:
            body["properties"] = list(properties)

        if properties_with_history:
            body["propertiesWithHistory"] = list(properties_with_history)

        for attempt in range(tries):
            try:
                r = requests.post(url, headers=headers, json=body, timeout=30)
                r.raise_for_status()
                resp = r.json()

                for deal in resp.get("results", []):
                    deal_id = deal.get("id")
                    if deal_id is not None:
                        results_by_id[deal_id] = deal

                break  # deu certo, sai do retry
            except Exception as e:
                logger.error(
                    f"Erro ao buscar deals v3 em batch "
                    f"(chunk {ids_chunk[0]}..{ids_chunk[-1]}) "
                    f"(tentativa {attempt+1}/{tries}): {e}"
                )
                if attempt == tries - 1:
                    raise

    return results_by_id