from pymongo.collection import Collection

from fastapi import APIRouter, Depends
router = APIRouter(
    prefix="/api/health",
    tags=["health"]
)

# https://testfully.io/blog/api-health-check-monitoring/
@router.get("")
def status():
    event = {"running": True}
    return event


