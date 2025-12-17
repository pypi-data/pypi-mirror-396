from __future__ import annotations
import time
import jwt as pyjwt
from typing import Dict, Any, Optional
from flask import Flask, Blueprint, request, jsonify, make_response, redirect

from ..config import AuthCoreConfig
from ..contracts import UserRepository
from ..jwt_service import JWTService
from ..session_service import SessionService
from ..utils import public_identity
from ..permission_decorator import PermissionDenied
from ..oauth_service import OAuth2Service
from ..rbac_services import RbacService
from ..two_factor_auth_service import TwoFactorAuth
from ..store_backends import InMemoryTTLStore, RedisTTLStore, OAuthTempCodeStore


class FlaskAuthCore:
    def __init__(self, app: Flask, cfg: AuthCoreConfig, repo: UserRepository):
        self.app = app
        self.cfg = cfg
        self.repo = repo

        if cfg.jwt_enabled and cfg.session_enabled:
            raise ValueError("AuthCore misconfigured: both JWT and Session enabled. Choose only one.")
        if not cfg.jwt_enabled and not cfg.session_enabled:
            raise ValueError("AuthCore misconfigured: both JWT and Session disabled. Enable one.")

        self.jwt_service = JWTService(cfg.jwt) if cfg.jwt_enabled and cfg.jwt else None
        self.session_service = SessionService(cfg.session) if cfg.session_enabled and cfg.session else None
        self.oauth_service = OAuth2Service(cfg.oauth, repo) if cfg.oauth_enabled and cfg.oauth else None
        self.twofa_service = TwoFactorAuth(cfg.TwoFa) if cfg.two_fa_enabled and cfg.TwoFa else None

        self._oauth_code_store: Optional[OAuthTempCodeStore] = None
        if cfg.oauth_enabled and cfg.oauth:
            if cfg.oauth.temp_code_store_backend == "redis":
                if not cfg.oauth.temp_code_store_redis_url:
                    raise ValueError("oauth.temp_code_store_backend='redis' requires oauth.temp_code_store_redis_url")
                kv = RedisTTLStore(cfg.oauth.temp_code_store_redis_url, cfg.oauth.temp_code_store_redis_prefix)
            else:
                kv = InMemoryTTLStore()
            self._oauth_code_store = OAuthTempCodeStore(kv, ttl_seconds=int(cfg.oauth.temp_code_ttl_seconds))

        bp = Blueprint("authcore", __name__)

        if cfg.jwt_enabled:
            self._register_jwt_routes(bp)
        if cfg.session_enabled:
            self._register_session_routes(bp)
        if cfg.oauth_enabled:
            self._register_oauth2_routes(bp)
        if cfg.two_fa_enabled:
            self._register_2fa_routes(bp)

        app.register_blueprint(bp)

        @app.errorhandler(PermissionDenied)
        def handle_permission_error(exc):
            return jsonify({"detail": "Forbidden"}), 403

    def _unauth(self, msg="Unauthorized", code=401):
        return make_response(jsonify({"detail": msg}), code)

    # ---------- JWT ----------
    def _register_jwt_routes(self, bp):
        p = self.cfg.jwt.prefix  # type: ignore
        e = self.cfg.endpoints
        en = self.cfg.enabled

        if en.login:

            @bp.post(f"{p}{e.login}")
            async def jwt_login():
                body = request.get_json(force=True) or {}
                email = body.get("email", "")
                password = body.get("password", "")
                user = await self.repo.get_by_email(email)
                if not user or not await self.repo.verify_password(password, user["password"]):
                    return self._unauth()
                if self.cfg.two_fa_enabled:
                    await self.twofa_service.initiate_2fa(user)  # type: ignore
                    return jsonify({"message": "OTP sent to user"})
                access = self.jwt_service.issue_access(user)  # type: ignore
                refresh = self.jwt_service.issue_refresh(user)  # type: ignore
                return jsonify({"token_type": "bearer", "access_token": access, "refresh_token": refresh})

        if en.refresh:

            @bp.post(f"{p}{e.refresh}")
            async def jwt_refresh():
                body = request.get_json(force=True) or {}
                token = body.get("refresh_token", "")
                try:
                    data = self.jwt_service.verify_refresh(token)  # type: ignore
                except pyjwt.ExpiredSignatureError:
                    return self._unauth("Unauthorized")
                except pyjwt.InvalidTokenError:
                    return self._unauth("Unauthorized")
                user = await self.repo.get_by_email(data["email"])
                if not user:
                    return self._unauth("Unauthorized")
                access = self.jwt_service.issue_access(user)  # type: ignore
                new_refresh = self.jwt_service.issue_refresh(user)  # type: ignore
                return jsonify({"token_type": "bearer", "access_token": access, "refresh_token": new_refresh})

        if en.me:

            @bp.get(f"{p}{e.me}")
            def jwt_me():
                auth = request.headers.get("Authorization", "")
                if not auth.startswith("Bearer "):
                    return self._unauth("Unauthorized")
                token = auth.split(" ", 1)[1]
                try:
                    data = self.jwt_service.verify_access(token)  # type: ignore
                    return jsonify({"claims": data})
                except pyjwt.ExpiredSignatureError:
                    return self._unauth("Unauthorized")
                except pyjwt.InvalidTokenError:
                    return self._unauth("Unauthorized")

        if en.logout:

            @bp.post(f"{p}{e.logout}")
            def jwt_logout():
                return jsonify({"message": "successfully logged out"})

    # ---------- Session ----------
    def _register_session_routes(self, bp):
        p = self.cfg.session.prefix  # type: ignore
        e = self.cfg.endpoints
        en = self.cfg.enabled

        cookie_name = self.cfg.session.cookie_name  # type: ignore
        cookie_secure = self.cfg.session.cookie_secure  # type: ignore
        cookie_samesite = self.cfg.session.cookie_samesite  # type: ignore
        cookie_domain = self.cfg.session.cookie_domain  # type: ignore
        cookie_path = self.cfg.session.cookie_path  # type: ignore

        if en.login:

            @bp.post(f"{p}{e.login}")
            async def session_login():
                body = request.get_json(force=True) or {}
                email = body.get("email", "")
                password = body.get("password", "")
                user = await self.repo.get_by_email(email)
                if not user or not await self.repo.verify_password(password, user["password"]):
                    return self._unauth()
                if self.cfg.two_fa_enabled:
                    await self.twofa_service.initiate_2fa(user)  # type: ignore
                    return jsonify({"message": "OTP sent to user"})
                sid = self.session_service.create(user)  # type: ignore
                resp = jsonify({"message": "login successful"})
                resp.set_cookie(
                    cookie_name,
                    sid,
                    httponly=True,
                    samesite=cookie_samesite,
                    secure=cookie_secure,
                    domain=cookie_domain,
                    path=cookie_path,
                    max_age=self.cfg.session.ttl_seconds,  # type: ignore
                )
                return resp

        if en.logout:

            @bp.post(f"{p}{e.logout}")
            def session_logout():
                sid = request.cookies.get(cookie_name)
                if sid:
                    self.session_service.destroy(sid)  # type: ignore
                resp = jsonify({"message": "successfully logged out"})
                resp.delete_cookie(cookie_name, domain=cookie_domain, path=cookie_path)
                return resp

        if en.refresh:

            @bp.post(f"{p}{e.refresh}")
            def session_refresh():
                sid = request.cookies.get(cookie_name)
                if not sid:
                    return self._unauth("Unauthorized")
                new_sid = self.session_service.refresh(sid)  # type: ignore
                if not new_sid:
                    return self._unauth("Unauthorized")
                resp = jsonify({"message": "session refreshed"})
                resp.set_cookie(
                    cookie_name,
                    new_sid,
                    httponly=True,
                    samesite=cookie_samesite,
                    secure=cookie_secure,
                    domain=cookie_domain,
                    path=cookie_path,
                    max_age=self.cfg.session.ttl_seconds,  # type: ignore
                )
                return resp

        if en.me:

            @bp.get(f"{p}{e.me}")
            def session_me():
                sid = request.cookies.get(cookie_name)
                if not sid:
                    return self._unauth("Unauthorized")
                user = self.session_service.get(sid)  # type: ignore
                if not user:
                    return self._unauth("Unauthorized")
                return jsonify({"user": public_identity(user)})

    # ---------- OAuth ----------
    def _register_oauth2_routes(self, bp):
        base_prefix = self.cfg.oauth.prefix or "/auth"  # type: ignore
        if not self.cfg.oauth.providers:  # type: ignore
            return

        cookie_secure = self.cfg.oauth.cookie_secure  # type: ignore
        cookie_samesite = self.cfg.oauth.cookie_samesite  # type: ignore
        cookie_domain = self.cfg.oauth.cookie_domain  # type: ignore
        cookie_path = self.cfg.oauth.cookie_path  # type: ignore

        @bp.get(f"{base_prefix}/<provider>/login")
        def login(provider: str):
            result = self.oauth_service.get_authorize_url(provider)  # type: ignore
            resp = redirect(result.redirect_url)
            for k, v in result.cookies.items():
                resp.set_cookie(
                    key=k,
                    value=v,
                    httponly=True,
                    secure=cookie_secure,
                    samesite=cookie_samesite,
                    domain=cookie_domain,
                    path=cookie_path,
                    max_age=self.cfg.oauth.state_ttl_seconds,  # type: ignore
                )
            return resp

        @bp.get(f"{base_prefix}/<provider>/callback")
        async def callback(provider: str):
            failure_redirect = self.cfg.oauth.failure_redirect  # type: ignore

            error = request.args.get("error")
            if error:
                return redirect(f"{failure_redirect}?error=auth_failed")

            code = request.args.get("code")
            state = request.args.get("state")
            if not code:
                return redirect(f"{failure_redirect}?error=auth_failed")

            try:
                result = await self.oauth_service.handle_callback(  # type: ignore
                    provider, code, state, request.cookies
                )
                user = result.user

                if not self._oauth_code_store:
                    return redirect(f"{failure_redirect}?error=auth_failed")

                auth_code = self._oauth_code_store.mint(provider, user)
                success_url = f"{self.cfg.oauth.success_redirect}?provider={provider}&code={auth_code}"  # type: ignore
                return redirect(success_url)
            except Exception:
                return redirect(f"{failure_redirect}?error=auth_failed")

        @bp.post(f"{base_prefix}/<provider>/token")
        def exchange_token(provider: str):
            data = request.get_json() or {}
            code = data.get("code")
            if not code:
                return jsonify({"detail": "Unauthorized"}), 401

            if not self._oauth_code_store:
                return jsonify({"detail": "Internal server error"}), 500

            user = self._oauth_code_store.pop(provider, code)
            if not user:
                return jsonify({"detail": "Unauthorized"}), 401

            if self.cfg.jwt_enabled and self.cfg.oauth.issue_jwt:  # type: ignore
                access = self.jwt_service.issue_access(user)  # type: ignore
                refresh = self.jwt_service.issue_refresh(user)  # type: ignore
                body = {"success": True, "user": user, "access_token": access}
                if refresh and self.cfg.oauth.set_refresh_cookie:  # type: ignore
                    resp = make_response(jsonify({**body, "refresh_token": refresh}))
                    resp.set_cookie(
                        key="AuthRefreshToken",
                        value=refresh,
                        httponly=True,
                        secure=cookie_secure,
                        samesite=cookie_samesite,
                        domain=cookie_domain,
                        path=cookie_path,
                        max_age=7 * 24 * 60 * 60,
                    )
                    return resp
                if refresh:
                    body["refresh_token"] = refresh
                return jsonify(body)

            if self.cfg.session_enabled:
                sid = self.session_service.create(user)  # type: ignore
                resp = jsonify({"success": True, "user": user})
                resp.set_cookie(
                    self.cfg.session.cookie_name,  # type: ignore
                    sid,
                    httponly=True,
                    samesite=self.cfg.session.cookie_samesite,  # type: ignore
                    secure=self.cfg.session.cookie_secure,  # type: ignore
                    domain=self.cfg.session.cookie_domain,  # type: ignore
                    path=self.cfg.session.cookie_path,  # type: ignore
                    max_age=self.cfg.session.ttl_seconds,  # type: ignore
                )
                return resp

            return jsonify({"detail": "Internal server error"}), 500

    def _register_2fa_routes(self, bp):
        prefix = "/auth"

        @bp.post(f"{prefix}/2fa/verify")
        async def verify_2fa():
            body = request.get_json(force=True) or {}
            email = body.get("email")
            otp = body.get("otp")
            user = await self.repo.get_by_email(email)
            if not user:
                return self._unauth("Unauthorized", 401)

            try:
                valid = await self.twofa_service.verify_otp(user, otp)  # type: ignore
            except Exception:
                return self._unauth("Unauthorized", 401)

            if not valid:
                return self._unauth("Unauthorized", 401)

            if self.cfg.jwt_enabled:
                access = self.jwt_service.issue_access(user)  # type: ignore
                refresh = self.jwt_service.issue_refresh(user) if self.cfg.jwt.refresh_enabled else None  # type: ignore
                return jsonify({"token_type": "bearer", "access_token": access, "refresh_token": refresh})

            if self.cfg.session_enabled:
                sid = self.session_service.create(user)  # type: ignore
                resp = jsonify({"message": "Signin Successful"})
                resp.set_cookie(
                    self.cfg.session.cookie_name,  # type: ignore
                    sid,
                    httponly=True,
                    samesite=self.cfg.session.cookie_samesite,  # type: ignore
                    secure=self.cfg.session.cookie_secure,  # type: ignore
                    domain=self.cfg.session.cookie_domain,  # type: ignore
                    path=self.cfg.session.cookie_path,  # type: ignore
                    max_age=self.cfg.session.ttl_seconds,  # type: ignore
                )
                return resp
