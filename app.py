from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from uuid import uuid4  # Unique session IDs
from models import db, QuizSession, QuizResponse

# Flask app setup
app = Flask(__name__)
app.secret_key = "super_secure_random_key"

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/maths_challenge'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = "uploads"

db.init_app(app)
migrate = Migrate(app, db)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load questions from JSON
with open("quiz_questions_original.json", "r", encoding="utf-8") as f:
    ALL_QUESTIONS = json.load(f)

# ----------------------- #
#  HOME PAGE             #
# ----------------------- #
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return "Error: Name is required!"

        session_id = str(uuid4())  # Generate session ID
        session["name"] = name
        session["session_id"] = session_id
        session["score"] = 0
        session["current_q"] = 0
        session["answers"] = {}

        # Save quiz session to DB
        new_session = QuizSession(username=name, session_id=session_id, question_data=json.dumps(ALL_QUESTIONS[:20]))
        db.session.add(new_session)
        db.session.commit()
        
        print(f"DEBUG: Created new session for {name} with ID {session_id}")

        return redirect(url_for("quiz"))

    return render_template("home.html")

# ----------------------- #
#  QUIZ PAGE             #
# ----------------------- #
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "name" not in session or "session_id" not in session:
        print("DEBUG: Missing session data, redirecting to home")
        return redirect(url_for("home"))

    name = session["name"]
    session_id = session["session_id"]

    # Retrieve quiz session from DB
    quiz_session = QuizSession.query.filter_by(session_id=session_id).first()
    if not quiz_session:
        print(f"DEBUG: No session found for {name}, redirecting to home")
        return redirect(url_for("home"))

    user_questions = json.loads(quiz_session.question_data)  # Convert JSON to list

    session["current_q"] = int(session.get("current_q", 0))

    if request.method == "POST":
        action = request.form.get("action")
        selected_answer = request.form.get("answer")

        if selected_answer:
            session["answers"][str(session["current_q"])] = selected_answer

            # Save or update response in DB
            existing_response = QuizResponse.query.filter_by(session_id=session_id, question_id=session["current_q"]).first()
            if existing_response:
                existing_response.selected_answer = selected_answer
            else:
                new_response = QuizResponse(
                    session_id=session_id,
                    student_name=name,
                    question_id=session["current_q"],
                    selected_answer=selected_answer,
                    correct_answer=user_questions[session["current_q"]]["answer"]
                )
                db.session.add(new_response)

            db.session.commit()

        # Navigation
        if action == "next" and session["current_q"] < len(user_questions) - 1:
            session["current_q"] += 1
        elif action == "previous" and session["current_q"] > 0:
            session["current_q"] -= 1
        elif action == "submit":
            return redirect(url_for("result"))

    session["current_q"] = max(0, min(session["current_q"], len(user_questions) - 1))
    question = user_questions[session["current_q"]]

    return render_template("quiz.html", question=question, question_num=session["current_q"] + 1, total_questions=len(user_questions))

# ----------------------- #
#  RESULT PAGE           #
# ----------------------- #
@app.route("/result")
def result():
    if "name" not in session or "session_id" not in session:
        return redirect(url_for("home"))

    name = session["name"]
    session_id = session["session_id"]

    print(f"DEBUG: Fetching results for {name}")

    # Retrieve session & responses
    quiz_session = QuizSession.query.filter_by(session_id=session_id).first()
    user_responses = QuizResponse.query.filter_by(session_id=session_id).all()

    if not quiz_session or not user_responses:
        return "Error: No quiz session found. Please restart the quiz.", 400

    user_questions = json.loads(quiz_session.question_data)

    # Calculate score
    score = sum(1 for r in user_responses if r.selected_answer == r.correct_answer)

    # Fetch questions for review
    questions = [
        {
            "question": user_questions[r.question_id]["question"],
            "options": user_questions[r.question_id]["options"],
            "answer": r.correct_answer,
            "selected_answer": r.selected_answer,
            "explanation": user_questions[r.question_id].get("explanation", ""),
            "image": user_questions[r.question_id].get("image", "")
        }
        for r in user_responses
    ]

    return render_template("result.html", name=name, score=score, questions=questions)

# ----------------------- #
#  REVIEW PAGE           #
# ----------------------- #
@app.route("/review")
def review():
    if "name" not in session:
        return redirect(url_for("home"))

    name = session["name"]
    session_id = session.get("session_id")

    # Fetch responses
    responses = QuizResponse.query.filter_by(student_name=name, session_id=session_id).all()

    if not responses:
        return "No responses found."

    quiz_session = QuizSession.query.filter_by(session_id=session_id).first()
    user_questions = json.loads(quiz_session.question_data)

    questions = [
        {
            "question": user_questions[resp.question_id]["question"],
            "options": user_questions[resp.question_id]["options"],
            "answer": resp.correct_answer,
            "selected_answer": resp.selected_answer,
            "explanation": user_questions[resp.question_id].get("explanation", ""),
            "image": user_questions[resp.question_id].get("image", "")
        }
        for resp in responses
    ]

    return render_template("review.html", name=name, questions=questions)

# ---------------------------------------------#
#    LEADERBOARD #
# ---------------------------------------------#

LEADERBOARD_FILE = "quiz_leaderboard.json"

@app.route("/leaderboard")
def leaderboard():
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            leaderboard = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        leaderboard = []

    return render_template("leaderboard.html", leaderboard=leaderboard)
# ----------------------- #
#  CLEAR SESSION         #
# ----------------------- #
@app.route("/clear")
def clear_session():
    session.clear()
    return "Session cleared! <a href='/'>Go Home</a>"

# ----------------------- #
#  RUN APP               #
# ----------------------- #
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables exist
    app.run(debug=True)
