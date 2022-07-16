from pyclbr import Function
from fastapi import Depends

import json

from threading import Lock
from multiprocessing.pool import ThreadPool as Pool

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

class TokenProssesor():
    def __init__(self, traitsAddress: str, collectionLoadJob: CollectionLoadJob, save_batch: Function):
        self.traitsAddress = traitsAddress
        self.collectionLoadJob = collectionLoadJob
        self.save_batch = save_batch
        self.http = get_retry_http()

        self.lock = Lock()
        self.batch = []
        self.batchNum = [1]

    def get_token_function(self):
        def get_token(tokenId: int) -> Token:
            url = self.traitsAddress.format(tokenId)
            try:
                response = self.http.get(url)
                traits = deserialize(json.loads(response.text)["attributes"], list[Trait])
                success = True
                error = None
            except Exception as error:
                error = error
                success = False
                traits = None

            token = Token(success, num=tokenId, url=url, traits=traits)
            if error:
                token.set_error(error)

            # Ensure strictly increasing counts
            self.lock.acquire()

            self.batch.append(token)
            if len(self.batch) % 25 == 0 or tokenId == self.collectionLoadJob.total:
                print("{}: saving batch #{} size {}".format(self.collectionLoadJob.collectionName, self.batchNum[0], len(self.batch)))
                self.batchNum[0] += 1
                self.save_batch(self.batch, self.collectionLoadJob)
                self.batch.clear()

            self.lock.release()
            return token
        return get_token
    
    def get_tokens(self, parallelism: int) -> list[Token]:
        tokens = []
        with Pool(parallelism) as pool:
            func = self.get_token_function()
            tokens = pool.map(func, [id for id in range(1, int(self.collectionLoadJob.total) + 1)])

        # There may be some unsaved tokens
        if len(self.batch) > 0:
            print("{}: saving batch #{} size {}".format(self.collectionLoadJob.collectionName, self.batchNum[0], len(self.batch)))
            self.save_batch(self.batch, self.collectionLoadJob)

        return tokens

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

    def get_token_processor(self, collectionLoadJob: CollectionLoadJob) -> TokenProssesor:
        metadata = self.metadataService.get_metadata(collectionLoadJob.collectionName)
        contractAddess = metadata.contractAddress
        contractABI = metadata.contractABI
        totalCount = metadata.collectionSize
        collectionName = metadata.collectionName
        traitsAddress = self.get_token_uri(contractAddess, contractABI)

        return TokenProssesor(traitsAddress, collectionLoadJob, self.save_batch_for_job)

    def get_token_uri(self, contractAddress: str, contractABI: str) -> str:
        contract = self.w3.eth.contract(address = Web3.toChecksumAddress(contractAddress), abi = contractABI)
        traitsAddress: str = contract.functions.tokenURI(1).call()
        if traitsAddress.find("ipfs://") >= 0:
            traitsAddress = "https://ipfs.io/ipfs/" + traitsAddress.replace("ipfs://", "")
        # strip the ID and prepare it for string formatting
        lastIndex = indices = [i for i, c in enumerate(traitsAddress) if c == "1"][-1]

        traitsAddress = traitsAddress[:lastIndex] + "{}" + traitsAddress[lastIndex + 1:]
        return traitsAddress
    
    def save_batch_for_job(
        self,
        batch: list[Token],
        collectionLoadJob: CollectionLoadJob
    ):
        #print("Starting Save")
        self.save_batch(batch, collectionLoadJob.collectionName)
        #print("Finished Save")
        collectionLoadJob.increment_loaded(len(batch))
        self.jobDAO.update(collectionLoadJob)

    def save_batch(
        self,
        batch: list[Token],
        collectionName: str
    ):
        tokenDAO = TokenDAO(get_tokens_collection(collectionName))
        tokenDAO.save_many(batch)

    def update_batch(
        self,
        batch: list[Token],
        collectionName: str
    ):
        tokenDAO = TokenDAO(get_tokens_collection(collectionName))
        tokenDAO.update_many(batch)