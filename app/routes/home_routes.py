from datetime import datetime, timedelta

from flask import Blueprint, render_template, session, redirect, url_for, request
from app.database.models import User, Profile, Resume, Interview
from flask import flash
from app import db   
home_bp = Blueprint("home", __name__)


def _normalize_skill(value):
    return " ".join(str(value).strip().lower().split())


def _dedupe_skills(values):
    seen = set()
    normalized = []
    for value in values or []:
        skill = _normalize_skill(value)
        if skill and skill not in seen:
            seen.add(skill)
            normalized.append(skill)
    return normalized


def _format_change(current, previous, label):
    delta = current - previous
    if delta > 0:
        return f"+{delta} {label}"
    if delta < 0:
        return f"{delta} {label}"
    if current > 0:
        return f"0 {label}"
    return f"No change {label}"


def _rank_role_matches(skills):
    user_skills = set(_dedupe_skills(skills))
    if not user_skills:
        return []

    try:
        from app.modules.roadmap.roadmap_data import get_all_roles, get_role_skills
    except Exception:
        return []

    ranked = []
    for role in get_all_roles():
        role_skills = _dedupe_skills(get_role_skills(role))
        if not role_skills:
            continue

        matched_skills = user_skills.intersection(role_skills)
        if not matched_skills:
            continue

        match_ratio = len(matched_skills) / len(role_skills)
        if len(matched_skills) >= 2 or match_ratio >= 0.25:
            ranked.append({
                "role": role,
                "matched_count": len(matched_skills),
                "match_ratio": match_ratio,
            })

    if not ranked:
        for role in get_all_roles():
            role_skills = _dedupe_skills(get_role_skills(role))
            matched_skills = user_skills.intersection(role_skills)
            if matched_skills:
                ranked.append({
                    "role": role,
                    "matched_count": len(matched_skills),
                    "match_ratio": len(matched_skills) / max(len(role_skills), 1),
                })

    ranked.sort(key=lambda item: (-item["match_ratio"], -item["matched_count"], item["role"]))
    return ranked[:5]


def _build_dashboard_metrics(user):
    profile = Profile.query.filter_by(user_id=user.id).first()
    resumes = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.asc()).all()
    interviews = Interview.query.filter_by(user_id=user.id).order_by(Interview.started_at.asc()).all()

    now = datetime.utcnow()
    week_start = now - timedelta(days=7)
    previous_week_start = now - timedelta(days=14)

    current_week_resumes = sum(1 for resume in resumes if resume.uploaded_at and resume.uploaded_at >= week_start)
    previous_week_resumes = sum(
        1
        for resume in resumes
        if resume.uploaded_at and previous_week_start <= resume.uploaded_at < week_start
    )

    current_week_interviews = sum(
        1
        for interview in interviews
        if (interview.completed_at or interview.started_at)
        and (interview.completed_at or interview.started_at) >= week_start
    )
    previous_week_interviews = sum(
        1
        for interview in interviews
        if (interview.completed_at or interview.started_at)
        and previous_week_start <= (interview.completed_at or interview.started_at) < week_start
    )

    current_resume_skills = []
    previous_resume_skills = []
    if resumes:
        current_resume_skills.extend(resumes[-1].skills or [])
        if len(resumes) > 1:
            previous_resume_skills.extend(resumes[-2].skills or [])

    current_profile_skills = profile.skills or [] if profile else []
    previous_profile_skills = current_profile_skills if current_profile_skills else []

    current_skills = _dedupe_skills([*current_profile_skills, *current_resume_skills])
    previous_skills = _dedupe_skills([*previous_profile_skills, *previous_resume_skills])

    current_role_matches = _rank_role_matches(current_skills)
    previous_role_matches = _rank_role_matches(previous_skills)

    uploaded_resume_count = len(resumes)
    practice_session_count = len(interviews)
    suggested_role_count = len(current_role_matches)

    weekly_snapshot_text = (
        f"{current_week_resumes} resume upload{'s' if current_week_resumes != 1 else ''}, "
        f"{suggested_role_count} suggested role{'s' if suggested_role_count != 1 else ''}, "
        f"and {current_week_interviews} practice session{'s' if current_week_interviews != 1 else ''} in the last 7 days."
    )

    return {
        "uploaded_resumes": {
            "value": uploaded_resume_count,
            "growth": _format_change(current_week_resumes, previous_week_resumes, "this week"),
        },
        "suggested_roles": {
            "value": suggested_role_count,
            "growth": _format_change(suggested_role_count, len(previous_role_matches), "vs last upload"),
        },
        "practice_sessions": {
            "value": practice_session_count,
            "growth": _format_change(current_week_interviews, previous_week_interviews, "this week"),
        },
        "weekly_snapshot": {
            "subtitle": weekly_snapshot_text,
        },
    }

@home_bp.route("/")
def index():
    return render_template("index.html")


@home_bp.route("/login")
def login_page():
    return render_template("login.html")


@home_bp.route("/register")
def register_page():
    return render_template("register.html")


# ---------------------------
# DASHBOARD
# ---------------------------
@home_bp.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("home.login_page"))

    user = User.query.get(session["user_id"])
    if not user:
        return redirect(url_for("home.login_page"))

    profile = Profile.query.filter_by(user_id=user.id).first()
    dashboard_metrics = _build_dashboard_metrics(user)

    return render_template(
        "dashboard.html",
        user=user,
        profile=profile,
        dashboard_metrics=dashboard_metrics,
        sidebar_active="dashboard"
    )


# ---------------------------
# RESUME UPLOAD (FIXED ✅)
# ---------------------------
@home_bp.route("/resume-upload", methods=["GET", "POST"])
def resume_upload():

    if request.method == "POST":
        file = request.files.get("resume")

        if file and file.filename != "":
            
            # 🔥 Yahan processing karo
            result = "Your resume is strong in Python but needs improvement in projects."

            # 👉 RESULT PAGE pe bhejo
            return render_template("resume_result.html", result=result)

    return render_template("resume_upload.html")




@home_bp.route("/api/profile/profile", methods=["GET", "POST"])
def profile():

    # ✅ LOGIN CHECK
    if "user_id" not in session:
        return redirect(url_for("home.login_page"))

    user = User.query.get(session["user_id"])

    if not user:
        return redirect(url_for("home.login_page"))

    # 🔥 GET PROFILE
    profile = Profile.query.filter_by(user_id=user.id).first()

    # =========================
    # POST (SAVE DATA)
    # =========================
    if request.method == "POST":

        # 👉 GET FORM DATA
        current_role = request.form.get("current_role")
        experience = request.form.get("experience")
        skills = request.form.get("skills")
        interests = request.form.get("interests")
        cgpa = request.form.get("cgpa")

        # 👉 CREATE PROFILE IF NOT EXISTS
        if not profile:
            profile = Profile(user_id=user.id)
            db.session.add(profile)

        # 👉 UPDATE VALUES
        profile.current_role = current_role
        profile.years_of_experience = experience
        profile.skills = skills.split(",") if skills else []
        profile.interests = interests.split(",") if interests else []
        profile.cgpa = cgpa

        db.session.commit()

        flash("Profile Updated Successfully ✅", "success")   # 🔥 ADD THIS

        return redirect(url_for("home.profile"))

    # =========================
    # GET (SHOW DATA)
    # =========================
    return render_template(
        "profile.html",
        user=user,
        profile=profile
    )
# ---------------------------
# OTHER ROUTES
# ---------------------------
@home_bp.route("/career-result")
def career_result():
    return render_template("career_result.html")


@home_bp.route("/interview")
def interview():
    return render_template("interview_page.html")


@home_bp.route("/report")
def report():
    return render_template("report.html")


@home_bp.route("/roadmap")
def roadmap():
    from app.modules.roadmap.roadmap_data import get_all_roles, get_all_skills

    roles = get_all_roles()
    skills = get_all_skills()
    return render_template("roadmap.html", roles=roles, skills=skills)