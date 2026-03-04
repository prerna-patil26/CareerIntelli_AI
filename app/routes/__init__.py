"""Routes package for CareerIntelli AI."""

from flask import Blueprint

# Create blueprint for routes
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')
resume_bp = Blueprint('resume', __name__, url_prefix='/api/resume')
career_bp = Blueprint('career', __name__, url_prefix='/api/career')
interview_bp = Blueprint('interview', __name__, url_prefix='/api/interview')
engagement_bp = Blueprint('engagement', __name__, url_prefix='/api/engagement')
report_bp = Blueprint('report', __name__, url_prefix='/api/report')
