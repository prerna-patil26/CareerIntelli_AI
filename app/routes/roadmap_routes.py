"""Routes for the AI roadmap system."""

from __future__ import annotations

import os

from flask import Blueprint, jsonify, render_template, request, send_from_directory

# Create blueprints FIRST without imports
roadmap_page_routes = Blueprint("roadmap_page_routes", __name__)
roadmap_api_routes = Blueprint("roadmap_api_routes", __name__, url_prefix="/api")


@roadmap_page_routes.route("/assets/<path:filename>")
def roadmap_assets(filename: str):
    """Serve roadmap video assets from app/assets."""
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    return send_from_directory(assets_dir, filename)


def _get_all_roles():
    """Lazy-load roles."""
    from app.roadmap.roadmap_data import get_all_roles
    return get_all_roles()


@roadmap_page_routes.route("/roadmap")
def roadmap_page() -> str:
    """Render the roadmap builder page."""
    from app.roadmap.roadmap_data import get_all_roles, get_all_skills

    roles = get_all_roles()
    skills = get_all_skills()
    return render_template("roadmap.html", roles=roles, skills=skills)


@roadmap_page_routes.route("/roadmap-display")
def roadmap_display_page() -> str:
    """Render the visual roadmap display page."""
    return render_template("roadmap.html")


@roadmap_api_routes.route("/roadmap", methods=["GET"])
def roadmap_api() -> tuple:
    """Return roadmap data as JSON with graph structure."""
    from app.roadmap.roadmap_generator import generate_roadmap
    
    role = (request.args.get("role") or "").strip()
    if not role:
        return jsonify({"error": "role query parameter is required"}), 400

    skills = request.args.get("skills", "").strip()
    include_graph = request.args.get("include_graph", "true").lower() == "true"

    try:
        roadmap = generate_roadmap(role=role, user_skills_str=skills, include_graph=include_graph)
        if not roadmap.get("success"):
            return jsonify(roadmap), 400
        return jsonify(roadmap), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Roadmap generation failed: {exc}"}), 500


@roadmap_api_routes.route("/roadmap/roles", methods=["GET"])
def roadmap_roles_api() -> tuple:
    """Return available roadmap roles with info."""
    from app.roadmap.roadmap_data import get_all_roles, get_role_info
    
    try:
        roles = get_all_roles()
        roles_info = []
        
        for role in roles:
            info = get_role_info(role)
            if info:
                roles_info.append(info)
        
        return jsonify({"success": True, "roles": roles_info, "total": len(roles_info)}), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to fetch roles: {exc}"}), 500


@roadmap_api_routes.route("/roadmap/skills", methods=["GET"])
def roadmap_skills_api() -> tuple:
    """Return all available skills with metadata."""
    from app.roadmap.roadmap_data import get_all_skills, get_skill_info
    
    try:
        all_skills = get_all_skills()
        skills_info = []
        
        for skill in all_skills:
            info = get_skill_info(skill)
            if info:
                skills_info.append(info)
        
        return jsonify({"success": True, "skills": skills_info, "total": len(skills_info)}), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to fetch skills: {exc}"}), 500


@roadmap_api_routes.route("/roadmap/skill/<skill_name>", methods=["GET"])
def roadmap_skill_detail_api(skill_name: str) -> tuple:
    """Return detailed information about a specific skill."""
    from app.roadmap.roadmap_data import get_skill_info, get_roadmap_data_manager
    
    try:
        skill_info = get_skill_info(skill_name)
        
        if not skill_info:
            return jsonify({"error": f"Skill '{skill_name}' not found"}), 404
        
        # Add related skills
        data_manager = get_roadmap_data_manager()
        similar_skills = data_manager.suggest_similar_skills(skill_name, limit=5)
        skill_info['related_skills'] = similar_skills
        
        return jsonify({"success": True, "skill": skill_info}), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to fetch skill details: {exc}"}), 500


@roadmap_api_routes.route("/roadmap/graph", methods=["GET"])
def roadmap_graph_api() -> tuple:
    """Return graph structure for visualization."""
    from app.roadmap.roadmap_data import build_skill_graph
    
    try:
        role = request.args.get("role", "").strip()
        if not role:
            return jsonify({"error": "role query parameter is required"}), 400
        
        skills_str = request.args.get("skills", "").strip()
        user_skills = [s.strip() for s in skills_str.split(",")] if skills_str else []
        
        graph = build_skill_graph(role, user_skills)
        
        return jsonify({"success": True, "graph": graph}), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to generate graph: {exc}"}), 500


@roadmap_api_routes.route("/roadmap/guidance", methods=["POST"])
def roadmap_guidance_api() -> tuple:
    """Generate AI guidance for a roadmap."""
    from app.roadmap.ai_generator import generate_guidance
    
    try:
        data = request.get_json() or {}
        
        role = data.get("role", "").strip()
        completed_skills = data.get("completed_skills", [])
        current_skills = data.get("current_skills", [])
        missing_skills = data.get("missing_skills", [])
        next_step = data.get("next_step")
        progress = data.get("progress", 0)
        
        if not role:
            return jsonify({"error": "role is required"}), 400
        
        guidance = generate_guidance(
            role=role,
            completed_skills=completed_skills,
            current_skills=current_skills,
            missing_skills=missing_skills,
            next_step=next_step,
            progress=progress
        )
        
        return jsonify({"success": True, "guidance": guidance}), 200
        
    except Exception as exc:
        return jsonify({"error": f"Guidance generation failed: {exc}"}), 500


@roadmap_api_routes.route("/roadmap/buddy", methods=["POST"])
def roadmap_buddy_api() -> tuple:
    """Generate a friendly buddy chatbot response."""
    from app.roadmap.ai_generator import generate_buddy_response
    
    try:
        data = request.get_json() or {}
        role = (data.get("role") or "").strip()
        message = (data.get("message") or "").strip()

        if not role:
            return jsonify({"error": "role is required"}), 400
        if not message:
            return jsonify({"error": "message is required"}), 400

        reply = generate_buddy_response(
            message=message,
            role=role,
            completed_skills=data.get("completed_skills", []),
            current_skills=data.get("current_skills", []),
            missing_skills=data.get("missing_skills", []),
            next_step=data.get("next_step"),
            progress=data.get("progress", 0),
        )

        return jsonify({"success": True, "reply": reply}), 200
    except Exception as exc:
        return jsonify({"error": f"Buddy response failed: {exc}"}), 500
