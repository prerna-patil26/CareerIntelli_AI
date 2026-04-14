from flask import Blueprint, request, jsonify, render_template

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

# ✅ Blueprint
interview_bp = Blueprint("interview", __name__)

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
@interview_bp.route('/interview-page')
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
# SUBMIT ANSWERS (FINAL)
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

    print("SUBMIT API HIT")

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

    # 🔥 GEMINI AI
    print("👉 Before AI call")

    try:
        ai_result = feedback_generator.generate_feedback(answers)

        if not isinstance(ai_result, dict):
            raise Exception("Invalid AI response")

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

    print("👉 After AI call")

    # 🔥 AI SCORE
    try:
        ai_score = float(ai_result.get("score", 5))
    except:
        ai_score = 5

    # 🔥 FINAL SCORE
    final_score = round((manual_score * 0.6) + (ai_score * 10 * 0.4), 2)

    # 🎯 BREAKDOWN
    technical_score = round(final_score * 0.4, 2)

    communication_score = speech_metrics.calculate_communication_score(
        total_fillers, total_words
    )

    # 🎥 FACE DETECTION
    if image_data:
        try:
            image = decode_image(image_data)
            faces = face_detector.detect_faces(image)
            face_count = len(faces)
            face_position = face_detector.get_face_position(image, faces)
        except Exception as e:
            print("FACE ERROR:", e)
            face_count = 0
            face_position = "no_face"
    else:
        face_count = 0
        face_position = "no_face"

    # ⚠️ WARNING
    if face_position == "no_face":
        warning = "Face not detected. Please look at the camera."
    elif face_position in ["left", "right"]:
        warning = "Please keep your face centered."
    else:
        warning = ""

    # 🎯 ENGAGEMENT
    engagement_score = engagement_tracker.calculate_engagement(face_count)

    # 🎯 CONFIDENCE
    confidence_score = confidence_estimator.estimate_confidence(
        engagement_score,
        communication_score
    )

    if face_position == "center":
        confidence_score += 5
    elif face_position in ["left", "right"]:
        confidence_score -= 5
    elif face_position == "no_face":
        confidence_score -= 15

    confidence_score = max(0, min(100, confidence_score))

    # 🔥 FINAL FEEDBACK
    feedback = (
        f"Technical: {ai_result.get('technical')}\n"
        f"Communication: {ai_result.get('communication')}\n"
        f"Confidence: {ai_result.get('confidence')}"
    )

    suggestions = ai_result.get("suggestions", [])

    print("RETURN SUCCESS")

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

    except Exception as e:
        print("FACE ERROR:", e)
        return jsonify({"warning": ""})