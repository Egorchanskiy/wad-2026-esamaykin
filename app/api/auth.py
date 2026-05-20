import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.api.deps import get_current_user
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(payload: RegisterRequest) -> TokenResponse:
    auth_service = AuthService()
    try:
        return await auth_service.register(payload.login, payload.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    auth_service = AuthService()
    try:
        return await auth_service.login(payload.login, payload.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest) -> TokenResponse:
    auth_service = AuthService()
    try:
        return await auth_service.refresh(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.post("/logout")
async def logout(payload: RefreshRequest) -> dict[str, str]:
    auth_service = AuthService()
    await auth_service.logout(payload.refresh_token)
    return {"status": "ok"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=str(current_user["_id"]),
        login=current_user["login"],
        auth_provider=current_user.get("auth_provider", "local"),
    )


@router.get("/github/login")
async def github_login() -> RedirectResponse:
    from urllib.parse import urlencode

    from app.core.config import get_settings

    settings = get_settings()
    if not settings.github_client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub OAuth is not configured",
        )

    query = urlencode(
        {
            "client_id": settings.github_client_id,
            "redirect_uri": settings.github_redirect_uri,
            "scope": "read:user user:email",
        }
    )
    return RedirectResponse(url=f"https://github.com/login/oauth/authorize?{query}")


@router.get("/github/callback")
async def github_callback(
    code: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
):
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_description or error,
        )
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Missing GitHub authorization code. "
                "Start login at GET /api/v1/auth/github/login — "
                "do not open /github/callback directly or refresh this page."
            ),
        )
    auth_service = AuthService()
    try:
        tokens = await auth_service.login_with_github_code(code)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    access = json.dumps(tokens.access_token)
    refresh = json.dumps(tokens.refresh_token)
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>GitHub login</title></head>
<body>
<p>GitHub login successful. Redirecting to app...</p>
<script>
localStorage.setItem("access_token", {access});
localStorage.setItem("refresh_token", {refresh});
window.location.href = "/";
</script>
</body></html>"""
    return HTMLResponse(html)
