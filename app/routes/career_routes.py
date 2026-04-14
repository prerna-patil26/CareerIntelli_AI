"""Career page routes and career prediction API routes."""

from __future__ import annotations
from flask_login import current_user
from typing import Dict, List, Optional

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for


# Keep the blueprint name as ``career_routes`` so existing ``url_for`` calls keep working.
career_bp = Blueprint("career_routes", __name__)
career_routes = career_bp

_predictor: Optional[object] = None


def get_predictor():
    """Get or create CareerPredictor instance with lazy loading."""
    global _predictor
    if _predictor is None:
        try:
            from app.modules.career_prediction.career_predictor import CareerPredictor

            _predictor = CareerPredictor()
        except FileNotFoundError as error:
            print(f"Warning: CareerPredictor models not found: {error}")
            _predictor = None
        except Exception as error:
            print(f"Warning: Failed to load CareerPredictor: {error}")
            _predictor = None
    return _predictor


def _validate_skills_payload(payload: dict) -> List[str]:
    """Validate and clean skills from request payload."""
    skills = payload.get("skills")

    if skills is None:
        raise ValueError("'skills' field is required.")

    if not isinstance(skills, list):
        raise ValueError("'skills' must be a list of strings.")

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


def _extract_skill_ratings(payload: dict) -> Dict[str, int]:
    """Read optional per-skill ratings from request payload."""
    ratings = payload.get("ratings", {})
    if not isinstance(ratings, dict):
        return {}

    cleaned_ratings: Dict[str, int] = {}
    for skill, value in ratings.items():
        skill_name = str(skill).strip()
        if not skill_name:
            continue
        try:
            cleaned_ratings[skill_name] = max(1, min(5, int(value)))
        except (TypeError, ValueError):
            continue
    return cleaned_ratings


def _predict_career(payload: dict) -> tuple:
    """Run the career predictor and return a JSON response tuple."""
    skills = _validate_skills_payload(payload)
    target_career = _extract_target_career(payload)
    skill_ratings = _extract_skill_ratings(payload)

    predictor = get_predictor()
    if predictor is None:
        return jsonify({"error": "Career prediction model is not available."}), 503

    response = predictor.predict_career_with_details(
        skills,
        top_k=3,
        target_career=target_career,
        skill_ratings=skill_ratings,
    )
    session["latest_prediction"] = response
    return jsonify(response), 200


@career_bp.route("/career")
def career_page():
    """Render the career prediction page."""
    return render_template("career.html", user=current_user)


@career_bp.route("/dashboard")
def dashboard():
    """Render the dashboard page."""
    # return render_template("dashboard.html")
    return render_template("dashboard.html", user=current_user)


@career_bp.route("/career-prediction")
def career_prediction_page():
    """Render the career prediction input page."""
    return render_template("career.html", user=current_user)


@career_bp.route("/career-result")
def career_result_page():
    """Render the career prediction result page."""
    return render_template("career_result.html", user=current_user)


@career_bp.route("/profile")
def profile_page():
    """Render the user profile page."""
    user_data = {
        "username": session.get("username", "User"),
        "email": session.get("email", "user@example.com"),
        "skills": session.get("skills", []),
    }
    return render_template("profile_form.html", user=user_data)


@career_bp.route("/resume")
def resume_page():
    """Render the resume upload page."""
    return render_template("resume_upload.html")


@career_bp.route("/interview")
def interview_page():
    """Render the interview preparation page."""
    return render_template("interview_page.html")


@career_bp.route("/reports")
def reports_page():
    """Render the reports page."""
    return render_template("report.html")


@career_bp.route("/skills")
def skill_showcase_page():
    """Render the skill showcase page."""
    return render_template("skill_showcase.html")


@career_bp.route("/ai-coach")
def ai_coach_page():
    """Render the AI coach chatbot page."""
    return render_template("ai_coach.html")


@career_bp.route("/analytics")
def analytics_page():
    """Render the analytics and reports page."""
    return render_template("analytics.html")


@career_bp.route("/logout")
def logout():
    """Handle user logout."""
    session.clear()
    return redirect(url_for("career_routes.career_page"))


@career_bp.route("/api/career/predict-career", methods=["POST"])
@career_bp.route("/api/career/predict", methods=["POST"])
def predict_career():
    """Predict suitable career paths for user."""
    try:
        payload = request.get_json(silent=True)
        if payload is None:
            return jsonify({"error": "Invalid JSON body"}), 400
        return _predict_career(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        return jsonify({"error": f"Prediction failed: {error}"}), 500


@career_bp.route("/api/career/get-prediction", methods=["GET"])
def get_latest_prediction():
    """Get the latest prediction from session."""
    prediction = session.get("latest_prediction")
    if prediction is None:
        return jsonify({"error": "No prediction available"}), 404
    return jsonify(prediction), 200


@career_bp.route("/api/career/recommendations", methods=["GET"])
def get_recommendations():
    """Return the latest predicted careers when available."""
    prediction = session.get("latest_prediction")
    if prediction is None:
        return jsonify({"recommendations": []}), 200
    return jsonify({"recommendations": prediction.get("top_careers", [])}), 200
