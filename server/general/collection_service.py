from importlib.metadata import distribution
from fastapi import Depends
from pkg_resources import Distribution

from general.threading_utils import run_task
from threading import Lock

from multiprocessing.pool import ThreadPool as Pool

from models.collection_load_job import CollectionLoadJob, Status
from models.token import Token
from models.distribution import Distribution

from db.job_dao import JobDAO
from db.distribution_dao import DistributionDAO


from general.metadata_service import MetadataService
from general.token_service import TokenService

import logging

from db.mongodb import get_tokens_collection
logger = logging.getLogger(__name__) 

class CollectionService():
    def __init__(self,
        jobDAO: JobDAO = Depends(JobDAO),
        distributionDAO: DistributionDAO = Depends(DistributionDAO),
        metadataService: MetadataService = Depends(MetadataService),
        tokenService: TokenService = Depends(TokenService)
    ):
        self.jobDAO = jobDAO
        self.distributionDAO = distributionDAO
        self.metadataService = metadataService
        self.tokenService = tokenService

    def download_collection_async(self, collectionLoadJob: CollectionLoadJob):
        run_task(self.download_collection_task, arguments=[collectionLoadJob])

    def download_collection_task(self, collectionLoadJob: CollectionLoadJob):
        logger.info("Logging")
        try:
            collectionName = collectionLoadJob.collectionName
            self.jobDAO.update_status(collectionLoadJob, Status.PREPARING)

            # Look for collection metadata already existing
            # Load collection metadata into collections/metadata
            # Set collectionSize & numLoaded fields
            metadata = self.metadataService.get_metadata(collectionName)
            collectionLoadJob.total = metadata.collectionSize
            collectionLoadJob.status = Status.LOADING
            self.jobDAO.update(collectionLoadJob)
            # Get tokens
            parallelism = 10

            tokens = []
            with Pool(parallelism) as pool:
                get_token = self.tokenService.get_token_function(collectionLoadJob)
                tokens = pool.map(get_token, [id for id in range(1, int(metadata.collectionSize) + 1)])
                
            collectionLoadJob.progress = 1.0
            self.jobDAO.update(collectionLoadJob)

            distribution = Distribution(metadata.collectionName, CollectionService.compute_distribution(tokens))
            self.distributionDAO.save(distribution)

            self.jobDAO.update_status(collectionLoadJob, Status.FINISHED)
        except Exception as error:
            collectionLoadJob.set_error(error)
            collectionLoadJob.update_status(Status.ERROR)
            self.jobDAO.update(collectionLoadJob)

    @staticmethod
    def compute_distribution(tokens: list[Token], collectionSize: int):
        traitsDistribution = {}
        errorCount = 0
        for token in tokens:
            if not token.success:
                # Should this log or error?
                errorCount += 1
                continue
            for trait in token.traits:
                traitType = trait.trait_type
                value = trait.value
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