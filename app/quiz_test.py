from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models import QuizSession, QuizResponse
from app.database import db
import json
import random
from quiz import generate_math_questions

questions = generate_math_questions(3)  # Generate 3 test questions
print(questions)


quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

def generate_math_questions(num_questions=10):
    """Generates dynamic math questions with multiple-choice options."""
    questions = []

    for _ in range(num_questions):
        num1 = random.randint(10, 99)
        num2 = random.randint(10, 99)
        answer = num1 * num2

        options = {
            "A": str(answer),  # Ensure values are strings to match expected format
            "B": str(answer + random.randint(1, 10)),
            "C": str(answer - random.randint(1, 10)),
            "D": str(answer + random.randint(10, 20))
        }

        question = {
            "question": f"What is {num1} x {num2}?",
            "options": options,  # ✅ Ensure options is a dictionary
            "answer": "A"  # The correct answer key
        }
        questions.append(question)

    return questions

@quiz_bp.route("/", methods=["GET", "POST"])
def start_quiz():
    """Initialize quiz session and redirect to quiz page."""
    session['questions'] = generate_math_questions(10)  # Generate 10 questions

    if not session['questions']:  # Ensure questions exist
        print("ERROR: Question generation failed")  # Debugging
        return "Error: No questions generated!", 500  # Internal Server Error

    session['current_q'] = 0
    session['answers'] = {}

    return redirect(url_for('quiz.quiz'))

@quiz_bp.route("/quiz", methods=["GET", "POST"])
def quiz():
    """Handles quiz navigation and rendering."""

    print("DEBUG: Entering quiz function")
    
    if 'questions' not in session or not session['questions']:
        print("ERROR: Questions missing from session. Regenerating...")
        session['questions'] = generate_math_questions(10)
        session['current_q'] = 0
    
    if 'current_q' not in session:
        session['current_q'] = 0

    # Prevent accessing an out-of-range question index
    if session['current_q'] >= len(session['questions']):
        print("ERROR: current_q index out of range!")
        return "Error: No more questions available!", 400  # Bad Request

    # Ensure current_question is valid
    current_question = session['questions'][session['current_q']]
    if not isinstance(current_question, dict) or "options" not in current_question:
        print("ERROR: current_question is not formatted correctly!", current_question)
        return "Error: Invalid question format!", 500  # Internal Server Error

    previous_answer = session['answers'].get(str(session['current_q']), "")

    return render_template(
        "quiz.html", 
        question=current_question, 
        question_num=session["current_q"] + 1,
        total_questions=len(session["questions"]), 
        previous_answer=previous_answer
    )

def handle_post_request(request, session, quiz_session):
    """Handles next, previous, and submit actions."""
    action = request.form.get("action")
    selected_answer = request.form.get("answer")

    if selected_answer:
        session["answers"][str(session["current_q"])] = selected_answer

    if action == "next" and session["current_q"] < len(session["questions"]) - 1:
        session["current_q"] += 1
    elif action == "previous" and session["current_q"] > 0:
        session["current_q"] -= 1
    elif action == "submit":
        return redirect(url_for("result.result"))

if __name__ == "__main__":
    # Test generate_math_questions() function
    questions = generate_math_questions(5)  # Generate 5 test questions

    # Print output to check format
    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i}: {q['question']}")
        print("Options:")
        for key, value in q['options'].items():
            print(f"  {key}: {value}")

    # Ensure options is a dictionary
    assert isinstance(questions[0]['options'], dict), "❌ Error: options is not a dictionary!"
    print("\n✅ Function is working correctly!")
