# import logging
from collections.abc import Generator
from fastapi import FastAPI
from sqlmodel import Session, SQLModel, select
from app.core.db import engine
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from app.api.main import api_router
from app.core.config import settings
from app.middleware import AuthMiddleware, OptionalAuthMiddleware
from fastapi.middleware.cors import CORSMiddleware

# ВАЖНО: Импортируем модели чтобы SQLModel знал о них
from app.models import User, Torney

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(_):
    create_db_and_tables()
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Добавляем middleware для проверки токенов
# Раскомментируйте строку ниже чтобы включить обязательную проверку токенов на всех роутах
# app.add_middleware(AuthMiddleware)

# Или используйте опциональную проверку
app.add_middleware(OptionalAuthMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", '*'],
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
# nodemon --watch app --watch alembic --ext py,env \
#   --ignore venv --ignore .git --signal SIGTERM \
#   --exec "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"