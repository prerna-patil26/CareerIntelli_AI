import json
import os
from google import genai
from google.genai import types


class FeedbackGenerator:
    def __init__(self):
        self.api_key = (
            os.getenv("GEMINI_API_KEY_1")
            or os.getenv("GEMINI_API_KEY_2")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def generate_feedback(self, answers):
        prompt = f"""
You are a highly strict and professional AI interviewer.
Analyze the candidate answers deeply and realistically:
{answers}
Evaluate like a real interviewer panel.
Return STRICT JSON only:
{{
    "score": 0-10,
    "technical": "Detailed evaluation of technical understanding with strengths and weaknesses",
    "communication": "Evaluate clarity, structure, fluency and explanation quality",
    "confidence": "Judge confidence level based on explanation certainty and tone",
    "suggestions": [
        "Give 3-5 very specific and actionable improvements"
    ]
}}
RULES:
- Be specific to the answers
- No generic feedback
- No extra text outside JSON
"""

        try:
            if not self.client:
                return {
                    "score": 6,
                    "technical": "Basic understanding present but needs improvement.",
                    "communication": "Clarity can be improved with better structure.",
                    "confidence": "Moderate confidence but needs more practice.",
                    "suggestions": [
                        "Practice structured answers",
                        "Improve technical depth",
                        "Work on communication clarity",
                    ],
                }

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=1000,
                    temperature=0.4,
                ),
            )

            if not response.candidates:
                raise Exception("No response from Gemini")

            content = response.candidates[0].content.parts[0].text

            print("🔍 GEMINI RAW RESPONSE:", content)

            start = content.find("{")
            end = content.rfind("}") + 1

            if start == -1 or end == 0:
                raise Exception("Invalid JSON format")

            clean_json = content[start:end]
            parsed = json.loads(clean_json)

            return parsed

        except Exception as e:
            print("❌ Gemini Error:", e)

            return {
                "score": 6,
                "technical": "Basic understanding present but needs improvement.",
                "communication": "Clarity can be improved with better structure.",
                "confidence": "Moderate confidence but needs more practice.",
                "suggestions": [
                    "Practice structured answers",
                    "Improve technical depth",
                    "Work on communication clarity",
                ],
            }