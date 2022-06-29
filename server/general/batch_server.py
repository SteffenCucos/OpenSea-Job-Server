from typing import Optional
import atexit
import sys

import uvicorn
from fastapi import FastAPI
app = FastAPI()

from multiprocessing.pool import ThreadPool as Pool

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import json

retry_strategy = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

@app.get("/status")
def status():
    return {"running": True}

'''
parallelism = 1
with Pool(parallelism) as pool:
    def function(id):
        url = ipfs_url.format(id)
        return get_token(url)

    tokens = pool.map(function, [id for id in range(start, stop + 1)])
    return tokens
'''
@app.get("/ipfs/batch")
def batchIPFSRead(ipfs_url: str, start: int, stop: int):
    print(start, stop, port[0])
    
    tokens = []
    for id in range(start, stop+1):
        get_token(ipfs_url, id)
        print(id)
        tokens.append(get_token(ipfs_url))
    print(tokens)
    return tokens
    

def get_token(ipfs_url, id):
    url = ipfs_url.format(id)
    try:
        response = http.get(url)
        success = True
        traits = json.loads(response.text)["attributes"]
    except:
        success = False
        traits = None
    return {
        "success" : success,
        "id" : id,
        "url" : url,
        "traits" : traits
    }

port = [0]
if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(sys.argv)
        port[0] = sys.argv[1]
        uvicorn.run(app, port=int(sys.argv[1]), host=sys.argv[2])
    else:
        uvicorn.run(app, port=int(8000), host='localhost')