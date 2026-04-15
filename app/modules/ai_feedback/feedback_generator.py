import json
import os
from google import genai
from google.genai import types
from openai import OpenAI


class FeedbackGenerator:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")

        # Gemini models — tried one by one, 1 attempt each
        # Source: https://ai.google.dev/gemini-api/docs/models
        self.gemini_models = [
            "gemini-3.1-flash-lite-preview",  # Gemma 4 31B — fastest & cheapest Gemini 3 series
            "gemini-3-flash-preview",          # Gemini 3 Flash — frontier-class, free tier
            "gemini-2.5-flash",                # Gemini 2.5 Flash — stable production fallback
        ]

        # OpenRouter free models — tried one by one, 1 attempt each
        self.openrouter_models = [
            "google/gemma-4-31b-it:free",
            "z-ai/glm-4.5-air:free",
            "arcee-ai/trinity-large-preview:free",
            "minimax/minimax-m2.5:free",
        ]

        self.gemini_client = genai.Client(api_key=self.api_key)
        self.or_client = OpenAI(
            api_key=self.openrouter_key,
            base_url="https://openrouter.ai/api/v1"
        )

    def _build_prompt(self, answers):
        return f"""You are a highly strict and professional AI interviewer.

Analyze the candidate answers deeply and realistically:
{answers}

Evaluate like a real interviewer panel.

Return STRICT JSON only — no markdown, no extra text:

{{
    "score": 0-10,
    "technical": "Detailed evaluation of technical understanding with strengths and weaknesses",
    "communication": "Evaluate clarity, structure, fluency and explanation quality",
    "confidence": "Judge confidence level based on explanation certainty and tone",
    "suggestions": [
        "Give 3-5 very specific and actionable improvements"
    ]
}}"""

    def _parse_json(self, content):
        """Extract and parse JSON from model response."""
        start = content.find("{")
        end = content.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON object found in response")
        return json.loads(content[start:end])

    def generate_feedback(self, answers):
        prompt = self._build_prompt(answers)

        # ── GEMINI MODELS (1 attempt each) ──────────────────────────────────
        for model in self.gemini_models:
            print(f"👉 Trying Gemini: {model}")
            try:
                response = self.gemini_client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        max_output_tokens=2000,  # enough for full JSON
                        temperature=0.4,
                    ),
                )
                print(f"🔍 {model} RESPONSE:", response.text)
                result = self._parse_json(response.text)
                print(f"✅ Success: {model}")
                return result

            except Exception as e:
                print(f"❌ {model} failed: {e}")
                continue  # move to next model immediately

        # ── OPENROUTER MODELS (1 attempt each) ──────────────────────────────
        for model in self.openrouter_models:
            print(f"👉 Trying OpenRouter: {model}")
            try:
                response = self.or_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4,
                    max_tokens=2000,
                )
                content = response.choices[0].message.content
                print(f"🔍 OpenRouter ({model}) RESPONSE:", content)
                result = self._parse_json(content)
                print(f"✅ Success: {model}")
                return result

            except Exception as e:
                print(f"❌ OpenRouter ({model}) failed: {e}")
                continue  # move to next model immediately

        # ── FINAL FALLBACK (only if ALL models fail) ─────────────────────────
        print("⚠️ All models exhausted. Returning default feedback.")
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