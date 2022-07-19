from models.collection_load_job import CollectionLoadJob

from db.job_dao import JobDAO

from api.exceptions.not_found_exception import NotFoundException


from fastapi import APIRouter, Depends
router = APIRouter(
    prefix="/api/jobs",
    tags=["jobs"]
)

@router.get("/{jobId}")
def get_status(
    jobId: str,
    jobDAO: JobDAO = Depends(JobDAO)
) -> CollectionLoadJob:
    # Check for a running job
    if job := jobDAO.find_one_by_id(jobId):
        return jobDAO._serialize(job)
        
    raise NotFoundException("No job was found with Id {}".format(jobId))