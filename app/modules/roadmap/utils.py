"""Utility helpers for the roadmap module."""

from __future__ import annotations

import re
from difflib import SequenceMatcher


ROLE_ALIASES = {
    "qa engineer": "QA Engineer",
    "quality assurance engineer": "QA Engineer",
    "frontend engineer": "Frontend Developer",
    "backend engineer": "Backend Developer",
}


SKILL_ALIASES = {
    "manual testing": "testing fundamentals",
    "testing": "testing fundamentals",
    "qa": "testing fundamentals",
    "api": "api development",
    "apis": "api development",
    "rest": "api development",
    "rest api": "api development",
    "html/css": "html and css",
    "css": "html and css",
    "html": "html and css",
    "javascript": "javascript",
    "js": "javascript",
    "reactjs": "react",
    "nodejs": "node.js",
    "node": "node.js",
    "sql": "sql and data modeling",
    "database design": "sql and data modeling",
    "statistics": "statistics and probability",
    "stats": "statistics and probability",
    "numpy": "numpy",
    "pandas": "pandas",
    "ml": "machine learning",
    "machine learning": "machine learning",
    "selenium webdriver": "selenium",
    "automation testing": "automation frameworks",
    "automation": "automation frameworks",
    "ci/cd": "ci/cd and devops",
    "devops": "ci/cd and devops",
    "git": "git and collaboration",
}


def slugify(value: str) -> str:
    """Create a stable node id from a label."""
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return cleaned or "node"


def normalize_text(value: str) -> str:
    """Normalize free text for matching."""
    return re.sub(r"\s+", " ", value.strip().lower())


def normalize_role(role: str) -> str:
    """Normalize free-form role names."""
    cleaned = normalize_text(role)
    if cleaned in ROLE_ALIASES:
        return ROLE_ALIASES[cleaned]
    return " ".join(word.capitalize() for word in cleaned.split())


def canonicalize_skill(skill: str) -> str:
    """Normalize user skill names for graph matching."""
    cleaned = normalize_text(skill)
    return SKILL_ALIASES.get(cleaned, cleaned)


def skill_match_strength(user_skill: str, node_label: str) -> str | None:
    """Return match strength between a provided skill and a roadmap node label."""
    user = canonicalize_skill(user_skill)
    node = canonicalize_skill(node_label)

    if user == node:
        return "completed"

    if user in node or node in user:
        return "partial"

    ratio = SequenceMatcher(None, user, node).ratio()
    if ratio >= 0.72:
        return "partial"

    user_tokens = set(user.split())
    node_tokens = set(node.split())
    if user_tokens and node_tokens and user_tokens.intersection(node_tokens):
        return "partial"

    return None


def normalize_skill(skill_str):
    """Normalize skill string for comparison."""
    return skill_str.strip().lower()


def skill_similarity(skill1, skill2):
    """
    Calculate similarity between two skills using sequence matching.
    Returns value between 0 and 1.
    """
    s1 = normalize_skill(skill1)
    s2 = normalize_skill(skill2)

    if s1 == s2:
        return 1.0

    if s1 in s2 or s2 in s1:
        shorter = min(len(s1), len(s2))
        longer = max(len(s1), len(s2))
        return shorter / longer if longer > 0 else 0

    return SequenceMatcher(None, s1, s2).ratio()


def calculate_skill_gaps(roadmap):
    """Calculate skill gaps from a generated roadmap."""
    missing_steps = [s for s in roadmap['steps'] if s['status'] == 'missing']
    total_gaps = len(missing_steps)
    priority_gaps = [s['skill'] for s in missing_steps[:3]]
    gap_percentage = (total_gaps / roadmap['total_steps']) * 100 if roadmap['total_steps'] > 0 else 0

    return {
        'total_gaps': total_gaps,
        'priority_gaps': priority_gaps,
        'gap_percentage': round(gap_percentage, 2)
    }


def get_learning_timeline(roadmap):
    """Estimate learning timeline for remaining skills."""
    missing_count = roadmap['missing_count']
    current_count = roadmap['current_count']

    estimated_hours = (current_count * 10) + (missing_count * 20)
    estimated_weeks = estimated_hours / 10
    estimated_months = estimated_weeks / 4

    return {
        'estimated_hours': estimated_hours,
        'estimated_weeks': round(estimated_weeks, 1),
        'estimated_months': round(estimated_months, 1),
        'intensive_pace_weeks': round(estimated_weeks / 2, 1),
        'note': 'Based on 10 hours/week learning pace. Intensive pace assumes 20 hours/week.'
    }


def get_skill_suggestions():
    """Get list of common technical skills for suggestions."""
    return [
        'Python', 'JavaScript', 'Java', 'C++', 'Go', 'Rust', 'TypeScript', 'SQL', 'HTML', 'CSS',
        'React', 'Vue', 'Angular', 'Node.js', 'Express', 'Django', 'Flask', 'FastAPI',
        'PostgreSQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
        'Git', 'Linux', 'Bash', 'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
        'Pandas', 'NumPy', 'Scikit-learn', 'Data Analysis', 'Data Visualization', 'Matplotlib', 'Plotly',
        'Excel', 'Tableau', 'Power BI', 'REST API', 'GraphQL', 'WebSocket', 'MQTT',
        'Testing', 'Jest', 'Pytest', 'Selenium', 'JMeter', 'Jenkins', 'GitHub Actions', 'GitLab CI',
        'Terraform', 'Ansible', 'Nginx', 'Apache', 'CI/CD', 'Agile', 'Scrum',
        'System Design', 'Microservices', 'OAuth', 'JWT', 'SOLID Principles', 'Design Patterns', 'Algorithms', 'Data Structures'
    ]