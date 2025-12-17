import unittest
from flask import Flask
from flask.testing import FlaskClient
from authcore.adapters.flask_adapter import FlaskAuthCore
from authcore.config import AuthCoreConfig, JwtConfig, SessionConfig
from authcore.contracts import UserRepository
import bcrypt
import json


class UserService(UserRepository):
    async def get_by_email(self, email: str):
        if email == "example@example.com":
            return {"id": 1, "email": "example@example.com", "password": "password123"}
        return None

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        return plain_password == password_hash


class FlaskAuthCoreTest(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        jwt_config = JwtConfig(
            enabled=True,
            secret="super-secret-key-123456",
            access_expires_seconds=60,
            refresh_enabled=True,
            refresh_expires_seconds=3600,
            prefix="/auth/jwt",
        )
        session_config = SessionConfig(
            enabled=True,
            ttl_seconds=300,
            prefix="/auth/session",
        )

        cfg = AuthCoreConfig(jwt=jwt_config, session=session_config)

        FlaskAuthCore(app, cfg, UserService())
        self.client: FlaskClient = app.test_client()

    def test_jwt_flow(self):
        response_login = self.client.post(
            "/auth/jwt/login",
            json={"email": "example@example.com", "password": "password123"},
        )
        self.assertEqual(response_login.status_code, 200)
        data = response_login.get_json()
        
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]

        response_me = self.client.get(
            "/auth/jwt/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        self.assertEqual(response_me.status_code, 200)

        response_refresh = self.client.post(
            "/auth/jwt/refresh",
            json={"refresh_token": refresh_token},   # ✅ JSON body, not query param
        )
        self.assertEqual(response_refresh.status_code, 200)
        refreshed = response_refresh.get_json()
        
    def test_session_flow(self):

        response_login = self.client.post(
            "/auth/session/login",
            json={"email": "example@example.com", "password": "password123"},
        )
        self.assertEqual(response_login.status_code, 200)
        data = response_login.get_json()
        
        self.assertEqual(data["message"], "ok")

        sid_cookie = response_login.headers["Set-Cookie"]
        self.assertIn("sid=", sid_cookie)

        response_me = self.client.get(
            "/auth/session/me",
            headers={"Cookie": sid_cookie},
        )
        self.assertEqual(response_me.status_code, 200)

        response_refresh = self.client.post(
            "/auth/session/refresh",
            headers={"Cookie": sid_cookie},
        )
        self.assertEqual(response_refresh.status_code, 200)
        new_cookie = response_refresh.headers["Set-Cookie"]

        # 4. Session Logout
        response_logout = self.client.post(
            "/auth/session/logout",
            headers={"Cookie": new_cookie},
        )
        self.assertEqual(response_logout.status_code, 200)
        self.assertIn("sid=;", response_logout.headers["Set-Cookie"])  # cookie cleared


if __name__ == "__main__":
    unittest.main()
