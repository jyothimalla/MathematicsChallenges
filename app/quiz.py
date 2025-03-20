from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models import QuizSession, QuizResponse
from app.database import db
import json, os
import random

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')


@quiz_bp.route("/choose", methods=["GET", "POST"])
def choose_operation():
    """Displays a menu for selecting the math operation after entering a name."""
    
    if "name" not in session:
        print("ERROR: Name is missing! Redirecting to home.")  # Debugging
        return redirect(url_for("home.home"))  # Redirect to home if name is missing

    if request.method == "POST":
        selected_operation = request.form.get("operation")  # Get selected operation
        session["selected_operation"] = selected_operation  # Store selection in session

        print(f"✅ DEBUG: Operation selected and stored -> {session['selected_operation']}")  # Debugging
        return redirect(url_for("quiz.start_quiz"))  # Redirect to quiz

    return render_template("choose_operation.html", name=session["name"])  # Show operation selection page

# ✅ Load FMC (Primary Maths Challenge) Questions from JSON File
def load_fmc_questions():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the current file's directory
    json_path = os.path.join(base_dir, "..", "jsonfiles", "fmc_questions.json")  # ✅ Adjust path to reach JSON file


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
    
@quiz_bp.route("/", methods=["GET", "POST"])
def start_quiz():
    """Initialize quiz session and redirect to quiz page."""

    if "name" not in session:
        print("❌ ERROR: Name missing! Redirecting to home.")
        return redirect(url_for("home.home"))

    operation = session.get("selected_operation")  # ✅ Fetch the stored operation
    print(f"✅ DEBUG: Selected Operation in Session -> {operation}")  # 🔍 Debugging

    if not operation:
        print("❌ ERROR: No operation found in session! Redirecting to choose operation.")
        return redirect(url_for("quiz.choose_operation"))
    
    # ✅ Clear session to prevent old questions from being used
    session.pop("questions", None)
    
    if operation == "fmc":
        session['questions'] = load_fmc_questions()  # ✅ Load FMC questions from JSON
        print(f"✅ DEBUG: FMC Questions Loaded -> {len(session['questions'])} questions")  # 🔍 Debugging
    else:
        session['questions'] = generate_math_questions(20, operation)  # ✅ Generate dynamically for other operations
        print(f"✅ DEBUG: Generated {operation} Questions -> {len(session['questions'])} questions")  # 🔍 Debugging

    if not session['questions']:  # Ensure questions exist
        print("❌ ERROR: Question generation failed!")  # Debugging
        return "Error: No questions generated!", 500  # Internal Server Error

    session['current_q'] = 0
    session['answers'] = {}

    return redirect(url_for('quiz.quiz'))  # ✅ Redirect to the quiz page



@quiz_bp.route("/quiz", methods=["GET", "POST"])
def quiz():
    """Handles quiz navigation, answer saving, and rendering."""
    print("🔥 DEBUG: Entering quiz() function")

    if 'questions' not in session or not session['questions']:
        print("❌ ERROR: Questions missing from session. Regenerating...")
        session['questions'] = generate_math_questions(10)
        session['current_q'] = 0
        session['answers'] = {}

    if 'current_q' not in session:
        session['current_q'] = 0

    # Ensure session_id exists
    if "session_id" not in session:
        session["session_id"] = f"quiz_{random.randint(1000, 9999)}"  # Generate a random session ID
        print(f"🆕 DEBUG: Created new session ID: {session['session_id']}")

    # Check if QuizSession exists, if not create it
    quiz_session = QuizSession.query.filter_by(session_id=session["session_id"]).first()
    if not quiz_session:
        print(f"🆕 DEBUG: Creating new QuizSession for Session ID: {session['session_id']}")
        quiz_session = QuizSession(session_id=session["session_id"], question_data=json.dumps(session['questions']))
        db.session.add(quiz_session)
        db.session.commit()

    # Handle form submission (user selecting an answer or navigating)
    if request.method == "POST":
        action = request.form.get("action")  # Get which button was clicked
        selected_answer = request.form.get("answer")  # Get selected answer

        print(f"📝 DEBUG: Received action -> {action}")
        print(f"📝 DEBUG: User selected answer -> {selected_answer}")

        # Save the selected answer
        if selected_answer:
            session['answers'][str(session['current_q'])] = selected_answer
            print(f"✅ DEBUG: Answer saved! {session['answers']}")

            # Get the correct answer for the question
            correct_answer = session["questions"][session["current_q"]]["answer"]

            # Store in the database
            response = QuizResponse(
                session_id=session["session_id"],
                question_id=session["current_q"],
                selected_answer=selected_answer,
                student_name=session.get("name", "Unknown"),
                correct_answer=correct_answer
            )
            db.session.add(response)
            db.session.commit()
            print("📦 DEBUG: Answer saved to database.")

        # Handle navigation
        if action == "next" and session["current_q"] < len(session["questions"]) - 1:
            session["current_q"] += 1  # Move to the next question
        elif action == "previous" and session["current_q"] > 0:
            session["current_q"] -= 1  # Move to the previous question
        elif action == "submit":
            print("🚀 DEBUG: Submitting quiz... Redirecting to results!")
            return redirect(url_for("result.result"))  # ✅ Redirect to results page

        print(f"🔄 DEBUG: Current question index -> {session['current_q']}")

    # Prevent out-of-range index errors
    if session["current_q"] >= len(session["questions"]):
        print("❌ ERROR: current_q index out of range!")
        return "Error: No more questions available!", 400

    current_question = session["questions"][session["current_q"]]

    # Ensure options is a dictionary
    if isinstance(current_question["options"], list):
        print("🚨 ERROR: Options is a list! Converting to dictionary...")
        current_question["options"] = {str(i): option for i, option in enumerate(current_question["options"])}

    print(f"🎯 DEBUG: Final Question Data -> {current_question}")

    previous_answer = session["answers"].get(str(session["current_q"]), "")

    return render_template(
        "quiz.html", 
        question=current_question, 
        question_num=session["current_q"] + 1,
        total_questions=len(session["questions"]), 
        previous_answer=previous_answer
    )


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

@quiz_bp.route("/clear_operation", methods=["POST"])
def clear_operation():
    """Clears the stored operation to ensure a fresh selection."""
    print("🔄 DEBUG: Clearing selected operation from session...")
    session.pop("selected_operation", None)  # ✅ Removes old operation
    return "", 204  # No content response
