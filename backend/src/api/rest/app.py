from fastapi import FastAPI
from src.api.rest.routes import auth
from src.api.rest.routes import voice
from src.api.rest.routes import users
from src.api.middleware.cors import add_cors_middleware
from src.api.middleware.logging import logging_middleware
from src.api.middleware.auth import AuthorizationMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from src.data.clients.postgres_client import init_db

app = FastAPI()

app.add_middleware(AuthorizationMiddleware)
app.add_middleware(BaseHTTPMiddleware, dispatch = logging_middleware)

add_cors_middleware(app)

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(router=auth.router)

app.include_router(router = voice.router)


app.include_router(router = users.router)