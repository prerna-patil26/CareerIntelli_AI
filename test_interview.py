from app.modules.interview_engine.question_loader import QuestionLoader
from app.modules.interview_engine.question_selector import QuestionSelector
from app.modules.interview_engine.answer_evaluator import AnswerEvaluator
from app.modules.interview_engine.interview_scorer import InterviewScorer


print("🔹 STEP 1: Loading CSV...")
loader = QuestionLoader()
df = loader.load_questions()

print("✅ CSV Loaded Successfully")
print("Columns:", df.columns.tolist())
print("Total Rows:", len(df))


print("\n🔹 STEP 2: Getting Available Domains...")
selector = QuestionSelector(df)

domains = selector.get_available_domains()
print("✅ Domains:", domains)


# 👉 Choose any domain from output
domain = domains[0]
print(f"\n🔹 STEP 3: Selecting Questions for: {domain}")

questions = selector.select_questions(domain)

print(f"✅ Total Questions Selected: {len(questions)}\n")

for i, q in enumerate(questions, 1):
    print(f"{i}. {q}")


print("\n🔹 STEP 4: Evaluating Answers...")

evaluator = AnswerEvaluator()

# Dummy answers (auto generate)
answers = ["This is my answer about AI and experience " * 2 for _ in questions]

scores = [evaluator.evaluate_answer(ans) for ans in answers]

print("✅ Scores:", scores)


print("\n🔹 STEP 5: Final Score + Feedback")

scorer = InterviewScorer()

final_score = scorer.calculate_score(scores)
feedback = scorer.generate_feedback(final_score)

print("🎯 Final Score:", final_score)
print("💬 Feedback:", feedback)