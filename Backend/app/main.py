from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.routes import router
from .services.faiss_service import ensure_faiss_index
from .services.recommendation_service import load_jobs


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_faiss_index(load_jobs())
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router)
