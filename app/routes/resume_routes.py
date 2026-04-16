"""Resume processing routes for CareerIntelli AI."""

import os
import logging
from flask import request, render_template, redirect, url_for, session, make_response
from werkzeug.utils import secure_filename

from . import resume_bp

from app.modules.resume_analysis.parser import ResumeParser
from app.modules.resume_analysis.skill_extractor import SkillExtractor
from app.modules.resume_analysis.resume_scorer import ResumeScorer
from app.modules.resume_analysis.skill_gap_analysis import SkillGapAnalyzer
from app.modules.ai.feedback import FeedbackGenerator

logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join("app", "static", "uploads", "resumes")
ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Default target role for gap analysis
DEFAULT_TARGET_ROLE = "data scientist"


def allowed_file(filename: str) -> bool:
    """
    Check if file extension is allowed.
    
    Args:
        filename: Name of uploaded file
        
    Returns:
        True if file extension is in ALLOWED_EXTENSIONS
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file(file) -> tuple:
    """
    Validate uploaded file for size and format.
    
    Args:
        file: Flask file object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    if file.filename == "":
        return False, "No file selected"
    
    if not allowed_file(file.filename):
        return False, "Only PDF or DOCX files are allowed"
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size is 5MB, your file is {file_size / (1024*1024):.1f}MB"
    
    if file_size == 0:
        return False, "File is empty"
    
    return True, None


# ---------------------------
# UI PAGE
# ---------------------------
@resume_bp.route("/resume", methods=["GET"])
def resume_page():
    """Display resume upload page."""
    # result = session.pop("resume_result", None)
    result = session.get("resume_result")
    response = make_response(render_template("resume_upload.html", result=result))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# ---------------------------
# UPLOAD + ANALYZE
# ---------------------------
@resume_bp.route("/resume/upload", methods=["POST"])
def upload_resume():
    """
    Upload and analyze resume with comprehensive feedback.
    Provides: ATS score, skills extraction, gap analysis, and AI feedback.
    """
    try:
        # ---------- FILE VALIDATION ----------
        file = request.files.get("file") or request.files.get("resume")
        if not file:
            logger.warning("Resume upload attempt with no file provided")
            return render_template("resume_upload.html", error="No file provided")

        is_valid, error_msg = validate_file(file)
        
        if not is_valid:
            logger.warning(f"File validation failed: {error_msg}")
            return render_template("resume_upload.html", error=error_msg)

        # ---------- SAVE FILE ----------
        try:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            logger.info(f"Resume file saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save resume file: {e}")
            return render_template(
                "resume_upload.html", 
                error="Failed to save file. Please try again."
            )

        # ---------- PARSE RESUME ----------
        try:
            parser = ResumeParser()
            parsed_data = parser.parse(filepath)
            resume_text = parsed_data.get("text", "")
            
            logger.info(f"Resume parsed successfully. Length: {len(resume_text)} chars")
        except ValueError as e:
            logger.error(f"Resume parsing error: {e}")
            return render_template(
                "resume_upload.html",
                error=f"Failed to parse resume: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during parsing: {e}")
            return render_template(
                "resume_upload.html",
                error="Unexpected error while parsing resume. Please try again."
            )

        # ---------- EXTRACT SKILLS ----------
       # ---------- EXTRACT SKILLS ----------
        try:
            skill_extractor = SkillExtractor()

            # Get skill scores (dict)
            skill_scores = skill_extractor.extract_technical_skills_with_score(resume_text)

            # Convert to list (IMPORTANT for ATS scoring)
            technical_skills = list(skill_scores.keys())

            # Soft skills
            soft_skills = skill_extractor.extract_soft_skills(resume_text)

            # Save BOTH
            parsed_data["skills"] = technical_skills      # for ATS scoring
            parsed_data["skill_scores"] = skill_scores    # for UI strength
            parsed_data["soft_skills"] = soft_skills

            logger.info(f"Extracted {len(technical_skills)} technical skills, {len(soft_skills)} soft skills")

        except Exception as e:
            logger.error(f"Skill extraction error: {e}")
            parsed_data["skills"] = []
            parsed_data["skill_scores"] = {}
            parsed_data["soft_skills"] = []
        # ---------- SCORE RESUME ----------
        try:
            scorer = ResumeScorer()
            score_result = scorer.score_resume(
                parsed_data, 
                target_role=DEFAULT_TARGET_ROLE
            )
            logger.info(f"Resume scored: {score_result['percentage']}%")
        except Exception as e:
            logger.error(f"Resume scoring error: {e}")
            score_result = {
                "overall_score": 0,
                "percentage": 0,
                "breakdown": {},
                "suggestions": ["Error in scoring. Please try again."],
                "relevance_scores": {},
            }

        # ---------- ANALYZE SKILL GAP ----------
        try:
            gap_analyzer = SkillGapAnalyzer()
            gap_result = gap_analyzer.analyze_gap(
                user_skills=technical_skills,
                target_role=DEFAULT_TARGET_ROLE
            )
            gap_result["missing_skills"].sort()
            
            logger.info(
                f"Skill gap analysis: {gap_result['coverage_percentage']}% coverage, "
                f"{len(gap_result['missing_skills'])} missing skills"
            )
        except Exception as e:
            logger.error(f"Skill gap analysis error: {e}")
            gap_result = {
                "target_role": DEFAULT_TARGET_ROLE,
                "matched_skills": [],
                "missing_skills": [],
                "extra_skills": [],
                "coverage_percentage": 0,
                "gap_percentage": 100,
            }

        # ---------- AI FEEDBACK ----------
        ai_feedback = []
        try:
            feedback_gen = FeedbackGenerator()
            ai_feedback = feedback_gen.get_ai_resume_feedback(resume_text)
            
            logger.info(f"AI feedback generated: {len(ai_feedback)} suggestions")
        except Exception as e:
            logger.error(f"AI feedback error: {e}")
            # Don't crash if AI fails - it's optional
            ai_feedback = ["AI feedback temporarily unavailable."]

        # Determine whether to show basic suggestions when AI feedback is available
        show_basic_suggestions = True
        if ai_feedback and not (
            len(ai_feedback) == 1 and ai_feedback[0].lower().startswith("ai ")
        ):
            show_basic_suggestions = False

        # ---------- COMPILE RESULTS ----------
        result = {
            "filename": filename,
            "parsed_data": parsed_data,
            "resume_score": score_result,
            "skill_gap": gap_result,
            "ai_feedback": ai_feedback,
            "target_role": DEFAULT_TARGET_ROLE,
            "show_basic_suggestions": show_basic_suggestions,
        }

        session["resume_result"] = result
        logger.info("Resume analysis completed successfully")
        return render_template("resume_result.html", result=result)

    except Exception as e:
        logger.error(f"Unexpected error in resume upload: {e}", exc_info=True)
        return render_template(
            "resume_upload.html",
            error="An unexpected error occurred. Please try again later."
        )
    
@resume_bp.route("/resume/result")
def resume_result():
    result = session.get("resume_result")

    if not result:
        return redirect(url_for("resume.resume_page"))

    return redirect(url_for("resume.resume_result"))