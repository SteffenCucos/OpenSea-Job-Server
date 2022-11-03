from pymongo.collection import Collection

from v1 import base_route
from ...router import Router


router = Router(
    prefix= base_route + "/health",
    tags=["health"]
)

# https://testfully.io/blog/api-health-check-monitoring/
@router.get("")
def status():
    event = {"running": True}
    return event


