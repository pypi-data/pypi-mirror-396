from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/workspace", tags=["workspace"])


class WorkspaceResponse(BaseModel):
    root: str


@router.get("")
def workspace(request: Request) -> WorkspaceResponse:
    return WorkspaceResponse(root=str(request.app.state.topology.workspace))
