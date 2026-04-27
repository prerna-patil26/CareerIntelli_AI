from datetime import datetime

from flask import Blueprint, request, jsonify, render_template, session

from app import db
from app.database.models import Interview

from app.modules.interview_engine.question_loader import QuestionLoader
from app.modules.interview_engine.question_selector import QuestionSelector
from app.modules.interview_engine.answer_evaluator import AnswerEvaluator
from app.modules.interview_engine.interview_scorer import InterviewScorer

# ✅ NEW IMPORTS
from app.modules.speech_analysis.filler_word_detector import FillerWordDetector
from app.modules.speech_analysis.speech_metrics import SpeechMetrics
from app.modules.vision_analysis.face_detector import FaceDetector
from app.modules.vision_analysis.engagement_tracker import EngagementTracker
from app.modules.vision_analysis.confidence_estimator import ConfidenceEstimator
from app.modules.ai_feedback.feedback_generator import FeedbackGenerator

# ✅ IMAGE PROCESSING
import base64
import numpy as np
import cv2


# ✅ IMAGE DECODE FUNCTION
def decode_image(image_data):
    image_data = image_data.split(",")[1]
    img_bytes = base64.b64decode(image_data)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return image


# ✅ OBJECTS
feedback_generator = FeedbackGenerator()

face_detector = FaceDetector()
engagement_tracker = EngagementTracker()
confidence_estimator = ConfidenceEstimator()

# ✅ FIXED BLUEPRINT
interview_bp = Blueprint("interview", __name__, url_prefix="/interview")

# ✅ Modules
loader = QuestionLoader()
df = loader.load_questions()

selector = QuestionSelector(df)
evaluator = AnswerEvaluator()
scorer = InterviewScorer()

filler_detector = FillerWordDetector()
speech_metrics = SpeechMetrics()


# -------------------------------
# 🆕 INTERVIEW PAGE
# -------------------------------
@interview_bp.route('/')
def interview_page():
    return render_template('interview_page.html')


# -------------------------------
# START INTERVIEW
# -------------------------------
@interview_bp.route('/start', methods=['POST'])
def start_interview():
    data = request.get_json()
    career = data.get('career')

    if not career:
        return jsonify({'error': 'Career is required'}), 400

    questions = selector.select_questions(career)

    # ✅ FIX 1: Store total questions in session for coverage penalty in submit
    session['total_questions'] = len(questions)

    return jsonify({
        "career": career,
        "total_questions": len(questions),
        "questions": questions
    })


# -------------------------------
# GET DOMAINS
# -------------------------------
@interview_bp.route('/domains', methods=['GET'])
def get_domains():
    domains = selector.get_available_domains()
    return jsonify({"domains": domains})


# -------------------------------
# RESULT PAGE
# -------------------------------
@interview_bp.route('/result')
def interview_result():
    return render_template('interview_result.html')


# -------------------------------
# SUBMIT ANSWERS (🔥 FIXED)
# -------------------------------
@interview_bp.route('/submit', methods=['POST'])
def submit_answers():
    print("🔥 SUBMIT STARTED")

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    image_data = data.get("image")
    answers = data.get("answers", [])

    if not answers:
        return jsonify({"error": "Answers required"}), 400

    scores = []
    total_fillers = 0
    total_words = 0

    for ans in answers:
        score = evaluator.evaluate_answer(ans)
        scores.append(score)

        try:
            fillers = filler_detector.detect_fillers(ans)
        except:
            fillers = 0

        total_fillers += fillers
        total_words += len(ans.split())

    # 🎯 MANUAL SCORE
    manual_score = scorer.calculate_score(scores)

    # 🔥 AI FEEDBACK (✅ FIXED HERE)
    try:
        combined_answers = "\n".join(answers)  # ⭐ IMPORTANT FIX
        ai_result = feedback_generator.generate_feedback(combined_answers)
        print("AI RESULT:", ai_result)
    except Exception as e:
        print("❌ Gemini ERROR:", e)
        ai_result = {
            "score": 5,
            "technical": "Basic understanding present but needs improvement.",
            "communication": "Clarity can be improved.",
            "confidence": "Moderate confidence.",
            "suggestions": [
                "Practice more",
                "Improve clarity",
                "Work on confidence"
            ]
        }

    # 🔥 AI SCORE
    try:
        ai_score = float(ai_result.get("score", 5))
    except:
        ai_score = 5

    # ✅ FIX 2: Apply coverage penalty — if user answered only 1 of 15 questions,
    # the score must reflect that, not just score the answers given
    total_questions = data.get("total_questions") or session.get("total_questions") or len(answers)
    coverage_ratio = len(answers) / total_questions
    penalized_manual_score = manual_score * coverage_ratio
    penalized_ai_score = ai_score * coverage_ratio

    final_score = round((penalized_manual_score * 0.6) + (penalized_ai_score * 10 * 0.4), 2)

    # 🎯 BREAKDOWN
    technical_score = round(final_score * 0.4, 2)

    # ✅ FIX 3: Communication score — pass answers + total_questions so it penalizes
    # low coverage. Old code used filler ratio which gave 90% for "hello" (0 fillers).
    meaningful_answers = [ans for ans in answers if len(ans.strip().split()) > 5]
    meaningful_ratio = len(meaningful_answers) / total_questions
    avg_word_count = total_words / len(answers) if answers else 0

    if avg_word_count > 20 and meaningful_ratio >= 0.7:
        communication_score = 8.0
    elif avg_word_count > 10 and meaningful_ratio >= 0.4:
        communication_score = 6.0
    elif avg_word_count > 5 and meaningful_ratio >= 0.2:
        communication_score = 4.0
    else:
        communication_score = 2.0

    # 🎥 FACE DETECTION
    if image_data:
        try:
            image = decode_image(image_data)
            faces = face_detector.detect_faces(image)
            face_position = face_detector.get_face_position(image, faces)
        except:
            face_position = "no_face"
    else:
        face_position = "no_face"

    # ⚠️ WARNING
    if face_position == "no_face":
        warning = "Face not detected. Please look at the camera."
    elif face_position in ["left", "right"]:
        warning = "Please keep your face centered."
    else:
        warning = ""

    # 🎯 CONFIDENCE — pass actual face position instead of hardcoded 1
    if face_position == "centered":
        engagement_input = 1.0
    elif face_position in ["left", "right"]:
        engagement_input = 0.5
    else:
        engagement_input = 0.0

    engagement_score = engagement_tracker.calculate_engagement(engagement_input)

    confidence_score = confidence_estimator.estimate_confidence(
        engagement_score,
        communication_score
    )

    # 🔥 FINAL FEEDBACK FORMAT
    feedback = (
        f"{ai_result.get('technical')}\n"
        f"{ai_result.get('communication')}\n"
        f"{ai_result.get('confidence')}"
    )

    suggestions = ai_result.get("suggestions", [])

    user_id = session.get("user_id")
    if user_id:
        try:
            interview_record = Interview(
                user_id=user_id,
                job_role=data.get("career") or data.get("role") or "Interview Practice",
                difficulty=data.get("difficulty"),
                score=float(final_score),
                duration_seconds=data.get("duration_seconds"),
                completed_at=datetime.utcnow(),
            )
            db.session.add(interview_record)
            db.session.commit()
        except Exception as db_error:
            db.session.rollback()
            print(f"Interview save failed: {db_error}")

    return jsonify({
        "total_score": float(final_score),
        "technical_score": float(technical_score),
        "communication_score": float(communication_score),
        "confidence_score": float(confidence_score),
        "feedback": feedback,
        "suggestions": suggestions,
        "warning": warning
    })


# -------------------------------
# REAL-TIME FACE CHECK
# -------------------------------
@interview_bp.route('/check-face', methods=['POST'])
def check_face():
    try:
        data = request.get_json()
        image_data = data.get("image")

        if image_data:
            image = decode_image(image_data)
            faces = face_detector.detect_faces(image)
            face_position = face_detector.get_face_position(image, faces)
        else:
            face_position = "no_face"

        if face_position == "no_face":
            warning = "Face not detected. Please look at the camera."
        elif face_position in ["left", "right"]:
            warning = "Please keep your face centered."
        else:
            warning = ""

        return jsonify({"warning": warning})

    except:
        return jsonify({"warning": ""})
