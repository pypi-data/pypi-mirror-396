from __future__ import annotations
from typing import Optional, Dict, Any
import time
import jwt as pyjwt

from fastapi import FastAPI, Request, HTTPException, Response, status, Body
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel

from ..config import AuthCoreConfig
from ..contracts import UserRepository
from ..jwt_service import JWTService
from ..session_service import SessionService
from ..oauth_service import OAuth2Service
from ..two_factor_auth_service import TwoFactorAuth
from ..utils import public_identity
from ..store_backends import InMemoryTTLStore, RedisTTLStore, OAuthTempCodeStore


class LoginBody(BaseModel):
    email: str
    password: str


class RefreshBody(BaseModel):
    refresh_token: str


class FastAPIAuthCore:
    def __init__(self, app: FastAPI, cfg: AuthCoreConfig, repo: UserRepository):
        self.app = app
        self.cfg = cfg
        self.repo = repo

        if cfg.jwt_enabled and cfg.session_enabled:
            raise ValueError("AuthCore misconfigured: both JWT and Session enabled. Choose only one.")
        if not cfg.jwt_enabled and not cfg.session_enabled:
            raise ValueError("AuthCore misconfigured: both JWT and Session disabled. Enable one.")

        self.jwt_service = JWTService(cfg.jwt) if cfg.jwt_enabled and cfg.jwt else None
        self.session_service = SessionService(cfg.session) if cfg.session_enabled and cfg.session else None
        self.oauth2_service = OAuth2Service(cfg.oauth, repo) if cfg.oauth_enabled and cfg.oauth else None
        self.twofa_service = TwoFactorAuth(cfg.TwoFa) if cfg.two_fa_enabled and cfg.TwoFa else None

        # OAuth temp code store (prod-ready: Redis optional)
        self._oauth_code_store: Optional[OAuthTempCodeStore] = None
        if cfg.oauth_enabled and cfg.oauth:
            if cfg.oauth.temp_code_store_backend == "redis":
                if not cfg.oauth.temp_code_store_redis_url:
                    raise ValueError("oauth.temp_code_store_backend='redis' requires oauth.temp_code_store_redis_url")
                kv = RedisTTLStore(cfg.oauth.temp_code_store_redis_url, cfg.oauth.temp_code_store_redis_prefix)
            else:
                kv = InMemoryTTLStore()
            self._oauth_code_store = OAuthTempCodeStore(kv, ttl_seconds=int(cfg.oauth.temp_code_ttl_seconds))

        self.router = APIRouter()

        if cfg.jwt_enabled:
            self._register_jwt_routes()
        if cfg.session_enabled:
            self._register_session_routes()
        if cfg.oauth_enabled:
            self._register_oauth2_routes()
        if cfg.two_fa_enabled:
            self._register_2fa_routes()

        if len(self.router.routes) > 0:
            self.app.include_router(self.router, tags=["authcore"])

    def _error(self, code: int, msg: str):
        raise HTTPException(status_code=code, detail=msg)

    def _http_response(self, typ: str, access: str, refresh: Optional[str]):
        return {"token_type": typ, "access_token": access, "refresh_token": refresh}

    # ---------- JWT ----------
    def _register_jwt_routes(self) -> None:
        p = self.cfg.jwt.prefix  # type: ignore
        e = self.cfg.endpoints
        en = self.cfg.enabled

        if en.login:

            @self.router.post(f"{p}{e.login}")
            async def jwt_login(body: LoginBody) -> Dict[str, Any]:
                user = await self.repo.get_by_email(body.email)
                if not user or not await self.repo.verify_password(body.password, user["password"]):
                    self._error(status.HTTP_401_UNAUTHORIZED, "Unauthorized")

                if self.cfg.two_fa_enabled:
                    await self.twofa_service.initiate_2fa(user)  # type: ignore
                    return {"message": "OTP sent to user"}

                access = self.jwt_service.issue_access(user)  # type: ignore
                refresh = self.jwt_service.issue_refresh(user)  # type: ignore
                return self._http_response("bearer", access, refresh)

        if en.refresh:

            @self.router.post(f"{p}{e.refresh}")
            async def jwt_refresh(body: RefreshBody) -> Dict[str, Any]:
                try:
                    data = self.jwt_service.verify_refresh(body.refresh_token)  # type: ignore
                except pyjwt.ExpiredSignatureError:
                    self._error(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
                except pyjwt.InvalidTokenError:
                    self._error(status.HTTP_401_UNAUTHORIZED, "Unauthorized")

                user = await self.repo.get_by_email(data["email"])
                if not user:
                    self._error(status.HTTP_401_UNAUTHORIZED, "Unauthorized")

                access = self.jwt_service.issue_access(user)  # type: ignore
                refresh = self.jwt_service.issue_refresh(user)  # type: ignore
                return self._http_response("bearer", access, refresh)

        if en.me:

            @self.router.get(f"{p}{e.me}")
            async def jwt_me(request: Request) -> Dict[str, Any]:
                auth = request.headers.get("Authorization", "")
                if not auth.startswith("Bearer "):
                    self._error(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
                token = auth.split(" ", 1)[1]
                try:
                    data = self.jwt_service.verify_access(token)  # type: ignore
                    return {"data": data}
                except pyjwt.ExpiredSignatureError:
                    self._error(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
                except pyjwt.InvalidTokenError:
                    self._error(status.HTTP_401_UNAUTHORIZED, "Unauthorized")

        if en.logout:

            @self.router.post(f"{p}{e.logout}")
            async def jwt_logout() -> Dict[str, Any]:
                return {"message": "successfully logged out"}

    # ---------- Session ----------
    def _register_session_routes(self) -> None:
        p = self.cfg.session.prefix  # type: ignore
        e = self.cfg.endpoints
        en = self.cfg.enabled

        cookie_name = self.cfg.session.cookie_name  # type: ignore
        cookie_secure = self.cfg.session.cookie_secure  # type: ignore
        cookie_samesite = self.cfg.session.cookie_samesite  # type: ignore
        cookie_domain = self.cfg.session.cookie_domain  # type: ignore
        cookie_path = self.cfg.session.cookie_path  # type: ignore

        if en.login:

            @self.router.post(f"{p}{e.login}")
            async def session_login(body: LoginBody, response: Response) -> Dict[str, Any]:
                user = await self.repo.get_by_email(body.email)
                if not user or not await self.repo.verify_password(body.password, user["password"]):
                    self._error(status.HTTP_401_UNAUTHORIZED, "Unauthorized")

                if self.cfg.two_fa_enabled:
                    await self.twofa_service.initiate_2fa(user)  # type: ignore
                    return {"message": "OTP sent to user"}

                sid = self.session_service.create(user)  # type: ignore
                response.set_cookie(
                    cookie_name,
                    sid,
                    httponly=True,
                    samesite=cookie_samesite,
                    secure=cookie_secure,
                    domain=cookie_domain,
                    path=cookie_path,
                    max_age=self.cfg.session.ttl_seconds,  # type: ignore
                )
                return {"message": "login successful"}

        if en.refresh:

            @self.router.post(f"{p}{e.refresh}")
            async def session_refresh(request: Request, response: Response) -> Dict[str, Any]:
                sid = request.cookies.get(cookie_name)
                if not sid:
                    self._error(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
                new_sid = self.session_service.refresh(sid)  # type: ignore
                if not new_sid:
                    self._error(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
                response.set_cookie(
                    cookie_name,
                    new_sid,
                    httponly=True,
                    samesite=cookie_samesite,
                    secure=cookie_secure,
                    domain=cookie_domain,
                    path=cookie_path,
                    max_age=self.cfg.session.ttl_seconds,  # type: ignore
                )
                return {"message": "session refreshed"}

        if en.logout:

            @self.router.post(f"{p}{e.logout}")
            async def session_logout(request: Request, response: Response) -> Dict[str, Any]:
                sid = request.cookies.get(cookie_name)
                if sid:
                    self.session_service.destroy(sid)  # type: ignore
                response.delete_cookie(cookie_name, domain=cookie_domain, path=cookie_path)
                return {"message": "successfully logged out"}

        if en.me:

            @self.router.get(f"{p}{e.me}")
            async def session_me(request: Request) -> Dict[str, Any]:
                sid = request.cookies.get(cookie_name)
                if not sid:
                    self._error(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
                user = self.session_service.get(sid)  # type: ignore
                if not user:
                    self._error(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
                return {"user": public_identity(user)}

    # ---------- OAuth ----------
    def _register_oauth2_routes(self) -> None:
        router: APIRouter = self.router
        base_prefix = self.cfg.oauth.prefix  # type: ignore
        cookie_secure = self.cfg.oauth.cookie_secure  # type: ignore
        cookie_samesite = self.cfg.oauth.cookie_samesite  # type: ignore
        cookie_domain = self.cfg.oauth.cookie_domain  # type: ignore
        cookie_path = self.cfg.oauth.cookie_path  # type: ignore

        if not self.cfg.oauth.providers:  # type: ignore
            return

        for provider_name in self.cfg.oauth.providers.keys():  # type: ignore
            login_path = f"{base_prefix}/{provider_name}/login"
            callback_path = f"{base_prefix}/{provider_name}/callback"
            token_path = f"{base_prefix}/{provider_name}/token"

            @router.get(login_path)
            async def login(provider_name: str = provider_name):
                result = self.oauth2_service.get_authorize_url(provider_name)  # type: ignore
                response = RedirectResponse(result.redirect_url)
                for k, v in result.cookies.items():
                    response.set_cookie(
                        key=k,
                        value=v,
                        httponly=True,
                        secure=cookie_secure,
                        samesite=cookie_samesite,
                        path=cookie_path,
                        domain=cookie_domain,
                        max_age=self.cfg.oauth.state_ttl_seconds,  # type: ignore
                    )
                return response

            @router.get(callback_path)
            async def oauth2_callback(request: Request, provider_name: str = provider_name):
                failure_redirect = self.cfg.oauth.failure_redirect  # type: ignore
                error = request.query_params.get("error")
                if error:
                    return RedirectResponse(url=f"{failure_redirect}?error=auth_failed")

                code = request.query_params.get("code")
                state = request.query_params.get("state")
                if not code:
                    return RedirectResponse(url=f"{failure_redirect}?error=no_code")

                try:
                    result = await self.oauth2_service.handle_callback(  # type: ignore
                        provider_name, code, state, request.cookies
                    )
                    user = result.user

                    if not self._oauth_code_store:
                        raise RuntimeError("OAuth temp store not initialized")

                    auth_code = self._oauth_code_store.mint(provider_name, user)
                    success_url = f"{self.cfg.oauth.success_redirect}?provider={provider_name}&code={auth_code}"  # type: ignore
                    return RedirectResponse(url=success_url)
                except Exception:
                    return RedirectResponse(url=f"{failure_redirect}?error=auth_failed")

            @router.post(token_path)
            async def exchange_token(request: Request, response: Response, provider_name: str = provider_name):
                data = await request.json()
                code = data.get("code")
                if not code:
                    raise HTTPException(status_code=401, detail="Unauthorized")

                if not self._oauth_code_store:
                    raise HTTPException(status_code=500, detail="Internal server error")

                user = self._oauth_code_store.pop(provider_name, code)
                if not user:
                    raise HTTPException(status_code=401, detail="Unauthorized")

                if self.cfg.jwt_enabled:
                    access_token = self.jwt_service.issue_access(user)  # type: ignore
                    refresh_token = self.jwt_service.issue_refresh(user)  # type: ignore
                    resp = {"success": True, "user": user, "access_token": access_token}

                    if refresh_token and self.cfg.oauth.set_refresh_cookie:  # type: ignore
                        resp["refresh_token"] = refresh_token
                        response.set_cookie(
                            "AuthRefreshToken",
                            refresh_token,
                            httponly=True,
                            secure=cookie_secure,
                            samesite=cookie_samesite,
                            domain=cookie_domain,
                            path=cookie_path,
                            max_age=7 * 24 * 60 * 60,
                        )
                    elif refresh_token:
                        resp["refresh_token"] = refresh_token

                    return JSONResponse(resp)

                if self.cfg.session_enabled:
                    sid = self.session_service.create(user)  # type: ignore
                    response.set_cookie(
                        self.cfg.session.cookie_name,  # type: ignore
                        sid,
                        httponly=True,
                        samesite=self.cfg.session.cookie_samesite,  # type: ignore
                        secure=self.cfg.session.cookie_secure,  # type: ignore
                        domain=self.cfg.session.cookie_domain,  # type: ignore
                        path=self.cfg.session.cookie_path,  # type: ignore
                        max_age=self.cfg.session.ttl_seconds,  # type: ignore
                    )
                    return JSONResponse({"success": True, "user": user})

                raise HTTPException(status_code=500, detail="Internal server error")

    # ---------- 2FA ----------
    def _register_2fa_routes(self):
        router = APIRouter(prefix="/auth")

        @router.post("/2fa/verify")
        async def verify_2fa(body: dict = Body(...)):
            email = body.get("email")
            otp = body.get("otp")
            user = await self.repo.get_by_email(email)
            if not user:
                raise HTTPException(status_code=401, detail="Unauthorized")

            try:
                valid = await self.twofa_service.verify_otp(user, otp)  # type: ignore
            except Exception:
                raise HTTPException(status_code=401, detail="Unauthorized")

            if not valid:
                raise HTTPException(status_code=401, detail="Unauthorized")

            if self.cfg.jwt_enabled:
                access = self.jwt_service.issue_access(user)  # type: ignore
                refresh = self.jwt_service.issue_refresh(user) if self.cfg.jwt.refresh_enabled else None  # type: ignore
                return {"token_type": "bearer", "access_token": access, "refresh_token": refresh}

            if self.cfg.session_enabled:
                sid = self.session_service.create(user)  # type: ignore
                content = {"message": "Signin Successful"}
                response = JSONResponse(content=content)
                response.set_cookie(
                    self.cfg.session.cookie_name,  # type: ignore
                    sid,
                    httponly=True,
                    samesite=self.cfg.session.cookie_samesite,  # type: ignore
                    secure=self.cfg.session.cookie_secure,  # type: ignore
                    domain=self.cfg.session.cookie_domain,  # type: ignore
                    path=self.cfg.session.cookie_path,  # type: ignore
                    max_age=self.cfg.session.ttl_seconds,  # type: ignore
                )
                return response

        self.app.include_router(router, tags=["authcore"])
