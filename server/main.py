import uvicorn
from api.v1.api import api_router

from fastapi import FastAPI
app = FastAPI()
app.include_router(api_router)

if __name__ == "__main__":
    print("Enter")
    uvicorn.run(app, port=int(8000), host='localhost')