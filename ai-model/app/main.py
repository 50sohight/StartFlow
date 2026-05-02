from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .routers import generate


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup: Initializing services...")

    from .llm.model_loader import VikhrRAG

    VikhrRAG.get_llm()

    yield


app = FastAPI(
    title="StartFlow AI Service",
    description="Бэкенд-сервис для аналитики проектов и генерации графиков",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Настройка CORS ---
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router, prefix="/api", tags=["AI Model"])


@app.get("/")
async def root():
    return {"message": "StartFlow AI Backend is running"}
