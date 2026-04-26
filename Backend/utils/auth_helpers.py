"""
Auth helpers for extracting current user from bearer token
"""

from typing import Dict
from flask import request

from services.auth_service import AuthService

auth_service = AuthService()


def get_current_user_or_raise() -> Dict:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise PermissionError("Missing or invalid Authorization header")
    token = auth_header.replace("Bearer ", "", 1).strip()
    payload = auth_service.verify_token(token)
    if not payload:
        raise PermissionError("Invalid or expired token")
    return payload
