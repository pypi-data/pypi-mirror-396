from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from remotivelabs.cli.studio.api.auth import router as auth_router
from remotivelabs.cli.studio.api.files import router as files_router
from remotivelabs.cli.studio.api.workspace import router as workspace_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.startup()
    yield


api = FastAPI(lifespan=lifespan)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api.include_router(auth_router)
api.include_router(files_router)
api.include_router(workspace_router)

__all__ = ["api"]
