
from flask import Blueprint, render_template, session, redirect, url_for
from app.models import QuizSession, QuizResponse, db
import json
from app.database import db
# Create Blueprint
result_bp = Blueprint('result', __name__, url_prefix='/result')

@result_bp.route("/", methods=["GET", "POST"])
def result():
    if "name" not in session or "session_id" not in session:
        return redirect(url_for("home.home"))  # ✅ Fix Redirect Issue

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

    # Fetch questions for review (✅ Prevent Out-of-Bounds Issues)
    questions = [
        {
            "question": user_questions[r.question_id]["question"] if r.question_id < len(user_questions) else "Invalid Question",
            "options": user_questions[r.question_id]["options"] if r.question_id < len(user_questions) else {},
            "answer": r.correct_answer,
            "selected_answer": r.selected_answer,
            "explanation": user_questions[r.question_id].get("explanation", "") if r.question_id < len(user_questions) else "",
            "image": user_questions[r.question_id].get("image", "") if r.question_id < len(user_questions) else ""
        }
        for r in user_responses
    ]

    return render_template("result.html", name=name, score=score, questions=questions)