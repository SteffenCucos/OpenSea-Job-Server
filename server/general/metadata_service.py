from fastapi import Depends

import json


from general.credentials import Credentials, get_credentials
from general.http import get_retry_http

from models.metadata import Metadata

from db.metadata_dao import MetadataDAO

from requests.sessions import Session

class MetadataService():
    def __init__(
        self,
        http: Session = Depends(get_retry_http),
        credentials: Credentials = Depends(get_credentials),
        metadataDAO: MetadataDAO = Depends(MetadataDAO)
    ):
        self.http = http
        self.credentials = credentials
        self.metadataDAO = metadataDAO

    def get_contract_abi(self, contractAddress: str) -> str:
        etherScanUrl = 'https://api.etherscan.io/api?module=contract&action=getabi&address={}&apikey={}'.format(contractAddress, self.credentials.etherscan.apikey)
        response = self.http.get(etherScanUrl)
        return json.loads(response.text)["result"]

    def get_opensea_collection_stats(self, collectionName: str) -> dict:
        url = "https://api.opensea.io/api/v1/collection/" + collectionName
        response = self.http.get(url)
        return json.loads(response.text)

    def create_metadata(self, collectionName: str) -> Metadata:
        opeanSeaCollectionData = self.get_opensea_collection_stats(collectionName)["collection"]
        collectionSize = int(opeanSeaCollectionData["stats"]["total_supply"])
        contractAddress = opeanSeaCollectionData["primary_asset_contracts"][-1]["address"]
        contractABI = self.get_contract_abi(contractAddress)
        
        metadata = Metadata(collectionName, collectionSize, contractAddress, contractABI)
        self.metadataDAO.save(metadata)

        return metadata

    def get_metadata(self, collectionName: str) -> Metadata:
        metadata = self.metadataDAO.find_one_by_id(collectionName)
        if not metadata:
            metadata = self.create_metadata(collectionName)

        return metadata