"""
Report Routes - Save/list/fetch report data and medicine details
"""

from flask import Blueprint, jsonify, request

from services.report_service import ReportService
from services.medicine_service import MedicineService
from utils.auth_helpers import get_current_user_or_raise

reports_bp = Blueprint("reports", __name__)
report_service = ReportService()
medicine_service = MedicineService()


@reports_bp.route("/reports", methods=["GET"])
def list_reports():
    try:
        user = get_current_user_or_raise()
        reports = report_service.list_reports(user["user_id"])
        return jsonify({"success": True, "reports": reports}), 200
    except PermissionError as error:
        return jsonify({"success": False, "error": str(error)}), 401
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500


@reports_bp.route("/reports/<int:report_id>", methods=["GET"])
def get_report(report_id: int):
    try:
        user = get_current_user_or_raise()
        report = report_service.get_report(user["user_id"], report_id)
        if not report:
            return jsonify({"success": False, "error": "Report not found"}), 404
        return jsonify({"success": True, "report": report}), 200
    except PermissionError as error:
        return jsonify({"success": False, "error": str(error)}), 401
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500


@reports_bp.route("/medicines/<string:name>", methods=["GET"])
def get_medicine(name: str):
    try:
        _ = get_current_user_or_raise()
        details = medicine_service.get_medicine_details(name)
        alternatives = medicine_service.get_alternative_medicines(name)
        return jsonify(
            {
                "success": True,
                "medicine": details,
                "alternatives": alternatives,
            }
        ), 200
    except PermissionError as error:
        return jsonify({"success": False, "error": str(error)}), 401
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500
