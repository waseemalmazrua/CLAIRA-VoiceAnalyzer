from fastapi import Request

from app.core.auth import CurrentUser, _unauthorized


def user_identifier(request: Request) -> str:
    """Rate-limit key per authenticated user.

    Must run after `get_current_user`, which stores the user on `request.state`.
    Never falls back to a shared placeholder: no user means no request.
    """
    user: CurrentUser | None = getattr(request.state, "user", None)
    if user is None:
        raise _unauthorized()
    return f"user:{user.id}"
