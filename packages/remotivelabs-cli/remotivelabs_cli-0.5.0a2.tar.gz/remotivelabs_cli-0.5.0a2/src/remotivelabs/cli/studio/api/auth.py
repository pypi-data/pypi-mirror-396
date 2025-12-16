from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from remotivelabs.cli.settings import settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "Bearer"


@router.get("/token")
def token() -> AccessToken:
    token = settings.get_active_token()
    if not token:
        raise HTTPException(status_code=401, detail="No active token found")
    return AccessToken(access_token=token)
