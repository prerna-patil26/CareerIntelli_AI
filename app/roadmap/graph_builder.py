"""Career roadmap graph builder."""

from __future__ import annotations

from app.roadmap.utils import normalize_role, slugify


ROLE_ROADMAPS = {
    "Data Scientist": {
        "summary": "Build strong analysis foundations first, then move into machine learning and project-based problem solving.",
        "stages": {
            "basic": [
                ("Python", "Learn Python syntax, functions, and problem solving for data work."),
                ("Statistics", "Understand probability, distributions, and hypothesis testing."),
                ("Data Analysis", "Clean data, inspect trends, and answer business questions."),
            ],
            "intermediate": [
                ("SQL", "Query structured datasets efficiently."),
                ("Pandas", "Transform and analyze data in tabular form."),
                ("Data Visualization", "Explain findings through charts and dashboards."),
            ],
            "advanced": [
                ("Machine Learning", "Train predictive models and evaluate performance."),
                ("Projects", "Build end-to-end portfolio case studies."),
                ("Model Deployment", "Publish and monitor practical ML solutions."),
            ],
        },
    },
    "QA Engineer": {
        "summary": "Start with testing fundamentals, then automation, and finally production-ready quality engineering practices.",
        "stages": {
            "basic": [
                ("Testing Basics", "Understand SDLC, STLC, bug reports, and QA mindset."),
                ("Test Cases", "Write clear manual test cases and scenarios."),
                ("Bug Tracking", "Document defects with reproducible evidence."),
            ],
            "intermediate": [
                ("SQL", "Validate data changes and backend test results."),
                ("API Testing", "Test endpoints, payloads, and response validation."),
                ("Selenium", "Automate browser-based functional testing."),
            ],
            "advanced": [
                ("Automation Frameworks", "Create reusable test structure and utilities."),
                ("CI/CD Testing", "Run automated tests inside delivery pipelines."),
                ("Performance Testing", "Validate speed and stability under load."),
            ],
        },
    },
    "Backend Developer": {
        "summary": "Learn coding, databases, and APIs first, then move into secure and scalable backend architecture.",
        "stages": {
            "basic": [
                ("Programming Basics", "Understand logic, functions, and clean coding fundamentals."),
                ("Python", "Use Python for server-side development."),
                ("Data Structures", "Choose efficient ways to organize and process data."),
            ],
            "intermediate": [
                ("SQL", "Design schemas and query relational data."),
                ("API Development", "Build REST endpoints and business logic."),
                ("Authentication", "Secure routes and manage user identity."),
            ],
            "advanced": [
                ("System Design", "Plan scalable architecture and service boundaries."),
                ("Caching", "Improve response times and reduce repeated load."),
                ("Deployment", "Run backend applications in production environments."),
            ],
        },
    },
    "Frontend Developer": {
        "summary": "Start with web fundamentals, then build interactive applications, and finally optimize polished user experiences.",
        "stages": {
            "basic": [
                ("HTML", "Create semantic and accessible page structure."),
                ("CSS", "Build layouts, responsiveness, and visual styling."),
                ("JavaScript", "Add interaction and client-side behavior."),
            ],
            "intermediate": [
                ("React", "Build reusable components and application views."),
                ("API Integration", "Fetch and display backend data correctly."),
                ("State Management", "Handle shared application state cleanly."),
            ],
            "advanced": [
                ("Accessibility", "Make interfaces usable for more people."),
                ("Performance Optimization", "Ship faster-loading and smoother interfaces."),
                ("Projects", "Create polished portfolio applications."),
            ],
        },
    },
}


def available_roles() -> list[str]:
    """Return supported roadmap roles."""
    return sorted(ROLE_ROADMAPS.keys())


def build_graph(role: str) -> dict:
    """Build a structured dependency graph for a role."""
    role = normalize_role(role)
    if role not in ROLE_ROADMAPS:
        raise ValueError(f"Unsupported role '{role}'.")

    roadmap = ROLE_ROADMAPS[role]
    nodes, edges, ordered_path = [], [], []
    previous_node_id = None
    step_number = 1

    for level in ("basic", "intermediate", "advanced"):
        for label, description in roadmap["stages"][level]:
            node_id = slugify(f"{role}-{label}")
            nodes.append(
                {
                    "id": node_id,
                    "label": label,
                    "level": level,
                    "description": description,
                    "role": role,
                    "stage_title": level.capitalize(),
                    "step_number": step_number,
                    "start_hint": "Start here" if step_number == 1 else f"Step {step_number}",
                }
            )
            ordered_path.append(node_id)
            if previous_node_id is not None:
                edges.append({"from": previous_node_id, "to": node_id})
            previous_node_id = node_id
            step_number += 1

    target_id = slugify(role)
    nodes.append(
        {
            "id": target_id,
            "label": role,
            "level": "target",
            "description": f"Target career: {role}",
            "role": role,
            "stage_title": "Target",
            "step_number": step_number,
            "start_hint": "Career Goal",
        }
    )
    if previous_node_id:
        edges.append({"from": previous_node_id, "to": target_id})
    ordered_path.append(target_id)

    return {
        "role": role,
        "summary": roadmap["summary"],
        "nodes": nodes,
        "edges": edges,
        "ordered_path": ordered_path,
        "target_node": target_id,
        "skill_options": [node["label"] for node in nodes if node["level"] != "target"],
        "stage_overview": [
            {"level": "basic", "title": "Start Here"},
            {"level": "intermediate", "title": "Build Practical Skills"},
            {"level": "advanced", "title": "Become Job Ready"},
        ],
    }
