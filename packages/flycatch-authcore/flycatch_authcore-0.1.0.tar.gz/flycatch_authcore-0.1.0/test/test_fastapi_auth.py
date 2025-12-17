import unittest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from authcore import FastAPIAuthCore, AuthCoreConfig, JwtConfig, SessionConfig, UserRepository, Identity
import bcrypt


# ---- Fake User Repo ----
class UserService(UserRepository):
    async def get_by_email(self, email="example@example.com") -> Identity | None:
        if email == "example@example.com":
            # store hashed password for bcrypt check
            hashed = bcrypt.hashpw("password123".encode(), bcrypt.gensalt()).decode()
            return {"id": 1, "email": email, "password": hashed}
        return None

    async def verify_password(self, plain_password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), password_hash.encode())


# ---- Build FastAPI app with AuthCore ----
jwt_config = JwtConfig(
    enabled=True,
    secret="jwt-secret-long-enough",
    access_expires_seconds=3600,
    refresh_enabled=True,
    refresh_expires_seconds=3600 * 24,
    prefix="/auth/jwt"
)

session_config = SessionConfig(
    enabled=True,
    ttl_seconds=30 * 60,
    prefix="/auth/session"
)

authcore_config = AuthCoreConfig(jwt=jwt_config, session=session_config)

app = FastAPI()
auth = FastAPIAuthCore(app=app, cfg=authcore_config, repo=UserService())  # register routes


@app.get("/me")
async def get_user():
    # print("GET /me called")
    # auth = requests.headers.get("Authorization", "")
    # print("Auth header:", auth)
    return {"user": "message granded"}


client = TestClient(app)


class TestAuthCoreSession(unittest.TestCase):
    def test_session_login_and_me(self):
        """Test session login and /me flow"""  
        response = client.post(
            "/auth/session/login",
            json={"email": "example@example.com", "password": "password123"},
        )
        self.assertEqual(response.status_code, 200)
    
        cookies = response.cookies
        self.assertIn("sid", cookies)

        response_me = client.get("/auth/session/me", cookies=cookies)
        self.assertEqual(response_me.status_code, 200)
        data = response_me.json()
        self.assertIn("user", data)
        self.assertEqual(data["user"]["email"], "example@example.com")

    # def test_jwt_login_me_refresh(self):
    #     """Test JWT login, /me, and refresh flow"""
    #     # Login
    #     response = client.post(
    #         "/auth/jwt/login",
    #         json={"email": "example@example.com", "password": "password123"},
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     tokens = response.json()
    #     self.assertIn("access_token", tokens)
    #     self.assertIn("refresh_token", tokens)

    #     access_token = tokens["access_token"]
    #     refresh_token = tokens["refresh_token"]

    #     # /me with access token
    #     response_me = client.get(
    #         "/me",
    #         headers={"Authorization": f"Bearer {access_token}"},
    #     )
    #     self.assertEqual(response_me.status_code, 200)
    #     claims = response_me.json()["user"]
    #     self.assertIn("message granded", claims)
    #     # self.assertEqual(claims["email"], "example@example.com")

    #     # refresh token
    #     response_refresh = client.post(
    #         f"/auth/jwt/refresh?refresh_token={refresh_token}"
    #     )
    #     self.assertEqual(response_refresh.status_code, 200)
    #     refreshed = response_refresh.json()

    #     self.assertIn("access_token", refreshed)
    #     self.assertIn("refresh_token", refreshed)


if __name__ == "__main__":
    unittest.main()
