"""
Auth Service - User account registration/login and token verification
"""

from typing import Optional, Dict, Any
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from services.storage_service import StorageService


class AuthService:
    """Account auth helper built on signed bearer tokens."""

    def __init__(self):
        self.storage = StorageService()
        self.serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

    def register(self, email: str, password: str) -> Dict[str, Any]:
        existing = self.storage.fetch_one("SELECT id FROM users WHERE email = ?", (email.lower(),))
        if existing:
            raise ValueError("Email already registered")
        user_id = self.storage.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (email.lower(), generate_password_hash(password), self.storage.now()),
        )
        token = self._create_token(user_id, email.lower())
        return {"user_id": user_id, "email": email.lower(), "token": token}

    def login(self, email: str, password: str) -> Dict[str, Any]:
        user = self.storage.fetch_one("SELECT * FROM users WHERE email = ?", (email.lower(),))
        if not user or not check_password_hash(user["password_hash"], password):
            raise ValueError("Invalid email or password")
        token = self._create_token(user["id"], user["email"])
        return {"user_id": user["id"], "email": user["email"], "token": token}

    def _create_token(self, user_id: int, email: str) -> str:
        return self.serializer.dumps({"user_id": user_id, "email": email}, salt="auth-token")

    def verify_token(self, token: str, max_age_seconds: int = 60 * 60 * 24 * 7) -> Optional[Dict[str, Any]]:
        try:
            payload = self.serializer.loads(token, salt="auth-token", max_age=max_age_seconds)
            return payload
        except (BadSignature, SignatureExpired):
            return None
