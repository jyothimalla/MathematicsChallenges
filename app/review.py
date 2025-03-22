from flask import Blueprint, render_template, session, redirect, url_for
from app.models import QuizSession, QuizResponse, db
import json

# Create Blueprint
review_bp = Blueprint('review', __name__, url_prefix='/review')

@review_bp.route("/", methods=["GET", "POST"])

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

    return render_template("review.html", name=name,questions=questions)