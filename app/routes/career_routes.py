"""Career page routes and career prediction API routes."""

from __future__ import annotations

import sys
from typing import List, Optional

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

career_routes = Blueprint("career_routes", __name__)
career_api_routes = Blueprint("career_api_routes", __name__, url_prefix="/api/career")

_predictor: Optional[object] = None


def get_predictor():
    """Get or create CareerPredictor instance with lazy loading."""
    global _predictor
    if _predictor is None:
        try:
            from app.modules.career_prediction.career_predictor import CareerPredictor
            _predictor = CareerPredictor()
        except FileNotFoundError as e:
            print(f"⚠️  Warning: CareerPredictor models not found: {e}")
            _predictor = None
        except Exception as e:
            print(f"⚠️  Warning: Failed to load CareerPredictor: {e}")
            _predictor = None
    return _predictor


def _validate_skills_payload(payload: dict) -> List[str]:
    """Validate and clean skills from request payload."""
    skills = payload.get("skills")

    if skills is None:
        raise ValueError("'skills' field is required.")

    if not isinstance(skills, list):
        raise ValueError("'skills' must be a list of strings.")

    if not skills:
        raise ValueError("'skills' cannot be empty.")

    cleaned_skills = [str(skill).strip() for skill in skills if str(skill).strip()]

    if not cleaned_skills:
        raise ValueError("'skills' must contain valid values.")

    return cleaned_skills


def _extract_target_career(payload: dict) -> str | None:
    """Read optional target career selection from request payload."""
    target_career = payload.get("target_career")
    if target_career is None:
        return None

    cleaned = str(target_career).strip()
    return cleaned or None


def _extract_skill_ratings(payload: dict) -> dict:
    """Read optional per-skill ratings from request payload."""
    ratings = payload.get("ratings", {})
    if not isinstance(ratings, dict):
        return {}

    cleaned_ratings = {}
    for skill, value in ratings.items():
        skill_name = str(skill).strip()
        if not skill_name:
            continue
        try:
            cleaned_ratings[skill_name] = max(1, min(5, int(value)))
        except (TypeError, ValueError):
            continue
    return cleaned_ratings


# ================= HTML ROUTES =================

@career_routes.route("/")
def home_page() -> str:
    """Render the dashboard page."""
    return render_template("dashboard.html")


@career_routes.route("/dashboard")
def dashboard() -> str:
    """Render the dashboard page (alias)."""
    return render_template("dashboard.html")


@career_routes.route("/career-prediction")
def career_prediction_page() -> str:
    """Render the career prediction input page."""
    try:
        return render_template("career.html")
    except Exception as e:
        return f'<h1>Error</h1><p>Error loading career.html: {str(e)}</p>', 500


@career_routes.route("/career-result")
def career_result_page() -> str:
    """Render the career prediction result page."""
    return render_template("career_result.html")


@career_routes.route("/profile")
def profile_page() -> str:
    """Render the user profile page."""
    user_data = {
        "username": session.get("username", "User"),
        "email": session.get("email", "user@example.com"),
        "skills": session.get("skills", [])
    }
    return render_template("profile_form.html", user=user_data)


@career_routes.route("/resume")
def resume_page() -> str:
    """Render the resume upload page."""
    return render_template("resume_upload.html")


@career_routes.route("/interview")
def interview_page() -> str:
    """Render the interview preparation page."""
    return render_template("interview_page.html")


@career_routes.route("/reports")
def reports_page() -> str:
    """Render the reports page."""
    return render_template("report.html")


@career_routes.route("/skills")
def skill_showcase_page() -> str:
    """Render the skill showcase page."""
    return render_template("skill_showcase.html")


@career_routes.route("/ai-coach")
def ai_coach_page() -> str:
    """Render the AI coach chatbot page."""
    return render_template("ai_coach.html")


@career_routes.route("/analytics")
def analytics_page() -> str:
    """Render the analytics and reports page."""
    return render_template("analytics.html")


@career_routes.route("/logout")
def logout() -> tuple:
    """Handle user logout."""
    session.clear()
    return redirect(url_for('career_routes.home_page'))


# ================= API =================

@career_api_routes.route("/predict-career", methods=["POST"])
def predict_career() -> tuple:
    """
    Predict career based on provided skills.

    Expected JSON payload:
    {
        "skills": ["python", "machine learning", "data analysis"]
    }

    Returns:
        JSON response with career prediction or error message.
    """
    try:
        payload = request.get_json(silent=True)

        if payload is None:
            return jsonify({"error": "Invalid JSON body"}), 400

        skills = _validate_skills_payload(payload)

        target_career = _extract_target_career(payload)

        skill_ratings = _extract_skill_ratings(payload)

        predictor = get_predictor()
        response = predictor.predict_career_with_details(
            skills,
            top_k=3,
            target_career=target_career,
            skill_ratings=skill_ratings,
        )

        session["latest_prediction"] = response

        return jsonify(response), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


@career_routes.route("/api/career/get-prediction", methods=["GET"])
def get_latest_prediction() -> tuple:
    """Get the latest prediction from session."""
    prediction = session.get("latest_prediction")
    if prediction is None:
        return jsonify({"error": "No prediction available"}), 404
    return jsonify(prediction), 200
