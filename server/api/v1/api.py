from fastapi import APIRouter

from api.v1.endpoints import collections, health, jobs

api_router = APIRouter()
api_router.include_router(collections.router)
api_router.include_router(health.router)
api_router.include_router(jobs.router)
