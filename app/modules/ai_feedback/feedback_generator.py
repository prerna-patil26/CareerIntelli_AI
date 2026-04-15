import json
import os
import time
from google import genai
from google.genai import types

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class FeedbackGenerator:
    def __init__(self):
        # ✅ API KEY
        self.api_key = os.getenv("GEMINI_API_KEY")

        # ✅ OPENROUTER KEY
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")

        # ✅ MULTIPLE MODELS
        self.models = [
            "gemini-3.1-flash-lite-preview",
            "gemini-2.5-flash",
            "gemini-1.5-flash"
        ]

        # ✅ CLIENTS
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

        self.or_client = None
        if OpenAI and self.openrouter_key:
            self.or_client = OpenAI(
                api_key=self.openrouter_key,
                base_url="https://openrouter.ai/api/v1"
            )

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

        # 🔁 TRY GEMINI
        for model in self.models:
            print(f"👉 Trying model: {model}")

            for attempt in range(1):   # ⚡ FAST (only 1 try)
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            max_output_tokens=500,
                            temperature=0.4,
                        ),
                        timeout=8   # ⚡ prevent long wait
                    )

                    content = response.text
                    print("🔍 GEMINI RAW RESPONSE:", content)

                    start = content.find("{")
                    end = content.rfind("}") + 1

                    if start == -1 or end == -1:
                        raise ValueError("Invalid JSON from AI")

                    return json.loads(content[start:end])

                except Exception as e:
                    print(f"❌ {model} Error:", e)
                    break

        # 🔥 OPENROUTER FALLBACK
        print("👉 Trying OpenRouter fallback...")

        try:
            if not self.or_client:
                raise RuntimeError("OpenRouter client is unavailable")

            response = self.or_client.chat.completions.create(
                model="openchat/openchat-7b",   # ⚡ faster model
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                timeout=10
            )

            content = response.choices[0].message.content
            print("🔍 OPENROUTER RESPONSE:", content)

            start = content.find("{")
            end = content.rfind("}") + 1

            if start != -1 and end != -1:
                return json.loads(content[start:end])

        except Exception as e:
            print("❌ OpenRouter Error:", e)

        # ✅ FINAL FALLBACK
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