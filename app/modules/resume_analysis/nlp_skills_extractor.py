import spacy

class NLPSkillExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

        # Add your skill patterns
        self.skill_patterns = {
            "machine learning": ["ml", "machine learning", "model training"],
            "data science": ["data analysis", "data scientist", "analytics"],
            "python": ["python", "py scripting"],
            "deep learning": ["neural network", "cnn", "rnn"],
            "sql": ["sql", "database queries"],
        }

    def extract_skills(self, text):
        doc = self.nlp(text.lower())
        found_skills = set()

        # 🔹 Rule 1: Phrase matching
        for skill, keywords in self.skill_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    found_skills.add(skill)

        # 🔹 Rule 2: Context-based detection
        for sent in doc.sents:
            if "developed" in sent.text or "built" in sent.text:
                if "model" in sent.text:
                    found_skills.add("machine learning")

        return list(found_skills)