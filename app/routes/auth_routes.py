"""Authentication routes for CareerIntelli AI."""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from app.database.db import db
from app.database.models import User


# Create Blueprint
auth_bp = Blueprint("auth", __name__)


# ---------------------------------------------------
# LOGIN PAGE + LOGIN LOGIC
# ---------------------------------------------------

@auth_bp.route("/login", methods=["GET", "POST"])
def login_page():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        # Validation
        if not email or not password:
            return render_template("login.html", error="Email and password required")

        # Check user in database
        user = User.query.filter_by(email=email).first()

        if not user:
            return render_template("login.html", error="User not found")

        # 🔐 Secure password check
        if not check_password_hash(user.password_hash, password):
            return render_template("login.html", error="Invalid password")

        # ✅ Save session
        session["user_id"] = user.id

        # 🔥 Redirect to HOME dashboard (IMPORTANT FIX)
        return redirect(url_for("home.dashboard"))

    return render_template("login.html")


# ---------------------------------------------------
# REGISTER PAGE + REGISTER LOGIC
# ---------------------------------------------------

@auth_bp.route("/register", methods=["GET", "POST"])
def register_page():

    if request.method == "POST":

        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Validation
        if not email or not password:
            return render_template("register.html", error="Email and password required")

        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return render_template("register.html", error="User already exists")

        # 🔐 Hash password before storing
        hashed_password = generate_password_hash(password)

        # Create new user
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("auth.login_page"))

    return render_template("register.html")


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home.index"))   # ✅ change here

# ---------------------------------------------------
# API LOGIN
# ---------------------------------------------------

@auth_bp.route("/api/login", methods=["POST"])
def api_login():

    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid password"}), 401

        return jsonify({
            "message": "Login successful",
            "user_id": user.id,
            "email": user.email
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------
# API REGISTER
# ---------------------------------------------------

@auth_bp.route("/api/register", methods=["POST"])
def api_register():

    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return jsonify({"error": "User already exists"}), 409

        hashed_password = generate_password_hash(password)

        new_user = User(
            email=email,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message": "User registered successfully"
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------
# API LOGOUT
# ---------------------------------------------------

@auth_bp.route("/api/logout", methods=["POST"])
def api_logout():

    session.clear()

    return jsonify({
        "message": "Logout successful"
    }), 200