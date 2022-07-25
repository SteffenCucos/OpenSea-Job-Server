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
from db.token_dao import TokenDAO


from general.metadata_service import MetadataService
from general.token_service import TokenService

import logging

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

            # Load metadata
            metadata = self.metadataService.get_metadata(collectionName)
            collectionLoadJob.total = metadata.collectionSize
            collectionLoadJob.status = Status.LOADING
            self.jobDAO.update(collectionLoadJob)

            # Load tokens
            tokenProssesor = self.tokenService.get_token_processor(collectionLoadJob)
            tokens = tokenProssesor.get_tokens(parallelism=10)
                
            collectionLoadJob.progress = 1.0
            self.jobDAO.update(collectionLoadJob)
            
            # Compute distribution
            distribution = CollectionService.compute_distribution(metadata.collectionName, tokens)
            self.distributionDAO.save(distribution)

            # Compute rarities
            for token in tokens:
                token.rarity = CollectionService.compute_token_rarity(token, distribution)
            self.tokenService.update_batch(tokens, collectionName)

            # Finish job
            self.jobDAO.update_status(collectionLoadJob, Status.FINISHED)
        except Exception as error:
            collectionLoadJob.set_error(error)
            collectionLoadJob.update_status(Status.ERROR)
            self.jobDAO.update(collectionLoadJob)


    @staticmethod
    def compute_token_rarity(token: Token, distribution: Distribution) -> float:
        if token.error:
            return 0.0

        traitsDistribution = distribution.distribution

        total = 0.0
        for trait in token.traits:
            traitName = trait.trait_type
            traitValue = trait.value

            numWithTrait = traitsDistribution[traitName][traitValue]
            trait.rarity = numWithTrait / distribution.collectionSize
            total += trait.rarity

        return total / len(token.traits)

    @staticmethod
    def compute_distribution(collectionName: str, tokens: list[Token]) -> Distribution:
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
            distribution["None"] = len(tokens) - distributionSize

        print("Encountered {} errors".format(errorCount))
        return Distribution(collectionName, len(tokens), traitsDistribution)