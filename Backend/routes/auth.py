"""
Auth Routes - Register/login endpoints
"""

from flask import Blueprint, jsonify, request

from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json() or {}
        email = (data.get("email") or "").strip().lower()
        password = (data.get("password") or "").strip()
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required"}), 400
        if len(password) < 6:
            return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400
        result = auth_service.register(email, password)
        return jsonify({"success": True, **result}), 201
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 400
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    try:
        data = request.get_json() or {}
        email = (data.get("email") or "").strip().lower()
        password = (data.get("password") or "").strip()
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required"}), 400
        result = auth_service.login(email, password)
        return jsonify({"success": True, **result}), 200
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 401
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500
