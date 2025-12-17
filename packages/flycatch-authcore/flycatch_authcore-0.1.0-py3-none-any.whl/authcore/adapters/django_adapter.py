from __future__ import annotations

import json
import time
from typing import Dict, Any, Optional

from django.urls import path
from django.http import JsonResponse, HttpRequest, HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync

from ..config import AuthCoreConfig
from ..jwt_service import JWTService
from ..session_service import SessionService
from ..oauth_service import OAuth2Service
from ..contracts import UserRepository
from ..two_factor_auth_service import TwoFactorAuth
from ..store_backends import InMemoryTTLStore, RedisTTLStore, OAuthTempCodeStore


def _json(data: dict, status: int = 200) -> JsonResponse:
    return JsonResponse(data, status=status, safe=False)


def _parse_body(request: HttpRequest) -> dict:
    try:
        if request.body:
            return json.loads(request.body.decode("utf-8"))
    except Exception:
        pass
    return request.POST.dict()


class DjangoAuthCore:
    def __init__(self, cfg: AuthCoreConfig, repo: UserRepository):
        self.cfg = cfg
        self.repo = repo

        if cfg.jwt_enabled and cfg.session_enabled:
            raise ValueError("AuthCore misconfigured: both JWT and Session enabled. Choose only one.")
        if not cfg.jwt_enabled and not cfg.session_enabled:
            raise ValueError("AuthCore misconfigured: both JWT and Session disabled. Enable one.")

        self.jwt_service = JWTService(cfg.jwt) if cfg.jwt and cfg.jwt_enabled else None
        self.session_service = SessionService(cfg.session) if cfg.session and cfg.session_enabled else None
        self.oauth_service = OAuth2Service(cfg.oauth, repo) if cfg.oauth and cfg.oauth_enabled else None
        self.twofa_service = TwoFactorAuth(cfg.TwoFa) if cfg.TwoFa and cfg.two_fa_enabled else None

        # OAuth temp code store
        self._oauth_code_store: Optional[OAuthTempCodeStore] = None
        if cfg.oauth_enabled and cfg.oauth:
            if cfg.oauth.temp_code_store_backend == "redis":
                if not cfg.oauth.temp_code_store_redis_url:
                    raise ValueError("oauth.temp_code_store_backend='redis' requires oauth.temp_code_store_redis_url")
                kv = RedisTTLStore(cfg.oauth.temp_code_store_redis_url, cfg.oauth.temp_code_store_redis_prefix)
            else:
                kv = InMemoryTTLStore()
            self._oauth_code_store = OAuthTempCodeStore(kv, ttl_seconds=int(cfg.oauth.temp_code_ttl_seconds))

    # ---------- JWT ----------
    @csrf_exempt
    async def _jwt_login(self, request: HttpRequest) -> JsonResponse:
        if request.method != "POST":
            return _json({"detail": "Method Not Allowed"}, 405)

        body = _parse_body(request)
        email = body.get("email")
        password = body.get("password")

        user = await self.repo.get_by_email(email)
        if not user or not await self.repo.verify_password(password or "", user["password"]):
            return _json({"detail": "Unauthorized"}, 401)

        if self.cfg.two_fa_enabled:
            await self.twofa_service.initiate_2fa(user)  # type: ignore
            return _json({"detail": "OTP sent to user email. Please verify."})

        access = self.jwt_service.issue_access(user) if self.jwt_service else None
        refresh = self.jwt_service.issue_refresh(user) if self.jwt_service else None

        return _json({"token_type": "bearer", "access_token": access, "refresh_token": refresh})

    @csrf_exempt
    async def _jwt_refresh(self, request: HttpRequest) -> JsonResponse:
        if request.method != "POST":
            return _json({"detail": "Method Not Allowed"}, 405)

        body = _parse_body(request)
        token = body.get("refresh_token")
        if not token or not self.jwt_service:
            return _json({"detail": "Unauthorized"}, 401)

        import jwt as pyjwt
        try:
            data = self.jwt_service.verify_refresh(token)
        except pyjwt.ExpiredSignatureError:
            return _json({"detail": "Unauthorized"}, 401)
        except pyjwt.InvalidTokenError:
            return _json({"detail": "Unauthorized"}, 401)

        user = await self.repo.get_by_email(data.get("email"))
        if not user:
            return _json({"detail": "Unauthorized"}, 401)

        new_token = self.jwt_service.issue_access(user)
        new_refresh = self.jwt_service.issue_refresh(user)

        return _json({"access_token": new_token, "refresh_token": new_refresh, "token_type": "bearer"})

    @csrf_exempt
    async def _jwt_logout(self, request: HttpRequest) -> JsonResponse:
        return _json({"detail": "Logged out successfully"})

    @csrf_exempt
    async def _jwt_me(self, request: HttpRequest) -> JsonResponse:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not self.jwt_service:
            return _json({"detail": "Unauthorized"}, 401)

        token = auth_header.replace("Bearer ", "").strip()
        import jwt as pyjwt
        try:
            payload = self.jwt_service.verify_access(token)
        except pyjwt.ExpiredSignatureError:
            return _json({"detail": "Unauthorized"}, 401)
        except pyjwt.InvalidTokenError:
            return _json({"detail": "Unauthorized"}, 401)

        return _json({"id": payload.get("sub"), "email": payload.get("email"), "roles": payload.get("roles", [])})

    # ---------- SESSION ----------
    @csrf_exempt
    async def _session_login(self, request: HttpRequest) -> JsonResponse:
        if request.method != "POST":
            return _json({"detail": "Method Not Allowed"}, 405)

        body = _parse_body(request)
        user = await self.repo.get_by_email(body.get("email"))
        if not user or not await self.repo.verify_password(body.get("password", ""), user["password"]):
            return _json({"detail": "Unauthorized"}, 401)

        if self.cfg.two_fa_enabled:
            await self.twofa_service.initiate_2fa(user)  # type: ignore
            return _json({"detail": "OTP sent to user email. Please verify."})

        session_id = self.session_service.create(user)  # type: ignore
        response = _json({"detail": "Login successful"})
        response.set_cookie(
            self.cfg.session.cookie_name,  # type: ignore
            session_id,
            max_age=self.cfg.session.ttl_seconds,  # type: ignore
            httponly=True,
            samesite=self.cfg.session.cookie_samesite,  # type: ignore
            secure=self.cfg.session.cookie_secure,  # type: ignore
            domain=self.cfg.session.cookie_domain,  # type: ignore
            path=self.cfg.session.cookie_path,  # type: ignore
        )
        return response

    @csrf_exempt
    async def _session_refresh(self, request: HttpRequest) -> JsonResponse:
        if request.method != "POST":
            return _json({"detail": "Method Not Allowed"}, 405)

        sid_name = self.cfg.session.cookie_name  # type: ignore
        session_id = request.COOKIES.get(sid_name)
        if not session_id:
            return _json({"detail": "Unauthorized"}, 401)

        new_session_id = self.session_service.refresh(session_id)  # type: ignore
        if not new_session_id:
            return _json({"detail": "Unauthorized"}, 401)

        response = _json({"detail": "Session refreshed"})
        response.set_cookie(
            sid_name,
            new_session_id,
            max_age=self.cfg.session.ttl_seconds,  # type: ignore
            httponly=True,
            samesite=self.cfg.session.cookie_samesite,  # type: ignore
            secure=self.cfg.session.cookie_secure,  # type: ignore
            domain=self.cfg.session.cookie_domain,  # type: ignore
            path=self.cfg.session.cookie_path,  # type: ignore
        )
        return response

    @csrf_exempt
    async def _session_logout(self, request: HttpRequest) -> JsonResponse:
        sid_name = self.cfg.session.cookie_name  # type: ignore
        session_id = request.COOKIES.get(sid_name)
        if session_id:
            self.session_service.destroy(session_id)  # type: ignore
        response = _json({"detail": "Logged out successfully"})
        response.delete_cookie(sid_name, domain=self.cfg.session.cookie_domain, path=self.cfg.session.cookie_path)  # type: ignore
        return response

    @csrf_exempt
    async def _session_me(self, request: HttpRequest) -> JsonResponse:
        sid_name = self.cfg.session.cookie_name  # type: ignore
        session_id = request.COOKIES.get(sid_name)
        user = self.session_service.get(session_id) if session_id else None  # type: ignore
        if not user:
            return _json({"detail": "Unauthorized"}, 401)
        return _json(user)

    # ---------- OAUTH2 ----------
    @csrf_exempt
    async def _oauth_login(self, request: HttpRequest, provider: str) -> HttpResponse:
        if not self.oauth_service:
            return _json({"detail": "Internal server error"}, 500)

        result = self.oauth_service.get_authorize_url(provider)
        response = HttpResponseRedirect(result.redirect_url)

        for k, v in result.cookies.items():
            response.set_cookie(
                key=k,
                value=v,
                httponly=True,
                secure=self.cfg.oauth.cookie_secure,  # type: ignore
                samesite=self.cfg.oauth.cookie_samesite,  # type: ignore
                domain=self.cfg.oauth.cookie_domain,  # type: ignore
                path=self.cfg.oauth.cookie_path,  # type: ignore
                max_age=self.cfg.oauth.state_ttl_seconds,  # type: ignore
            )
        return response

    @csrf_exempt
    async def _oauth_callback(self, request: HttpRequest, provider: str) -> HttpResponse:
        if not self.oauth_service or not self._oauth_code_store:
            return _json({"detail": "OAuth2 not enabled"}, 400)

        code = request.GET.get("code")
        state = request.GET.get("state")
        cookies = request.COOKIES

        try:
            result = await self.oauth_service.handle_callback(provider, code, state, cookies)
        except Exception:
            return HttpResponseRedirect(f"{self.cfg.oauth.failure_redirect}?error=auth_failed")  # type: ignore

        user = result.user
        auth_code = self._oauth_code_store.mint(provider, user)
        redirect_url = f"{self.cfg.oauth.success_redirect}?provider={provider}&code={auth_code}"  # type: ignore
        return HttpResponseRedirect(redirect_url)

    @csrf_exempt
    async def _oauth_token(self, request: HttpRequest, provider: str) -> JsonResponse:
        if request.method != "POST":
            return JsonResponse({"detail": "Method not allowed"}, status=405)

        try:
            body = json.loads(request.body.decode())
        except Exception:
            return JsonResponse({"detail": "Invalid request"}, status=400)

        code = body.get("code")
        if not code:
            return JsonResponse({"detail": "Unauthorized"}, status=401)

        if not self._oauth_code_store:
            return JsonResponse({"detail": "Internal server error"}, status=500)

        user = self._oauth_code_store.pop(provider, code)
        if not user:
            return JsonResponse({"detail": "Unauthorized"}, status=401)

        if getattr(self.cfg, "jwt_enabled", False) and self.jwt_service:
            access_token = self.jwt_service.issue_access(user)  # type: ignore
            refresh_token = self.jwt_service.issue_refresh(user) if self.cfg.jwt.refresh_enabled else None  # type: ignore

            resp: Dict[str, Any] = {"success": True, "user": user, "access_token": access_token}
            if refresh_token:
                resp["refresh_token"] = refresh_token
                if getattr(self.cfg.oauth, "set_refresh_cookie", False):
                    response = JsonResponse(resp)
                    response.set_cookie(
                        key="AuthRefreshToken",
                        value=refresh_token,
                        httponly=True,
                        secure=self.cfg.oauth.cookie_secure,  # type: ignore
                        samesite=self.cfg.oauth.cookie_samesite,  # type: ignore
                        domain=self.cfg.oauth.cookie_domain,  # type: ignore
                        path=self.cfg.oauth.cookie_path,  # type: ignore
                        max_age=7 * 24 * 60 * 60,
                    )
                    return response
            return JsonResponse(resp)

        if getattr(self.cfg, "session_enabled", False):
            session_id = self.session_service.create(user)  # type: ignore
            response = JsonResponse({"success": True, "user": user})
            response.set_cookie(
                self.cfg.session.cookie_name,  # type: ignore
                session_id,
                max_age=self.cfg.session.ttl_seconds,  # type: ignore
                httponly=True,
                samesite=self.cfg.session.cookie_samesite,  # type: ignore
                secure=self.cfg.session.cookie_secure,  # type: ignore
                domain=self.cfg.session.cookie_domain,  # type: ignore
                path=self.cfg.session.cookie_path,  # type: ignore
            )
            return response

        return JsonResponse({"detail": "Internal server error"}, status=500)

    # ---------- 2FA ----------
    @csrf_exempt
    async def _verify_2fa(self, request: HttpRequest) -> JsonResponse:
        if request.method != "POST":
            return _json({"detail": "Method Not Allowed"}, 405)

        body = _parse_body(request)
        email = body.get("email")
        otp = body.get("otp")

        user = await self.repo.get_by_email(email)
        if not user:
            return _json({"detail": "Unauthorized"}, 401)

        if not otp:
            await self.twofa_service.initiate_2fa(user)  # type: ignore
            return _json({"detail": "OTP sent. Please verify."})

        try:
            valid = await self.twofa_service.verify_otp(user, otp)  # type: ignore
            if not valid:
                return _json({"detail": "Unauthorized"}, 401)
        except Exception:
            return _json({"detail": "Unauthorized"}, 401)

        if self.jwt_service:
            access = self.jwt_service.issue_access(user)
            refresh = self.jwt_service.issue_refresh(user)
            return _json({"token_type": "bearer", "access_token": access, "refresh_token": refresh})

        session_id = self.session_service.create(user)  # type: ignore
        response = _json({"detail": "2FA verification successful"})
        response.set_cookie(
            self.cfg.session.cookie_name,  # type: ignore
            session_id,
            max_age=self.cfg.session.ttl_seconds,  # type: ignore
            httponly=True,
            samesite=self.cfg.session.cookie_samesite,  # type: ignore
            secure=self.cfg.session.cookie_secure,  # type: ignore
            domain=self.cfg.session.cookie_domain,  # type: ignore
            path=self.cfg.session.cookie_path,  # type: ignore
        )
        return response

    def get_urls(self):
        urls = []
        e = self.cfg.endpoints
        en = self.cfg.enabled

        if self.cfg.jwt_enabled:
            p = self.cfg.jwt.prefix  # type: ignore
            if en.login:
                urls.append(path(f"{p.lstrip('/')}{e.login}", csrf_exempt(async_to_sync(self._jwt_login))))
            if en.logout:
                urls.append(path(f"{p.lstrip('/')}{e.logout}", csrf_exempt(async_to_sync(self._jwt_logout))))
            if en.refresh:
                urls.append(path(f"{p.lstrip('/')}{e.refresh}", csrf_exempt(async_to_sync(self._jwt_refresh))))
            if en.me:
                urls.append(path(f"{p.lstrip('/')}{e.me}", csrf_exempt(async_to_sync(self._jwt_me))))

        if self.cfg.session_enabled:
            p = self.cfg.session.prefix  # type: ignore
            if en.login:
                urls.append(path(f"{p.lstrip('/')}{e.login}", csrf_exempt(async_to_sync(self._session_login))))
            if en.refresh:
                urls.append(path(f"{p.lstrip('/')}{e.refresh}", csrf_exempt(async_to_sync(self._session_refresh))))
            if en.logout:
                urls.append(path(f"{p.lstrip('/')}{e.logout}", csrf_exempt(async_to_sync(self._session_logout))))
            if en.me:
                urls.append(path(f"{p.lstrip('/')}{e.me}", csrf_exempt(async_to_sync(self._session_me))))

        if self.cfg.oauth_enabled and self.cfg.oauth and self.cfg.oauth.providers:
            prefix = self.cfg.oauth.prefix.lstrip("/")  # type: ignore
            for provider in self.cfg.oauth.providers.keys():  # type: ignore
                urls.append(path(f"{prefix}/{provider}/login", async_to_sync(lambda req, prov=provider: self._oauth_login(req, prov))))
                urls.append(path(f"{prefix}/{provider}/callback", async_to_sync(lambda req, prov=provider: self._oauth_callback(req, prov))))
                # FIX: token endpoint includes provider, and handler accepts provider
                urls.append(path(f"{prefix}/{provider}/token", csrf_exempt(async_to_sync(lambda req, prov=provider: self._oauth_token(req, prov)))))

        if getattr(self.cfg, "two_fa_enabled", False):
            p = "/auth"
            if en.login:
                urls.append(path(f"{p.lstrip('/')}/2fa/verify", csrf_exempt(async_to_sync(self._verify_2fa))))

        return urls
