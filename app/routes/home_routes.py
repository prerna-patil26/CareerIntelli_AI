from flask import Blueprint, render_template, session, redirect, url_for, request
from app.database.models import User, Profile
from flask import flash
home_bp = Blueprint("home", __name__)

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

    return render_template(
        "dashboard.html",
        user=user,
        profile=profile,
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
            filename = file.filename

            # 👉 TEMP: just test upload
            return f"Uploaded successfully: {filename}"

        return "No file selected"

    return render_template("resume_upload.html")


from app import db   # 🔥 ADD THIS IMPORT

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