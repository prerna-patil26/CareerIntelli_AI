"""Skill detail routes for roadmap pages."""

from __future__ import annotations

from flask import Blueprint, render_template

from app.roadmap.skill_explainer import get_skill_details


skill_routes = Blueprint("skill_routes", __name__)


@skill_routes.route("/roadmap/skill/<path:skill_name>")
def skill_detail_page(skill_name: str) -> str:
    """Render a dedicated skill explanation page."""
    details = get_skill_details(skill_name)
    return render_template("skill_detail.html", details=details)
