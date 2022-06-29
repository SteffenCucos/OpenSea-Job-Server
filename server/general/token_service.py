from fastapi import Depends

import json

from threading import Lock
from web3 import Web3

from models.token import Token
from models.trait import Trait
from models.metadata import Metadata
from models.collection_load_job import CollectionLoadJob

from general.metadata_service import MetadataService
from general.credentials import Credentials, get_credentials
from general.http import get_retry_http

from db.token_dao import TokenDAO
from db.job_dao import JobDAO
from db.mongodb import get_tokens_collection
from db.dict_to_class import deserialize

from requests.sessions import Session


import logging
logger = logging.getLogger(__name__) 

class TokenService():
    def __init__(self,
        http: Session = Depends(get_retry_http),
        credentials: Credentials = Depends(get_credentials),
        metadataService: MetadataService = Depends(MetadataService),
        jobDAO: JobDAO = Depends(JobDAO)
    ):
        self.http = http
        self.credentials = credentials
        self.w3 = Web3(Web3.HTTPProvider(self.credentials.infura.providerUrl))
        self.metadataService = metadataService
        self.jobDAO = jobDAO

    def get_token_uri(self, contractAddress: str, contractABI: str) -> str:
        contract = self.w3.eth.contract(address = Web3.toChecksumAddress(contractAddress), abi = contractABI)
        traitsAddress = contract.functions.tokenURI(1).call()
        if traitsAddress.find("ipfs://") >= 0:
            traitsAddress = "https://ipfs.io/ipfs/" + traitsAddress.replace("ipfs://", "")
        # strip the ID and prepare it for string formatting
        return traitsAddress[:-1] + "{}"

    def get_token_function(self, collectionLoadJob: CollectionLoadJob):
        lock = Lock()

        metadata = self.metadataService.get_metadata(collectionLoadJob.collectionName)
        contractAddess = metadata.contractAddress
        contractABI = metadata.contractABI
        totalCount = metadata.collectionSize
        collectionName = metadata.collectionName
        traitsAddress = self.get_token_uri(contractAddess, contractABI)
        
        batch = []
        batchNum = [1]
        tokenDAO: TokenDAO = TokenDAO(get_tokens_collection(collectionName))

        def get_token(tokenId: int) -> Token:
            url = traitsAddress.format(tokenId)
            try:
                response = self.http.get(url)
                success = True
                traits = deserialize(json.loads(response.text)["attributes"], list[Trait])
            except:
                success = False
                traits = None

            # Ensure strictly increasing counts
            lock.acquire()
            token = Token(success, num=tokenId, url=url, traits=traits)
            print("Got Token", tokenId)
            # Save tokens in batches
            batch.append(token)

            if len(batch) % 10 == 0 or tokenId == totalCount:
                print("Saving batch #{} size {}".format(batchNum[0], len(batch)))
                batchNum[0] += 1
                self.save_batch(batch, collectionLoadJob, tokenDAO)
                batch.clear()

            lock.release()
            return token
        return get_token

    # Move this into collection_service, or pass a callback
    def save_batch(
        self,
        batch: list[Token],
        collectionLoadJob: CollectionLoadJob,
        tokenDAO: TokenDAO
    ):
        print("Starting Save")
        for token in batch:
            if token.success == False:
                break;
        tokenDAO.save_many(batch)
        print("Finished Save")
        collectionLoadJob.increment_loaded(len(batch))
        self.jobDAO.update(collectionLoadJob)

        

