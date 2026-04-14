from typing import List
import google.generativeai as genai


class FeedbackGenerator:

    def __init__(self):
        # ✅ PUT API KEY DIRECTLY (for testing)
        genai.configure(api_key="GEMINI_API_KEY")

        self.model = genai.GenerativeModel("gemini-pro")

    def get_ai_resume_feedback(self, resume_text: str) -> List[str]:

        try:
            prompt = f"""
            You are an expert resume reviewer.

            Analyze this resume and give 5 short improvement suggestions.

            Resume:
            {resume_text}
            """

            response = self.model.generate_content(prompt)

            print("GEMINI RAW RESPONSE:", response)   # 🔥 DEBUG

            if not response or not response.text:
                return ["AI failed: No response"]

            feedback = response.text.split("\n")

            return [f.strip("•- ") for f in feedback if f.strip()]

        except Exception as e:
            print("🔥 GEMINI ERROR:", e)
            return [f"AI Error: {str(e)}"]