import random

# Generate 100 multiplication questions with two 2-digit numbers
questions = []
for i in range(1, 101):
    num1 = random.randint(10, 99)  # Random 2-digit number
    num2 = random.randint(10, 99)  # Random 2-digit number
    answer = num1 * num2
    question = {
        "question": f"{i}. What is {num1} multiplied by {num2}?",
        "answer": str(answer)
    }
    questions.append(question)

# Save to JSON format as requested
import json
json_output_path = "/mnt/data/Multiplication_Questions.json"
with open(json_output_path, "w") as json_file:
    json.dump(questions, json_file, indent=4)

json_output_path
