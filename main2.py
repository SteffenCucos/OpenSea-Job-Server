from pathlib import Path
import os
import signal
import subprocess
from itertools import chain
import time
import numpy
import pprint
pp = pprint.PrettyPrinter(indent=1)

from multiprocessing.pool import ThreadPool as Pool
from threading import Lock

import json

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

retry_strategy = Retry(
    total=100,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"]
)

adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

from server.general.credentials import Credentials
credentials = Credentials.fromFile("credentials.json")

from metadata import Metadata
metadata = Metadata(http=http, credentials=credentials)

load_mode = "internal" # internal external

def compute_rarity(token, traitsDistribution, collectionSize: int):
    rarityReport = {}
    rarenessSum = 0
    flatTrates = {}
    for traitDict in token["traits"]:
        flatTrates[traitDict["trait_type"]] = traitDict["value"]

    for traitType, traitCounts in traitsDistribution.items():
        if traitType in flatTrates.keys():
            tokenTrait = flatTrates[traitType]
            traitCount = traitCounts[tokenTrait]
        else:
            traitCount = traitCounts["None"]
        traitRareness = traitCount / collectionSize
        rarityReport[traitType] = traitRareness
        rarenessSum += traitRareness

    for traitDict in token["traits"]:
        traitDict["rarity"] = rarityReport[traitDict["trait_type"]]
    token["rarity"] = rarenessSum / len(token["traits"])

def compute_distribution(tokens: list, collectionSize: int):
    traitsDistribution = {}
    errorCount = 0
    for token in tokens:
        if not token["success"]:
            # Should this log or error?
            errorCount += 1
            continue
        for trait in token["traits"]:
            traitType = trait["trait_type"]
            value = trait["value"]
            traitValueCounts = traitsDistribution.get(traitType, {})
            traitValueCounts[value] = traitValueCounts.get(value, 0) + 1
            traitsDistribution[traitType] = traitValueCounts

    # For each traitType, compute how many nfts lack the trait
    for traitType, distribution in traitsDistribution.items():
        distributionSize = 0    
        for traitName, count in distribution.items():
            distributionSize += count
        distribution["None"] = collectionSize - distributionSize
    print("Encountered {} errors".format(errorCount))
    return traitsDistribution

def compute_collection_rarities(collectionInfo):
    collectionName = collectionInfo["collectionName"]
    collectionSize = collectionInfo["collectionSize"]
    contractAddress = collectionInfo["contractAddress"]
    contractABI = collectionInfo["contractABI"]
    
    traitsAddress = metadata.get_traits_address(contractAddress, contractABI)

    tokens = []
    collectionTokensFileName = "collections/" + collection + "/" + collectionName + ".tokens"
    if not Path(collectionTokensFileName).is_file():
        # We need to download the token data
        parallelism = 100
        with Pool(parallelism) as pool:
            if load_mode == "internal":
                lock = Lock()
                count = [0] # use an array for count so we can mutate it from multiple threads
                get_traits = metadata.get_traits_curry(collectionSize, traitsAddress, count, lock)
                tokens = pool.map(get_traits, [id for id in range(1, int(collectionSize)+1)])
            else:
                # boot N instances of batch-server.py
                basePort = 5000
                baseHost = "localhost"
                def is_port_in_use(port):
                    import socket
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        return s.connect_ex(('localhost', port)) == 0
                index = 0
                batchServerPorts = []
                print("Start Searching For Ports")
                while len(batchServerPorts) < parallelism:
                    port = basePort + index
                    index += 1
                    if not is_port_in_use(port):
                        batchServerPorts.append(port)
                        print(len(batchServerPorts), "/", parallelism)
                print("End Searching For Ports")
                baseServerAddress = "http://" + baseHost + ":{}/"
                def get_traits_external_curry(baseServerAddress, ports, traitsAddress, indeces, numBlocks):
                    def get_traits_external(block):
                        batchServerAddress = baseServerAddress.format(ports[block])
                        chunck = numpy.array_split(indeces, numBlocks)[block]
                        first, last = chunck[0], chunck[-1]
                        url = batchServerAddress + "ipfs/batch?ipfs_url={}&start={}&stop={}".format(traitsAddress, first, last)
                        response = http.get(url)
                        tokens = json.loads(response.text)
                        return tokens
                    return get_traits_external
                pids = []

                for port in batchServerPorts:
                    process = subprocess.Popen("python batch-server.py {} {}".format(port, baseHost), shell=True)
                    pids.append(process.pid)

                try:
                    indeces = [i for i in range(1, collectionSize + 1)]
                    get_traits_external = get_traits_external_curry(baseServerAddress, batchServerPorts, traitsAddress, indeces, parallelism)
                    tokensNested = pool.map(get_traits_external, [block for block in range(parallelism)])
                    tokens = list(chain.from_iterable(tokensNested))
                except:
                    for pid in pids:
                        try:
                            os.kill(pid, signal.SIGTERM)
                        except:
                            print("Failed to kill process with pid " + str(pid))
                    exit()

                for pid in pids:
                    try:
                        os.kill(pid, signal.SIGTERM)
                    except:
                        print("Failed to kill process with pid " + str(pid))
    
        traitsDistribution = compute_distribution(tokens, collectionSize)
        for token in tokens:
            if token["success"]:
                compute_rarity(token, traitsDistribution, collectionSize)
        pp.pprint(traitsDistribution)

        # Save the tokens
        os.makedirs(os.path.dirname(collectionTokensFileName), exist_ok=True)
        with open(collectionTokensFileName, 'w') as collectionTokensFile:
            collectionTokensFile.write(json.dumps(tokens))
    else:
        # The token data already exists, load it from the file
        print("skipped loading tokens")
        with open(collectionTokensFileName, 'r') as collectionTokensFile:
            tokens = json.loads(collectionTokensFile.read())

def create_collection_info(collection: str, collectionInfoFileName: str):
    opeanSeaCollectionData = metadata.get_opensea_collection_stats(collection)["collection"]
    collectionSize = int(opeanSeaCollectionData["stats"]["total_supply"])
    contractAddress = opeanSeaCollectionData["primary_asset_contracts"][-1]["address"]
    
    collectionInfo = {
        "collectionName" : collection,
        "collectionSize" : collectionSize,
        "contractAddress" : contractAddress,
        "contractABI" : metadata.get_contract_abi(contractAddress)
    }

    os.makedirs(os.path.dirname(collectionInfoFileName), exist_ok=True)
    with open(collectionInfoFileName, 'w') as filehandle:
        filehandle.write(json.dumps(collectionInfo))

if __name__ == "__main__":
    collections = ["the-sevens-official", "doodles-official", "monftersclub", "oxyaoriginproject"]
    collections = ["the-sevens-official", "monftersclub", "oxyaoriginproject"]
    collections = ["monftersclub"]

    for collection in collections:
        start_time = time.time()
        collectionInfoFileName = "collections/" + collection + "/" + collection + ".info"
        if not Path(collectionInfoFileName).is_file():
            create_collection_info(collection, collectionInfoFileName)
        else:
            print("skipped loading info")

        with open(collectionInfoFileName, 'rb') as collectionInfoFile:
            collectionInfo = json.loads(collectionInfoFile.read())
        
        compute_collection_rarities(collectionInfo)
        print("--- %s seconds ---" % (time.time() - start_time))
        

    