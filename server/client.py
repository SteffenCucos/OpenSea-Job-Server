import os
clear = lambda: os.system('cls')
import time
import json
from general.http import get_retry_http
http = get_retry_http()
base_url = "http://localhost:8000/api/"

def download_collection(name: str):
    response = http.post(base_url + "collections/" + name + "/download") 
    return response.text.strip('"')

def get_job(job_id):
    response = http.get(base_url + "jobs/" + job_id)
    return json.loads(response.text) 

def print_collection(collection):
    if collection["status"] == "LOADING" or collection["status"] == "FINISHED":
        print(collection["collectionName"], "->", str(collection["loaded"]) + "/" + str(collection["total"]), "=", collection["progress"])
    elif collection["status"] == "ERROR":
        error = collection["error"]
        lastLine = error.split("\n")[-2]
        print(collection["collectionName"], "->", lastLine)

if __name__ == "__main__":
    collections = [
        "bored-ape-kennel-club",
        "boredapeyachtclub",
        "godhatesnftees",
        "jpeg-cards",
        "justcubesnft",
        "otherdeed",
        "lostpoets",
        "fantasizenfts",
        "blvckgenesis",
        "projectgodjiragenesis",
        "cryptocitizensofficial",
        "project-godjira-gen-2",
        "murakami-flowers-2022-official"
    ]
    results = {}
    job_ids = {}
    for collection in collections:
        id = download_collection(collection)
        time.sleep(0.1)
        job_ids[collection] = id
        results[id] = get_job(id)
        time.sleep(0.1)

    while True:
        for collection in collections:
            id = job_ids[collection]
            result = results[id]
            print_collection(result)

        for collection in collections:
            id = job_ids[collection]
            result = results[id]
            if result["status"] in ["FINISHED", "ERROR"]:
                continue
            results[id] = get_job(id)

        time.sleep(2)
        clear()

    
    

