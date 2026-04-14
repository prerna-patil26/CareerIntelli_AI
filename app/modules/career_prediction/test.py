from app.modules.career_prediction.career_predictor import CareerPredictor

predictor = CareerPredictor()

result = predictor.predict_career_with_details(["testing", "regression", "selenium"])

print("Career:", result["career"])
print("Confidence:", result["confidence"])
print("Top 3:", result["top_3"])
print("Level:", result["current_level"])

print("\nSkill Analysis:")
for skill, status in result["skills_analysis"].items():
    print(f" - {skill}: {status}")

print("\nMissing Skills:")
for skill in result["missing_skills"]:
    print(f" - {skill}")

print("\nInsight:")
print(result["insight"])

print("\nAction Plan:")
for step in result["action_plan"]:
    print(f" - {step}")