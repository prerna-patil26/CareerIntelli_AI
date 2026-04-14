import sys
import os

# ✅ Fix import path (VERY IMPORTANT)
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from modules.interview_engine.question_loader import QuestionLoader
from modules.interview_engine.question_selector import QuestionSelector
from modules.interview_engine.answer_evaluator import AnswerEvaluator
from modules.interview_engine.interview_scorer import InterviewScorer


print("🔹 STEP 1: Loading CSV...")
loader = QuestionLoader()
df = loader.load_questions()

# ✅ Clean column names (VERY IMPORTANT FIX)
df.columns = df.columns.str.strip().str.lower()

print("✅ CSV Loaded Successfully")
print("Columns:", df.columns.tolist())
print("Total Rows:", len(df))


# ✅ Check required columns
required_cols = ['role', 'question', 'question_type']
for col in required_cols:
    if col not in df.columns:
        print(f"❌ Missing column: {col}")
        print("👉 Please check your CSV file!")
        exit()


print("\n🔹 STEP 2: Getting Available Domains...")
selector = QuestionSelector(df)

domains = selector.get_available_domains()
print("✅ Domains:", domains)

if not domains:
    print("❌ No domains found in CSV")
    exit()


# 👉 Choose first domain
domain = domains[0]
print(f"\n🔹 STEP 3: Selecting Questions for: {domain}")

questions = selector.select_questions(domain)

print(f"✅ Total Questions Selected: {len(questions)}\n")

if len(questions) < 15:
    print("⚠️ Warning: Less than 15 questions available for this domain")


for i, q in enumerate(questions, 1):
    print(f"{i}. {q}")


print("\n🔹 STEP 4: Evaluating Answers...")

evaluator = AnswerEvaluator()

# Dummy answers
answers = ["This is my answer about AI and experience " * 2 for _ in questions]

scores = [evaluator.evaluate_answer(ans) for ans in answers]

print("✅ Scores:", scores)


print("\n🔹 STEP 5: Final Score + Feedback")

scorer = InterviewScorer()

final_score = scorer.calculate_score(scores)
feedback = scorer.generate_feedback(final_score)

print("🎯 Final Score:", final_score)
print("💬 Feedback:", feedback)