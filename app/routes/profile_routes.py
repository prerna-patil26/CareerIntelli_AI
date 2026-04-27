"""User profile routes for CareerIntelli AI."""

from fileinput import filename
import os
from werkzeug.utils import secure_filename

from flask import request, jsonify, render_template, redirect, url_for, session

from . import profile_bp

from app.database.db import db
from app.database.models import User, Profile


# Upload folders
UPLOAD_PROFILE_PHOTO = "app/static/uploads/profile_photos"
UPLOAD_RESUME = os.path.join("static", "uploads", "resumes")


# ---------------------------------------------------
# PROFILE PAGE
# ---------------------------------------------------

@profile_bp.route("/profile")
def profile_page():
    """Show user profile."""

    if "user_id" not in session:
        return redirect(url_for("home.login_page"))

    user = User.query.get(session["user_id"])

    if not user:
        return redirect(url_for("home.login_page"))

    profile = Profile.query.filter_by(user_id=user.id).first()

    if not profile:
        profile = Profile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

    return render_template(
        "profile_form.html",
        user=user,
        profile=profile
    )


# ---------------------------------------------------
# UPDATE PROFILE
# ---------------------------------------------------

@profile_bp.route("/update", methods=["POST"])
def update_profile():

    try:

        if "user_id" not in session:
            return redirect(url_for("home.login_page"))

        user = User.query.get(session["user_id"])

        if not user:
            return redirect(url_for("home.login_page"))

        profile = Profile.query.filter_by(user_id=user.id).first()

        if not profile:
            profile = Profile(user_id=user.id)
            db.session.add(profile)

        # -----------------------------
        # FORM DATA
        # -----------------------------

        current_role = request.form.get("current_role")
        experience = request.form.get("experience")
        skills = request.form.get("skills")
        interests = request.form.get("interests")
        cgpa = request.form.get("cgpa")

        # -----------------------------
        # UPDATE PROFILE DATA
        # -----------------------------

        profile.current_role = current_role

        if experience:
            profile.years_of_experience = int(experience)

        if cgpa:
            cgpa = float(cgpa)

            if cgpa < 0 or cgpa > 10:
                return jsonify({"error": "CGPA must be between 0 and 10"}), 400

            profile.cgpa = cgpa

        # Skills list
        profile.skills = [s.strip() for s in skills.split(",")] if skills else []

        # Interests list
        profile.interests = [i.strip() for i in interests.split(",")] if interests else []

        # -----------------------------
        # PROFILE PHOTO UPLOAD
        # -----------------------------

        photo = request.files.get("profile_photo")

        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)

            os.makedirs(UPLOAD_PROFILE_PHOTO, exist_ok=True)

            path = os.path.join(UPLOAD_PROFILE_PHOTO, filename)
            photo.save(path)

            profile.profile_photo = "uploads/profile_photos/" + filename

        # -----------------------------
        # RESUME UPLOAD
        # -----------------------------

        resume = request.files.get("resume")

        if resume and resume.filename != "":
            filename = secure_filename(resume.filename)

            os.makedirs(UPLOAD_RESUME, exist_ok=True)

            path = os.path.join(UPLOAD_RESUME, filename)
            resume.save(path)

            profile.resume_file = f"uploads/resumes/{filename}"

        db.session.commit()

        return redirect(url_for("profile.profile_page", _external=True))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------
# GET PROFILE API
# ---------------------------------------------------

@profile_bp.route("/get", methods=["GET"])
def get_profile():

    try:

        if "user_id" not in session:
            return jsonify({"error": "Not logged in"}), 401

        user = User.query.get(session["user_id"])

        if not user:
            return jsonify({"error": "User not found"}), 404

        profile = Profile.query.filter_by(user_id=user.id).first()

        if not profile:
            return jsonify({"profile": {}})

        return jsonify({

            "name": f"{user.first_name} {user.last_name}",
            "email": user.email,

            "current_role": profile.current_role,
            "experience": profile.years_of_experience,
            "skills": profile.skills,
            "interests": profile.interests,
            "cgpa": profile.cgpa,

            "profile_photo": profile.profile_photo,
            "resume": profile.resume_file

        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500