from dataclasses import dataclass

from models.token import Token
from models.trait import Trait
from models.metadata import Metadata
from models.collection_load_job import CollectionLoadJob, Status

from api.exceptions.not_found_exception import NotFoundException

from general.threading_utils import run_task
from general.collection_service import CollectionService

from db.job_dao import JobDAO
from db.token_dao import TokenDAO
from db.distribution_dao import DistributionDAO
from db.metadata_dao import MetadataDAO

from fastapi import Depends
from ...router import Router

router = Router(
    prefix="/api/collections",
    tags=["collections"]
)

@router.post("/{collectionName}/download")
def download_collection(
    collectionName: str,
    jobDAO: JobDAO = Depends(JobDAO),
    collectionService: CollectionService = Depends(CollectionService)
) -> str:
    # Check if a job is already running
    # We don't have an Id here, so the collectionName + status will be our key
    if job := jobDAO.find_one_by_condition(
        condition = {
            "collectionName": collectionName,
            "status": {
                "$ne" : Status.FINISHED.value
            }
        }
    ):
        return job._id

    # Create the job, insert it into the db, then start it.
    job = CollectionLoadJob(collectionName)
    jobDAO.save(job)

    # Runs the load task on a new thread
    collectionService.download_collection_async(job)
    # Start executing job in thread
    return job._id

@router.get("/{collectionName}/distribution")
def get_collection_distribution(
    collectionName: str,
    distributionDAO: DistributionDAO = Depends(DistributionDAO)
):
    if distribution := distributionDAO.find_one_by_condition({"collectionName": collectionName}):
        return distribution
    
    raise NotFoundException("No distribution found for {}".format(collectionName))
    
@router.get("/{collectionName}/token/{tokenNumber}")
def get_token(
    collectionName: str,
    tokenNumber: int,
    tokenDAO: TokenDAO = Depends(TokenDAO)
) -> Token:
    if token := tokenDAO.find_one_by_id(str(tokenNumber)):
        return token

    raise NotFoundException("No token found with num {} in collection {}".format(tokenNumber, collectionName))




