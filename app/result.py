
from flask import Blueprint, render_template, session, redirect, url_for
from app.models import QuizSession, QuizResponse, db
import json
from app.database import db
# Create Blueprint
result_bp = Blueprint('result', __name__, url_prefix='/result')

@result_bp.route("/", methods=["GET", "POST"])
def result():
    if "name" not in session or "session_id" not in session:
        print("❌ ERROR: Session ID or Name missing! Redirecting to home.")
        return redirect(url_for("home.home"))

    name = session["name"]
    session_id = session["session_id"]

    print(f"🔍 DEBUG: Fetching results for {name}, Session ID: {session_id}")

    # Retrieve session & responses
    quiz_session = QuizSession.query.filter_by(session_id=session_id).first()
    user_responses = QuizResponse.query.filter_by(session_id=session_id).all()

    if not quiz_session:
        print(f"❌ ERROR: No quiz session found for Session ID: {session_id}")
        return "Error: No quiz session found. Please restart the quiz.", 400

    if not user_responses:
        print(f"❌ ERROR: No user responses found for Session ID: {session_id}")
        return "Error: No user responses found. Please restart the quiz.", 400

    user_questions = json.loads(quiz_session.question_data)
    total_questions=len(user_questions)
    # Use a dictionary to track latest response per question
    response_map = {}
    for r in user_responses:
        response_map[r.question_id] = r

    # Then calculate score only once per question
    score = sum(1 for r in response_map.values() if r.selected_answer == r.correct_answer)

    # Fetch questions for review
    questions = [
        {
            "question": user_questions[r.question_id]["question"] if r.question_id < total_questions else "Invalid Question",
            "options": user_questions[r.question_id]["options"] if r.question_id < total_questions else {},
            "answer": r.correct_answer,
            "selected_answer": r.selected_answer,
            "explanation": user_questions[r.question_id].get("explanation", "") if r.question_id < len(user_questions) else "",
            "image": user_questions[r.question_id].get("image", "") if r.question_id < len(user_questions) else ""
        }
        for r in user_responses
    ]

    print(f"🏆 DEBUG: User Score -> {score}")

    return render_template("result.html", name=name, score=score, questions=questions, total_questions=total_questions)
