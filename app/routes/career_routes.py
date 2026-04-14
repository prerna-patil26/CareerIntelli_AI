"""Career prediction routes for CareerIntelli AI."""

from flask import request, jsonify, render_template
from . import career_bp
from app.modules.career_prediction.career_predictor import CareerPredictor


# ---------------------------------------------------
# UI ROUTE (Career Prediction Page)
# ---------------------------------------------------

@career_bp.route('/career', methods=['GET'])
def career_page():
    """Render career prediction page."""
    return render_template("career_result.html")


# ---------------------------------------------------
# API: Career Prediction
# ---------------------------------------------------

@career_bp.route('/predict', methods=['POST'])
def predict_career():
    """Predict suitable career paths for user."""

    try:

        data = request.get_json()

        user_skills = data.get('skills', [])
        experience = data.get('experience', 0)
        education = data.get('education', '')

        if not user_skills:
            return jsonify({'error': 'Skills are required'}), 400

        predictor = CareerPredictor()

        # Future ML prediction logic
        # result = predictor.predict(user_skills, experience, education)

        return jsonify({
            'predicted_careers': [],
            'confidence_scores': []
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------
# API: Career Roadmap
# ---------------------------------------------------

@career_bp.route('/roadmap', methods=['POST'])
def generate_roadmap():
    """Generate career development roadmap."""

    try:

        data = request.get_json()

        current_role = data.get('current_role')
        target_role = data.get('target_role')

        if not current_role or not target_role:
            return jsonify({'error': 'Current and target roles are required'}), 400

        return jsonify({
            'roadmap': [],
            'timeline': 0
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------
# API: Career Recommendations
# ---------------------------------------------------

@career_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get career recommendations."""

    try:

        return jsonify({
            'recommendations': []
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500