import json

# Load questions from JSON file
with open("quiz_questions.json", "r", encoding="utf-8") as f:
    quiz_data = json.load(f)

# Ensure only 20 questions are asked
quiz_data = quiz_data[:3]  # Take the first 20 questions

# Initialize score
score = 0
user_answers = []  # Stores user's answers for review

print("\n🎯 Welcome to the First Mathematics Challenge! 🎯\n")

for i, q in enumerate(quiz_data, start=1):
    print(f"\nQ{i}: {q['question']}")
    
    # Display multiple-choice options
    for option in q["options"]:
        print(option)
    
    # Take user input
    user_answer = input("Your answer (A/B/C/D/E): ").strip().upper()

    # Validate user input
    while user_answer not in ["A", "B", "C", "D", "E"]:
        user_answer = input("Invalid choice! Enter A, B, C, D, or E: ").strip().upper()

    # Store answer for review
    correct_answer = q.get("answer", "")  # If answer is missing, default to empty string
    user_answers.append({
        "question": q["question"],
        "your_answer": user_answer,
        "correct_answer": correct_answer,
        "explanation": q.get("explanation", "No explanation available")
    })

    # Check correctness
    if user_answer == correct_answer:
        print("✅ Correct!")
        score += 1
    else:
        print(f"❌ Wrong! The correct answer is {correct_answer}")

# Show final result
print("\n🎉 Quiz Completed! 🎉")
print(f"✅ Your Score: {score}/{len(quiz_data)}")

# Option to review answers
review = input("Do you want to review answers? (yes/no): ").strip().lower()
if review == "yes":
    for i, qa in enumerate(user_answers, start=1):
        print(f"\nQ{i}: {qa['question']}")
        print(f"📝 Your Answer: {qa['your_answer']}")
        print(f"✅ Correct Answer: {qa['correct_answer']}")
        print(f"📖 Explanation: {qa['explanation']}")

print("\n🎯 Thank you for writing the Maths Test! 🎯")
