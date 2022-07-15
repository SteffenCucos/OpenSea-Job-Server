
import requests
from requests.sessions import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry



def get_retry_http() -> Session:
    retry_strategy = Retry(
        total=25,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    return http