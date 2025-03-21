from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models import QuizSession, QuizResponse
from app.database import db
import json, os
import random
from datetime import datetime


quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

# ------------------------- #
#   Utility Functions       #
# ------------------------- #

def load_fmc_questions():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "..", "jsonfiles", "fmc_questions.json")

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            questions = json.load(f)
            if questions:
                print(f"✅ DEBUG: Loaded {len(questions)} FMC questions.")
                return questions
            else:
                print("❌ ERROR: FMC JSON file is empty!")
                return []
    else:
        print("❌ ERROR: FMC Questions JSON file not found!")
        return []
    
    
def generate_math_questions(num_questions=20, operation="multiplication"):
    """Generates dynamic math questions based on the selected operation."""
    questions = []
    
    for _ in range(num_questions):
        num1 = random.randint(10, 99)  # Generate a 2-digit number
        num2 = random.randint(10, 99)  # Generate another 2-digit number

        if operation == "multiplication":
            correct_answer = num1 * num2
            question_text = f"What is {num1} × {num2}?"
        elif operation == "addition":
            correct_answer = num1 + num2
            question_text = f"What is {num1} + {num2}?"
        elif operation == "subtraction":
            num1, num2 = max(num1, num2), min(num1, num2)  # Ensure positive result
            correct_answer = num1 - num2
            question_text = f"What is {num1} - {num2}?"
        elif operation == "division":
            num1 = num1 * num2  # Ensure clean division (no remainders)
            correct_answer = num1 // num2
            question_text = f"What is {num1} ÷ {num2}?"
        
        else:
            raise ValueError("Invalid operation. Choose from: multiplication, addition, subtraction, division.")

        # Generate incorrect options
        incorrect_options = [
            correct_answer + random.randint(1, 10),
            correct_answer - random.randint(1, 10),
            correct_answer + random.randint(10, 20)
        ]

        # Shuffle options
        all_options = [correct_answer] + incorrect_options
        random.shuffle(all_options)

        # Assign letter keys dynamically (A, B, C, D)
        option_keys = ["A", "B", "C", "D"]
        options = {key: str(value) for key, value in zip(option_keys, all_options)}

        # Find the key corresponding to the correct answer
        correct_key = [key for key, value in options.items() if int(value) == correct_answer][0]

        question = {
            "question": question_text,
            "options": options,
            "answer": correct_key  # Store the correct answer key (A, B, C, or D)
        }
        questions.append(question)

    return questions

# ------------------------- #
#         Routes            #
# ------------------------- #

@quiz_bp.route("/choose", methods=["GET", "POST"])
def choose_operation():
    if "name" not in session:
        return redirect(url_for("home.home"))

    if request.method == "POST":
        selected_operation = request.form.get("operation")
        session["selected_operation"] = selected_operation
        print(f"✅ DEBUG: Operation selected and stored -> {selected_operation}")
        return redirect(url_for("quiz.start_quiz"))

    return render_template("choose_operation.html", name=session["name"])


@quiz_bp.route("/", methods=["GET", "POST"])
def start_quiz():
    if "name" not in session or "selected_operation" not in session:
        return redirect(url_for("home.home"))

    session_id = session["session_id"]
    username = session["name"]
    operation = session["selected_operation"]
    print(f"🧠 SESSION SELECTED OPERATION: {operation}")

    session["current_q"] = 0
    session["answers"] = {}

    # Load questions based on operation
    if operation == "fmc":
        questions = load_fmc_questions()
    else:
        questions = generate_math_questions(10, operation)

    print(f"✅ DEBUG: Questions Prepared for {operation} -> {len(questions)}")

    # Save in DB only if not already stored
    existing = QuizSession.query.filter_by(session_id=session_id).first()

    if existing:
        print("♻️ Updating existing QuizSession with new questions")
        existing.username = username
        existing.question_data = json.dumps(questions)
        existing.timestamp = datetime.utcnow()
    else:
        print("🆕 Creating new QuizSession")
        new_session = QuizSession(
            username=username,
            session_id=session_id,
            question_data=json.dumps(questions)
        )
        db.session.add(new_session)

    db.session.commit()

    print(f"📦 QuizSession saved to DB for {operation}")

    return redirect(url_for("quiz.quiz"))





@quiz_bp.route("/quiz", methods=["GET", "POST"])
def quiz():
    print("🔥 DEBUG: Entering quiz() function")

    session_id = session.get("session_id")
    if not session_id:
        return redirect(url_for("home.home"))

    quiz_session = QuizSession.query.filter_by(session_id=session_id).first()
    if not quiz_session:
        print("❌ ERROR: QuizSession not found!")
        return "Quiz session not found. Please start again.", 400

    questions = json.loads(quiz_session.question_data)

    if 'current_q' not in session:
        session['current_q'] = 0

    if request.method == "POST":
        action = request.form.get("action")
        selected_answer = request.form.get("answer")

        if selected_answer:
            session["answers"][str(session["current_q"])] = selected_answer
            correct_answer = questions[session["current_q"]]["answer"]

            response = QuizResponse(
                session_id=session_id,
                question_id=session["current_q"],
                selected_answer=selected_answer,
                correct_answer=correct_answer,
                student_name=session.get("name", "Unknown")
            )
            db.session.add(response)
            db.session.commit()

        if action == "next" and session["current_q"] < len(questions) - 1:
            session["current_q"] += 1
        elif action == "previous" and session["current_q"] > 0:
            session["current_q"] -= 1
        elif action == "submit":
            return redirect(url_for("result.result"))

    current_question = questions[session["current_q"]]
    previous_answer = session["answers"].get(str(session["current_q"]), "")

    print(f"🎯 DEBUG: Final Question Data -> {current_question}")

    return render_template(
        "quiz.html",
        question=current_question,
        question_num=session["current_q"] + 1,
        total_questions=len(questions),
        previous_answer=previous_answer
    )


'''
def handle_post_request(request, session, quiz_session):
    """Handles next, previous, and submit actions while saving answers."""
    action = request.form.get("action")
    selected_answer = request.form.get("answer")

    if selected_answer:
        session["answers"][str(session["current_q"])] = selected_answer
        print(f"✅ DEBUG: Saving answer for question {session['current_q']} -> {selected_answer}")

        # Store answer in database
        response = QuizResponse(
            session_id=session.get("session_id"),
            question_number=session["current_q"],
            selected_answer=selected_answer
        )
        db.session.add(response)
        db.session.commit()
        print("📦 DEBUG: Answer saved to database.")

    if action == "next" and session["current_q"] < len(session["questions"]) - 1:
        session["current_q"] += 1
    elif action == "previous" and session["current_q"] > 0:
        session["current_q"] -= 1
    elif action == "submit":
        return redirect(url_for("quiz.result"))
'''

@quiz_bp.route("/clear_operation", methods=["POST"])
def clear_operation():
    """Clears the stored operation to ensure a fresh selection."""
    print("🔄 DEBUG: Clearing selected operation from session...")
    session.pop("selected_operation", None)  # ✅ Removes old operation
    return "", 204  # No content response


#@quiz_bp.route("/", methods=["GET"])
#def redirect_to_quiz():
#    return redirect(url_for("quiz.quiz"))