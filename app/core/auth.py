from functools import lru_cache
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    id: str
    email: str | None = None


def _issuer() -> str:
    return f"{str(settings.supabase_url).rstrip('/')}/auth/v1"


@lru_cache
def _jwks_client() -> jwt.PyJWKClient:
    return jwt.PyJWKClient(
        f"{_issuer()}/.well-known/jwks.json",
        cache_keys=True,
        timeout=5,
    )


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> CurrentUser:
    if credentials is None:
        raise _unauthorized()

    token = credentials.credentials
    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
            issuer=_issuer(),
            options={"require": ["exp", "iat", "sub", "aud", "iss"]},
        )
    except jwt.PyJWTError as exc:
        raise _unauthorized() from exc

    return CurrentUser(id=payload["sub"], email=payload.get("email"))
