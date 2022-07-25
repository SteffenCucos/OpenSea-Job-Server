from pymongo.collection import Collection

from ...router import Router

router = Router(
    prefix="/api/health",
    tags=["health"]
)

# https://testfully.io/blog/api-health-check-monitoring/
@router.get("")
def status():
    event = {"running": True}
    return event


