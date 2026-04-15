"""Shared chatbot API routes for CareerIntelli AI."""

from flask import Blueprint, jsonify, request

from app.modules.chatbot.chatbot_service import generate_chatbot_reply


chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/api/chatbot")


@chatbot_bp.route("/respond", methods=["POST"])
def respond_chatbot():
    """Return a page-aware chatbot reply without exposing the API key in the browser."""
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    page = (data.get("page") or "general").strip()

    if not message:
        return jsonify({"success": False, "error": "message is required"}), 400

    reply = generate_chatbot_reply(message=message, page=page)
    return jsonify({"success": True, "reply": reply, "page": page or "general"}), 200
