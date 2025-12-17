from __future__ import annotations
from pydantic import BaseModel, Field, AnyHttpUrl
from typing import Dict, Optional, List, Callable, Awaitable, Union, Any, Literal


class JwtConfig(BaseModel):
    enabled: bool = True
    secret: str = Field(min_length=16)
    algorithm: str = "HS256"
    access_expires_seconds: int = 15 * 60

    refresh_enabled: bool = True
    refresh_expires_seconds: int = 30 * 24 * 60 * 60
    prefix: str = "/auth/jwt"

    # ---- Production-ready refresh rotation (optional, backward compatible) ----
    # If enabled, refresh tokens are single-use and stored server-side (Redis recommended).
    refresh_rotation_enabled: bool = False
    refresh_store_backend: Literal["memory", "redis"] = "memory"
    refresh_store_redis_url: Optional[str] = None
    refresh_store_redis_prefix: str = "authcore:refresh:"


class SessionConfig(BaseModel):
    enabled: bool = True
    ttl_seconds: int = 60 * 60
    prefix: str = "/auth/session"

    cookie_name: str = "session_id"
    cookie_secure: bool = True
    cookie_samesite: str = "None"
    cookie_domain: Optional[str] = None
    cookie_path: str = "/"

    # ---- Production-ready session store (optional, backward compatible) ----
    store_backend: Literal["memory", "redis"] = "memory"
    redis_url: Optional[str] = None
    redis_prefix: str = "authcore:sess:"


class OAuth2RedirectResponse(BaseModel):
    redirect_url: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Optional[str] = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    scope: Optional[str] = None


class OAuth2ProviderConfig(BaseModel):
    client_id: str
    client_secret: str
    callback_url: str
    scope: List[str] = Field(default_factory=lambda: ["openid", "email", "profile"])
    authorize_url: Optional[str] = None
    token_url: Optional[str] = None
    user_info_url: Optional[str] = None
    email_url: Optional[str] = None
    oidc_userinfo_url: Optional[str] = None
    pkce: bool = True
    use_oidc_userinfo: bool = False


class OAuth2Config(BaseModel):
    enabled: bool = True
    base_url: Optional[AnyHttpUrl] = "http://localhost:8000"
    prefix: str = "/auth"
    success_redirect: Optional[AnyHttpUrl] = "http://localhost:3000/oauth-success"
    failure_redirect: Optional[AnyHttpUrl] = "http://localhost:3000/oauth-failure"
    auto_provision: bool = True
    access_token_param: str = "accessToken"
    refresh_token_param: str = "refreshToken"
    default_role: str = "ROLE_USER"
    set_refresh_cookie: bool = True
    append_tokens_in_redirect: bool = False
    include_authorities: bool = True
    issue_jwt: bool = True

    cookie_secure: bool = True
    cookie_samesite: str = "None"
    cookie_domain: Optional[str] = None
    cookie_path: str = "/"

    state_cookie_name: str = "authcore_oauth2_state"
    pkce_cookie_name: str = "authcore_pkce_verifier"
    temp_code_ttl_seconds: int = 300
    state_ttl_seconds: int = 300

    http_timeout: int = 30
    providers: Dict[str, OAuth2ProviderConfig] = Field(default_factory=dict)

    # ---- Production-ready OAuth temp-code store (optional, backward compatible) ----
    temp_code_store_backend: Literal["memory", "redis"] = "memory"
    temp_code_store_redis_url: Optional[str] = None
    temp_code_store_redis_prefix: str = "authcore:oauthcode:"


class EndpointsConfig(BaseModel):
    login: Optional[str] = "/login"
    logout: Optional[str] = "/logout"
    refresh: Optional[str] = "/refresh"
    me: Optional[str] = "/me"


class EndpointEnabled(BaseModel):
    login: bool = True
    refresh: bool = True
    logout: bool = True
    me: bool = True


class TwoFAConfig:
    def __init__(
        self,
        enabled: bool,
        otp_length: int = 6,
        otp_type: str = "numeric",
        otp_expires_in: Union[int, str] = 300,
        transport: Optional[Callable[[str, Dict[str, Any]], Awaitable[None]]] = None,
        store_otp: Optional[Callable[[Union[str, int], str, int], Awaitable[None]]] = None,
        get_stored_otp: Optional[Callable[[Union[str, int]], Awaitable[Optional[str]]]] = None,
        clear_otp: Optional[Callable[[Union[str, int]], Awaitable[None]]] = None,
        on_otp_generated: Optional[Callable[[str, Dict[str, Any]], Awaitable[None]]] = None,
        on_otp_sent: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        on_verify_success: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        on_verify_fail: Optional[Callable[[Dict[str, Any], Exception], Awaitable[None]]] = None,
        max_attempts: int = 5,
        attempt_window_seconds: int = 10 * 60,
    ):
        self.enabled = enabled
        self.otp_length = otp_length
        self.otp_type = otp_type
        self.otp_expires_in = self._parse_expires(otp_expires_in)
        self.transport = transport
        self.store_otp = store_otp
        self.get_stored_otp = get_stored_otp
        self.clear_otp = clear_otp
        self.on_otp_generated = on_otp_generated
        self.on_otp_sent = on_otp_sent
        self.on_verify_success = on_verify_success
        self.on_verify_fail = on_verify_fail

        self.max_attempts = int(max_attempts)
        self.attempt_window_seconds = int(attempt_window_seconds)

    def _parse_expires(self, expires_in: Union[int, str]) -> int:
        if isinstance(expires_in, int):
            return expires_in
        if isinstance(expires_in, str):
            unit = expires_in[-1]
            value = int(expires_in[:-1])
            if unit == "s":
                return value
            if unit == "m":
                return value * 60
            if unit == "h":
                return value * 3600
        raise ValueError(f"Invalid expires_in format: {expires_in}")


class AuthCoreConfig(BaseModel):
    jwt: Optional[JwtConfig] = None
    session: Optional[SessionConfig] = None
    oauth: Optional[OAuth2Config] = None
    TwoFa: Optional[TwoFAConfig] = None
    endpoints: EndpointsConfig = EndpointsConfig()
    enabled: EndpointEnabled = EndpointEnabled()

    class Config:
        arbitrary_types_allowed = True

    @property
    def jwt_enabled(self) -> bool:
        return self.jwt is not None and self.jwt.enabled

    @property
    def session_enabled(self) -> bool:
        return self.session is not None and self.session.enabled

    @property
    def oauth_enabled(self) -> bool:
        return self.oauth is not None and self.oauth.enabled

    @property
    def two_fa_enabled(self) -> bool:
        return self.TwoFa is not None and self.TwoFa.enabled
