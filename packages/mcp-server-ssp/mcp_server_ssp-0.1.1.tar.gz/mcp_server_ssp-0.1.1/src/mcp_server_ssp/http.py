import logging
logger = logging.getLogger(__name__)

import httpx

def request(url: str, params):

    response = httpx.get(url, params=params)

    return response
