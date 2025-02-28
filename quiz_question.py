import pdfplumber
import json
import re

pdf_path = "First Mathematics Challenge 2023 Paper.pdf"
output_json = "quiz_questions.json"

quiz_data = []
current_question = {}

def extract_questions(text):
    global current_question
    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        # Detect a new question (starts with a number followed by a period)
        if re.match(r"^\d+\.", line):
            if "question" in current_question and "options" in current_question:
                quiz_data.append(current_question)  # Save previous question
            current_question = {"question": line, "options": []}  # Start new question

        # Detect answer choices (A) B) C) D) E))
        elif re.match(r"^[A-E]\)", line) or re.match(r"^[A-E] ", line):
            current_question.setdefault("options", []).append(line)

        # Continue adding multi-line question text
        elif "question" in current_question:
            current_question["question"] += " " + line

    if "question" in current_question and "options" in current_question:
        quiz_data.append(current_question)  # Add last question

# Open PDF and extract text
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            extract_questions(text)

# Save questions to JSON file
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(quiz_data, f, indent=4)

print(f"✅ Extraction Complete! JSON saved as {output_json}")
