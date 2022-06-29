import json

from threading import Lock
from web3 import Web3

from server.general.credentials import Credentials

class Metadata():
    def __init__(self, http, credentials: Credentials):
        self.credentials = credentials
        self.http = http
        self.w3 = Web3(Web3.HTTPProvider(self.credentials.infura.providerUrl))

    def get_contract_abi(self, contractAddress: str) -> str:
        etherScanUrl = 'https://api.etherscan.io/api?module=contract&action=getabi&address={}&apikey={}'.format(contractAddress, self.credentials.etherscan.apikey)
        response = self.http.get(etherScanUrl)
        return json.loads(response.text)["result"]

    def get_traits_address(self, contractAddress: str, contractABI: str) -> str:
        contract = self.w3.eth.contract(address = Web3.toChecksumAddress(contractAddress), abi = contractABI)
        traitsAddress = contract.functions.tokenURI(1).call()
        if traitsAddress.find("ipfs://") >= 0:
            traitsAddress = "https://ipfs.io/ipfs/" + traitsAddress.replace("ipfs://", "")
        # strip the ID and prepare it for string formatting
        return traitsAddress[:-1] + "{}"

    def get_opensea_collection_stats(self, collectionName: str) -> dict:
        url = "https://api.opensea.io/api/v1/collection/" + collectionName
        response = self.http.get(url)
        return json.loads(response.text)

    def get_traits_curry(self, totalCount: int, traitsAddress: str, count: list[int], lock: Lock):
        def get_traits(id):
            url = traitsAddress.format(id)
            try:
                response = self.http.get(url)
                success = True
                traits = json.loads(response.text)["attributes"]
            except:
                success = False
                traits = None
                print("failure")

            # Ensure strictly increasing counts
            lock.acquire()
            localCount = count[0] + 1
            count[0] = count[0] + 1
            #if localCount % 500 == 0:
            print(str(localCount) + "/" + str(totalCount))
            lock.release()
            return {
                "success" : success,
                "id" : id,
                "url" : url,
                "traits" : traits
            }
        return get_traits

    