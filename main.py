from typing import Annotated

from fastapi import FastAPI, Depends
from database import get_session

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
database = Annotated[AsyncSession, Depends(get_session)]


@app.get("/")
async def index():
    return {"Hello": "World"}