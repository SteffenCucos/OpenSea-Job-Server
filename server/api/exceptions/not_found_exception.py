from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    def __init__(self, detail: str):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = detail