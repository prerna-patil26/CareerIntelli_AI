"""Database models for CareerIntelli AI."""

from app.database.db import db
from datetime import datetime


# ---------------------------------------------------
# USER MODEL
# ---------------------------------------------------

class User(db.Model):
    """User model for authentication and profile management."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    profile = db.relationship(
        "Profile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    resumes = db.relationship(
        "Resume",
        backref="user",
        cascade="all, delete-orphan"
    )

    interviews = db.relationship(
        "Interview",
        backref="user",
        cascade="all, delete-orphan"
    )

    reports = db.relationship(
        "Report",
        backref="user",
        cascade="all, delete-orphan"
    )

    # 🔥 AUTO CREATE PROFILE (NEW)
    def create_profile(self):
        if not self.profile:
            profile = Profile(user_id=self.id)
            db.session.add(profile)
            db.session.commit()

    def __repr__(self):
        return f"<User {self.email}>"


# ---------------------------------------------------
# PROFILE MODEL
# ---------------------------------------------------

class Profile(db.Model):
    """User profile model."""

    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Career fields
    current_role = db.Column(db.String(100))
    years_of_experience = db.Column(db.Integer)
    cgpa = db.Column(db.Float)

    # Skills and interests
    skills = db.Column(db.JSON, default=list)
    interests = db.Column(db.JSON, default=list)

    # Uploads
    profile_photo = db.Column(db.String(255))
    resume_file = db.Column(db.String(255))

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Profile User {self.user_id}>"


# ---------------------------------------------------
# RESUME MODEL
# ---------------------------------------------------

class Resume(db.Model):
    """Resume storage model."""

    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    file_path = db.Column(db.String(255))
    score = db.Column(db.Float)

    skills = db.Column(db.JSON, default=list)
    experience = db.Column(db.JSON, default=list)
    education = db.Column(db.JSON, default=list)

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Resume {self.id}>"


# ---------------------------------------------------
# INTERVIEW MODEL
# ---------------------------------------------------

class Interview(db.Model):
    """Interview session model."""

    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    job_role = db.Column(db.String(100))
    difficulty = db.Column(db.String(20))
    score = db.Column(db.Float)
    duration_seconds = db.Column(db.Integer)

    started_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    completed_at = db.Column(db.DateTime)

    answers = db.relationship(
        "InterviewAnswer",
        backref="interview",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Interview {self.id}>"


# ---------------------------------------------------
# INTERVIEW ANSWER MODEL
# ---------------------------------------------------

class InterviewAnswer(db.Model):
    """Interview answer model."""

    __tablename__ = "interview_answers"

    id = db.Column(db.Integer, primary_key=True)

    interview_id = db.Column(
        db.Integer,
        db.ForeignKey("interviews.id"),
        nullable=False
    )

    question_id = db.Column(db.String(100))
    answer_text = db.Column(db.Text)
    score = db.Column(db.Float)
    feedback = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<InterviewAnswer {self.id}>"


# ---------------------------------------------------
# REPORT MODEL
# ---------------------------------------------------

class Report(db.Model):
    """User report model."""

    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    report_type = db.Column(db.String(50))
    content = db.Column(db.JSON)
    talent_score = db.Column(db.Float)

    generated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Report {self.id}>"