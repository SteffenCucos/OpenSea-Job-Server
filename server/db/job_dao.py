from pymongo.collection import Collection
from fastapi import Depends

from models.collection_load_job import CollectionLoadJob, Status

from db.mongodb import get_jobs_collection
from db.base_dao import BaseDAO

class JobDAO(BaseDAO):
    '''
    Responsible for manipulating the collections/jobs Collection
    '''
    def __init__(self, jobsCollection: Collection = Depends(get_jobs_collection)):
        self.collection = jobsCollection
        self.classType = CollectionLoadJob

    def update_status(self, job: CollectionLoadJob, status: Status):
        job.update_status(status)
        self.update(job)