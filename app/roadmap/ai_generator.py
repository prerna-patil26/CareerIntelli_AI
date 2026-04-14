"""AI-powered guidance and buddy chat generation with Gemini fallback."""

from __future__ import annotations

import os
from typing import Dict, List, Optional

import requests


class AIGuidanceGenerator:
    """Generate personalized AI guidance for career roadmaps."""
    
    def __init__(self):
        """Initialize AI generator."""
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.use_fallback = not self.api_key
    
    def generate_roadmap_guidance(self, roadmap_data: Dict) -> Dict:
        """Generate personalized guidance for the entire roadmap."""
        if self.use_fallback:
            return self._fallback_roadmap_guidance(roadmap_data)
        
        try:
            # In production, call LLM here
            return self._fallback_roadmap_guidance(roadmap_data)
        except Exception as e:
            print(f"Error: {e}")
            return self._fallback_roadmap_guidance(roadmap_data)
    
    # ========== FALLBACK RESPONSES ==========
    
    def _fallback_roadmap_guidance(self, roadmap_data: Dict) -> Dict:
        """Fallback roadmap guidance."""
        role = roadmap_data.get('role', 'your target role')
        next_step = roadmap_data.get('next_step', 'the next skill')
        progress = roadmap_data.get('progress', 0)
        completed = roadmap_data.get('completed_skills', [])
        missing = roadmap_data.get('missing_skills', [])
        
        insights = {
            'insight': f'✨ You\'re {progress}% complete on your journey to {role}. You\'ve mastered {len(completed)} skills - great foundation! The remaining skills will unlock your potential and make you truly job-ready.',
            'next_step_why': f'{next_step} is critical because {self._get_skill_importance(next_step)}. It\'s one of the top skills employers look for.',
            'motivation': self._get_motivation_message(progress),
            'pro_tip': self._get_pro_tip(next_step),
            'time_estimate': self._estimate_time_to_completion(len(missing)),
            'common_challenge': self._get_common_challenge(next_step),
            'gap_analysis': f'You need to focus on: {", ".join(missing[:3])}. These are you main learning priorities.'
        }
        
        return insights
    
    def _get_skill_importance(self, skill: str) -> str:
        """Get why a skill is important."""
        reasons = {
            'Python': 'it\'s the foundation for data science, ML, and automation',
            'SQL': 'every tech job uses databases, and SQL is the universal language',
            'Machine Learning': 'it\'s what powers modern AI and transforms raw data into insights',
            'React': 'it\'s used by 80% of modern web apps and is highly in-demand',
            'Docker': 'every company needs containerization for deployment',
            'AWS': 'cloud skills are non-negotiable in 2024',
            'Statistics': 'understanding data is crucial for decision-making'
        }
        return reasons.get(skill, f'{skill} is a highly sought-after skill in the industry')
    
    def _get_motivation_message(self, progress: int) -> str:
        """Get motivational message based on progress."""
        if progress < 25:
            return '🚀 You\'re just getting started! Every expert was once a beginner. You\'re doing amazing - keep that motivation going!'
        elif progress < 50:
            return '💪 Great progress! You\'re a quarter of the way there. The momentum is with you - don\'t stop now!'
        elif progress < 75:
            return '🎯 You\'re over halfway! You\'ve proven you can do this. The finish line is in sight - sprint to the end!'
        else:
            return '🏆 Almost there! You\'re so close to mastery. These final steps will cement your expertise. You\'ve got this!'
    
    def _get_pro_tip(self, skill: str) -> str:
        """Get pro tip for learning a skill."""
        tips = {
            'Python': 'Build projects, don\'t just follow tutorials. Build a portfolio - it\'s worth 10x more than certificates.',
            'SQL': 'Query real datasets. The more complex queries you write, the better you become.',
            'Machine Learning': 'Start with simple algorithms before diving into deep learning. Master the basics first.',
            'React': 'Build a real web app, not just todo lists. Deploy it and show it off.',
            'Docker': 'Containerize your projects. You\'ll understand it 10x better by doing vs reading.',
            'AWS': 'Use the free tier and build something. Hands-on experience beats theory every time.',
            'Statistics': 'Connect concepts to real data. Visualize before you calculate.'
        }
        return tips.get(skill, f'Build projects using {skill}. Hands-on experience is the best teacher.')
    
    def _estimate_time_to_completion(self, remaining_skills: int) -> str:
        """Estimate time to complete roadmap."""
        weeks = remaining_skills * 4  # ~4 weeks per skill on average
        if weeks < 4:
            return f'🎉 Just 1-2 weeks away if you commit 5 hours daily!'
        elif weeks < 12:
            return f'{weeks // 4} months with consistent, focused learning (5 hours/week)'
        elif weeks < 24:
            return f'{weeks // 4} months to complete, 6+ months to be truly proficient'
        else:
            return f'{weeks // 4} months to master everything - but you\'ll be highly competitive after 3 months'
    
    def _get_common_challenge(self, skill: str) -> str:
        """Get common challenge for a skill."""
        challenges = {
            'Python': '❌ Getting stuck with OOP? Use flowcharts to visualize class relationships.',
            'SQL': '❌ Struggling with JOINs? Draw Venn diagrams to understand set relationships.',
            'Machine Learning': '❌ Overfitting is everyone\'s first challenge. Start with simple models.',
            'React': '❌ State management confusion? Break components into tiny pieces.',
            'Docker': '❌ Image sizes too big? Use multi-stage builds to slim them down.',
            'AWS': '❌ Costs spiraling? Use budget alerts and the free tier generously.',
            'Statistics': '❌ Math too abstract? Always start with visualizations.'
        }
        return challenges.get(skill, f'💡 Join communities learning {skill}. You\'re never alone in challenges.')

    def generate_buddy_reply(self, message: str, roadmap_data: Dict) -> str:
        """Generate a friendly buddy-style reply."""
        if self.use_fallback:
            return self._fallback_buddy_reply(message, roadmap_data)

        prompt = f"""
You are a warm, friendly AI career buddy. Keep the tone human, positive, and specific.

User context:
- Target role: {roadmap_data.get('role', 'Unknown role')}
- Completed skills: {', '.join(roadmap_data.get('completed_skills', [])[:6]) or 'None yet'}
- Current skills: {', '.join(roadmap_data.get('current_skills', [])[:6]) or 'Just starting'}
- Missing skills: {', '.join(roadmap_data.get('missing_skills', [])[:6]) or 'None'}
- Next step: {roadmap_data.get('next_step', 'Choose the next foundational skill')}
- Progress: {roadmap_data.get('progress', 0)}%

User message:
{message}

Reply in 3 short parts:
1. Friendly answer
2. Clear next action
3. Small motivation boost
Keep it concise and conversational.
""".strip()

        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=15,
            )
            response.raise_for_status()
            payload = response.json()
            return payload["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            return self._fallback_buddy_reply(message, roadmap_data)

    def _fallback_buddy_reply(self, message: str, roadmap_data: Dict) -> str:
        role = roadmap_data.get("role", "your target role")
        next_step = roadmap_data.get("next_step") or "the next foundational skill"
        progress = roadmap_data.get("progress", 0)
        completed = roadmap_data.get("completed_skills", [])
        current = roadmap_data.get("current_skills", [])

        lower_message = message.lower()
        if any(keyword in lower_message for keyword in ["next", "what should i learn", "start"]):
            return (
                f"Hey, buddy. For your {role} path, the smartest next move is {next_step}. "
                f"Start with one focused session on the basics, then build a tiny practice task around it. "
                f"You're already {progress}% in, so this next push will unlock real momentum."
            )

        if any(keyword in lower_message for keyword in ["stuck", "hard", "difficult", "confused"]):
            focus = current[0] if current else next_step
            return (
                f"It’s completely okay to feel stuck on {focus}. Break it into one concept, one tool, and one mini exercise today. "
                f"Small wins count a lot more than perfect study sessions. "
                f"You’ve already completed {len(completed)} skill(s), so you absolutely can keep moving."
            )

        return (
            f"I’m with you on this {role} journey. Based on your roadmap, {next_step} is the next skill that will create the biggest payoff. "
            f"Try spending 30-45 minutes today on a concept review plus one hands-on example. "
            f"Your consistency matters more than speed, and you're building real progress."
        )


def generate_guidance(
    role: str,
    completed_skills: List[str] = None,
    current_skills: List[str] = None,
    missing_skills: List[str] = None,
    next_step: str = None,
    progress: int = 0
) -> Dict:
    """Generate AI guidance for roadmap."""
    if completed_skills is None:
        completed_skills = []
    if current_skills is None:
        current_skills = []
    if missing_skills is None:
        missing_skills = []
    
    generator = AIGuidanceGenerator()
    
    roadmap_data = {
        'role': role,
        'completed_skills': completed_skills,
        'current_skills': current_skills,
        'missing_skills': missing_skills,
        'next_step': next_step,
        'progress': progress
    }
    
    return generator.generate_roadmap_guidance(roadmap_data)


def generate_buddy_response(
    message: str,
    role: str,
    completed_skills: Optional[List[str]] = None,
    current_skills: Optional[List[str]] = None,
    missing_skills: Optional[List[str]] = None,
    next_step: Optional[str] = None,
    progress: int = 0,
) -> str:
    """Generate a buddy chat reply."""
    generator = AIGuidanceGenerator()
    roadmap_data = {
        "role": role,
        "completed_skills": completed_skills or [],
        "current_skills": current_skills or [],
        "missing_skills": missing_skills or [],
        "next_step": next_step,
        "progress": progress,
    }
    return generator.generate_buddy_reply(message, roadmap_data)
