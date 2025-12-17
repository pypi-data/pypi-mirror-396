from __future__ import annotations
from typing import Dict, Optional, Tuple
import base64, hashlib, os, httpx

from .config import OAuth2Config, TokenResponse, OAuth2ProviderConfig
from .contracts import UserRepository
from .rbac_services import RbacService

DEFAULT_OAUTH_URLS: Dict[str, Dict[str, str]] = {
    "google": {
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "user_info_url": "https://openidconnect.googleapis.com/v1/userinfo",
    },
    "linkedin": {
        "authorize_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "user_info_url": "https://api.linkedin.com/v2/userinfo",
    },
    "facebook": {
        "authorize_url": "https://www.facebook.com/v17.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v17.0/oauth/access_token",
        "user_info_url": "https://graph.facebook.com/me?fields=id,name,email",
    },
}


class OAuth2Result:
    def __init__(
        self,
        redirect_url: Optional[str] = None,
        cookies: Optional[Dict[str, str]] = None,
        tokens: Optional[TokenResponse] = None,
        user: Optional[dict] = None,
    ):
        self.redirect_url = redirect_url
        self.cookies = cookies or {}
        self.tokens = tokens
        self.user = user


class OAuth2Service:
    def __init__(self, cfg: OAuth2Config, user_repo: UserRepository):
        self.cfg = cfg
        self.user_repo = user_repo
        self.rbac = RbacService()

    @staticmethod
    def _b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    def _gen_state(self) -> str:
        return self._b64url(os.urandom(32))

    def _gen_pkce_pair(self) -> Tuple[str, str]:
        verifier = self._b64url(os.urandom(40))
        challenge = self._b64url(hashlib.sha256(verifier.encode()).digest())
        return verifier, challenge

    def _pcfg(self, provider: str) -> OAuth2ProviderConfig:
        if provider not in self.cfg.providers:
            raise ValueError(f"Unknown OAuth provider: {provider}")
        return self.cfg.providers[provider]

    def get_authorize_url(self, provider: str) -> OAuth2Result:
        pc = self._pcfg(provider)
        urls = DEFAULT_OAUTH_URLS.get(provider.lower())
        state = self._gen_state()
        verifier, challenge = self._gen_pkce_pair()

        params = {
            "client_id": pc.client_id,
            "response_type": "code",
            "redirect_uri": pc.callback_url,
            "scope": " ".join(pc.scope or ["openid", "email", "profile"]),
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }

        from urllib.parse import urlencode
        authorize_url = f"{(pc.authorize_url or urls['authorize_url'])}?{urlencode(params)}"

        return OAuth2Result(
            redirect_url=authorize_url,
            cookies={
                self.cfg.state_cookie_name: state,
                self.cfg.pkce_cookie_name: verifier,
            },
        )

    async def fetch_token(self, provider: str, code: str, verifier: str) -> TokenResponse:
        pc = self._pcfg(provider)
        urls = DEFAULT_OAUTH_URLS.get(provider.lower())
        token_url = pc.token_url or urls["token_url"]

        async with httpx.AsyncClient(timeout=self.cfg.http_timeout) as client:
            data = {
                "client_id": pc.client_id,
                "client_secret": pc.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": pc.callback_url,
                "code_verifier": verifier,
            }
            resp = await client.post(token_url, data=data)
            resp.raise_for_status()
            token_data = resp.json()

        return TokenResponse(**token_data)

    async def fetch_user_info(self, provider: str, access_token: str) -> dict:
        urls = DEFAULT_OAUTH_URLS.get(provider.lower())
        user_info_url = urls["user_info_url"]
        async with httpx.AsyncClient(timeout=self.cfg.http_timeout) as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            resp = await client.get(user_info_url, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def handle_callback(self, provider: str, code: str, state: str, cookies: Dict[str, str]) -> OAuth2Result:
        cookie_state = cookies.get(self.cfg.state_cookie_name)
        verifier = cookies.get(self.cfg.pkce_cookie_name)
        if not state or state != cookie_state:
            raise ValueError("Invalid OAuth state")

        tokens = await self.fetch_token(provider, code, verifier)
        user = await self.fetch_user_info(provider, tokens.access_token)
        return OAuth2Result(tokens=tokens, user=user)
