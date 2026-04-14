"""
Roadmap Generator - Core logic for personalized learning roadmaps.
Generates data-driven roadmaps from actual career data with rich skill hierarchy.
"""

from typing import Dict, List, Optional, Tuple
from .roadmap_data import get_all_roles, get_role_skills, get_all_skills, get_skill_info, get_roadmap_data_manager
import difflib


def normalize_skill(skill: str) -> str:
    """Normalize skill name for comparison."""
    return skill.lower().strip()


def skill_similarity(user_skill: str, target_skill: str) -> float:
    """Calculate similarity between user skill and target skill (0.0 to 1.0)."""
    user_normalized = normalize_skill(user_skill)
    target_normalized = normalize_skill(target_skill)
    
    # Exact match
    if user_normalized == target_normalized:
        return 1.0
    
    # Use sequence matcher for partial matches
    return difflib.SequenceMatcher(None, user_normalized, target_normalized).ratio()


def parse_user_skills(user_skills_str: str) -> List[str]:
    """Parse comma-separated user skills."""
    if not user_skills_str:
        return []
    
    skills = [s.strip() for s in user_skills_str.split(',') if s.strip()]
    return skills


def get_skill_status(user_skills: List[str], target_skill: str) -> Tuple[str, float]:
    """
    Determine if user has the skill.
    Returns: (status, similarity_score)
    status: 'completed' | 'current' | 'missing'
    """
    if not user_skills:
        return 'missing', 0.0
    
    similarities = [skill_similarity(user_skill, target_skill) for user_skill in user_skills]
    max_similarity = max(similarities) if similarities else 0.0
    
    if max_similarity >= 0.85:  # High similarity = completed
        return 'completed', max_similarity
    elif max_similarity >= 0.50:  # Medium similarity = current/in progress
        return 'current', max_similarity
    else:
        return 'missing', max_similarity


def _get_resources_for_skill(skill: str) -> List[Dict]:
    """Get learning resources for a skill."""
    resources_map = {
        'Python': [
            {'name': 'Python.org', 'type': 'documentation', 'url': 'https://python.org'},
            {'name': 'Real Python', 'type': 'tutorial', 'url': 'https://realpython.com'},
            {'name': 'HackerRank Python', 'type': 'practice', 'url': 'https://hackerrank.com'},
        ],
        'SQL': [
            {'name': 'SQL Tutorial', 'type': 'documentation', 'url': 'https://w3schools.com/sql'},
            {'name': 'LeetCode SQL', 'type': 'practice', 'url': 'https://leetcode.com'},
        ],
        'Machine Learning': [
            {'name': 'Andrew Ng ML Course', 'type': 'course', 'url': 'https://coursera.org'},
            {'name': 'Scikit-learn Docs', 'type': 'documentation', 'url': 'https://scikit-learn.org'},
        ],
        'React': [
            {'name': 'React Official Docs', 'type': 'documentation', 'url': 'https://react.dev'},
            {'name': 'React Tutorial', 'type': 'tutorial', 'url': 'https://react.dev/learn'},
        ]
    }
    return resources_map.get(skill, [
        {'name': f'{skill} Documentation', 'type': 'documentation', 'url': '#'},
        {'name': f'{skill} Tutorial', 'type': 'tutorial', 'url': '#'},
    ])


def _get_projects_for_skill(skill: str) -> List[Dict]:
    """Get project ideas for practicing a skill."""
    projects_map = {
        'Python': [
            {'name': 'Build a Web Scraper', 'difficulty': 'beginner'},
            {'name': 'Create a Task Manager CLI', 'difficulty': 'intermediate'},
        ],
        'SQL': [
            {'name': 'Design a Student Database', 'difficulty': 'beginner'},
            {'name': 'Create Complex JOIN Queries', 'difficulty': 'intermediate'},
        ],
        'Machine Learning': [
            {'name': 'Build a Titanic Survival Predictor', 'difficulty': 'intermediate'},
            {'name': 'Create an Image Classification Model', 'difficulty': 'advanced'},
        ],
        'React': [
            {'name': 'Build a Todo App', 'difficulty': 'beginner'},
            {'name': 'Create a Weather Dashboard', 'difficulty': 'intermediate'},
        ]
    }
    return projects_map.get(skill, [
        {'name': f'Beginner {skill} Project', 'difficulty': 'beginner'},
        {'name': f'Intermediate {skill} Project', 'difficulty': 'intermediate'},
    ])


def build_step_progression(role_skills: List[str]) -> List[Dict]:
    """
    Build step progression for role skills with rich hierarchy.
    Skills are already ordered from basic to advanced by roadmap_data.py
    """
    steps = []
    
    for idx, skill in enumerate(role_skills):
        # Get enriched skill info
        skill_info = get_skill_info(skill) or {}
        
        # Build step info with hierarchy
        step = {
            'id': idx + 1,
            'skill': skill,
            'intro': skill_info.get('intro', skill_info.get('description', f'Master {skill}')),
            'description': skill_info.get('description', f'Master {skill}'),
            'why': skill_info.get('why', f"{skill} is essential for career growth"),
            'level': skill_info.get('level', 1),
            'stage_label': skill_info.get('stage_label', 'Build'),
            'sub_skills': skill_info.get('sub_skills', []),
            'libraries': skill_info.get('libraries', []),
            'concepts': skill_info.get('concepts', []),
            'tools': skill_info.get('tools', []),
            'what_to_learn': skill_info.get('what_to_learn', {}),
            'why_important': skill_info.get('why_important', skill_info.get('why', f"{skill} is essential for career growth")),
            'time_required': skill_info.get('time_estimate', '3-4 weeks'),
            'real_world_usage': skill_info.get('real_world_usage', ''),
            'how_used': skill_info.get('how_used', {'summary': skill_info.get('real_world_usage', ''), 'examples': []}),
            'how_to_start': skill_info.get('how_to_start', []),
            'resources': _get_resources_for_skill(skill),
            'projects': _get_projects_for_skill(skill),
            'status': 'missing',  # Will be updated based on user skills
            'similarity': 0.0
        }
        
        steps.append(step)
    
    return steps


def generate_roadmap(role: str, user_skills_str: str = "", include_graph: bool = True) -> Dict:
    """
    Generate a personalized roadmap for the user with graph structure.
    
    Args:
        role: Selected career role
        user_skills_str: Comma-separated list of user skills
        include_graph: Include graph structure for visualization
    
    Returns:
        Roadmap with steps, progress, graph, and rich skill info
    """
    
    # Validate role
    all_roles = get_all_roles()
    if role not in all_roles:
        return {
            'success': False,
            'error': f'Role "{role}" not found',
            'available_roles': all_roles
        }
    
    # Parse user skills
    user_skills = parse_user_skills(user_skills_str)
    
    # Get all skills for the role
    role_skills = get_role_skills(role)
    
    if not role_skills:
        return {
            'success': False,
            'error': f'No skills found for role "{role}"'
        }
    
    # Build step progression with rich metadata
    steps = build_step_progression(role_skills)
    
    # Assign status based on user skills
    completed_count = 0
    current_count = 0
    missing_count = 0
    next_step = None
    start_point = None
    completed_skills = []
    current_skills = []
    missing_skills = []
    
    for step in steps:
        status, similarity = get_skill_status(user_skills, step['skill'])
        step['status'] = status
        step['similarity'] = round(similarity, 2)
        
        if status == 'completed':
            completed_count += 1
            completed_skills.append(step['skill'])
        elif status == 'current':
            current_count += 1
            current_skills.append(step['skill'])
            if start_point is None:
                start_point = step['skill']
        else:  # missing
            missing_count += 1
            missing_skills.append(step['skill'])
            if next_step is None:
                next_step = step['skill']
                if start_point is None:
                    start_point = step['skill']
    
    # Calculate progress
    total_steps = len(steps)
    progress = int((completed_count / total_steps * 100)) if total_steps > 0 else 0
    
    # Build roadmap response
    roadmap = {
        'success': True,
        'role': role,
        'steps': steps,
        'progress': progress,
        'next_step': next_step,
        'start_point': start_point,
        'completed_skills': completed_skills,
        'current_skills': current_skills,
        'missing_skills': missing_skills,
        'total_steps': total_steps,
        'completed_count': completed_count,
        'current_count': current_count,
        'missing_count': missing_count,
        'user_skills': user_skills
    }
    
    # Add graph structure if requested
    if include_graph:
        data_manager = get_roadmap_data_manager()
        graph = data_manager.build_skill_graph(role, user_skills)
        roadmap['graph'] = graph
    
    return roadmap
