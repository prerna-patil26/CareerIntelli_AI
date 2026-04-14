from flask import Blueprint, render_template, session, redirect, url_for, request
from app.database.models import User

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home():
    return render_template("login.html")


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

    return render_template("dashboard.html", user=user)


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