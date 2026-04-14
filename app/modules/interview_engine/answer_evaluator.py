import pandas as pd
import os


class QuestionLoader:
    def __init__(self):
        # Current file directory → interview_engine
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # ✅ Go up → modules → app (STOP HERE, not root)
        base_dir = os.path.abspath(os.path.join(current_dir, "../../"))

        # ✅ FIXED PATH (your current structure)
        self.file_path = os.path.join(
            base_dir,
            "datasets",
            "career_interview_question_bank_dataset.csv.xlsx"
        )

        self.df = None

    def load_questions(self):
        try:
            print("📂 FINAL PATH:", self.file_path)  # debug

            # ✅ Check if file exists
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"File not found at: {self.file_path}")

            # ✅ Load file
            if self.file_path.endswith(".csv"):
                self.df = pd.read_csv(self.file_path)
            elif self.file_path.endswith(".xlsx"):
                self.df = pd.read_excel(self.file_path)
            else:
                raise ValueError("Unsupported file format. Use CSV or XLSX.")

            # ✅ IMPORTANT FIX (column cleaning)
            self.df.columns = (
                self.df.columns
                .str.strip()
                .str.lower()
                .str.replace(" ", "_")
            )

            print("✅ COLUMNS:", self.df.columns)  # debug

            return self.df

        except Exception as e:
            raise Exception(f"Error loading dataset: {str(e)}")