import pandas as pd
import os


class QuestionLoader:
    def __init__(self):
        # Current file directory → interview_engine
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Go up → modules → app → project root
        base_dir = os.path.abspath(os.path.join(current_dir, "../../"))

        # ✅ Correct file path (root/data folder)
        self.file_path = os.path.join(
            base_dir,
<<<<<<< HEAD
=======
            "app",
>>>>>>> 861db6d4a1dac5677cd1dab90e29279e49e14d82
            "datasets",
            "career_interview_question_bank_dataset.csv.xlsx"
        )

        self.df = None

    def load_questions(self):
        try:
            # ✅ Check if file exists
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"File not found at: {self.file_path}")

            # ✅ Load based on file type
            if self.file_path.endswith(".csv"):
                self.df = pd.read_csv(self.file_path)
            elif self.file_path.endswith(".xlsx"):
                self.df = pd.read_excel(self.file_path)
            else:
                raise ValueError("Unsupported file format. Use CSV or XLSX.")

            # ✅ Clean column names (important)
            self.df.columns = self.df.columns.str.strip().str.lower()

            return self.df

        except Exception as e:
            raise Exception(f"Error loading dataset: {str(e)}")