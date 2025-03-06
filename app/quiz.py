from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models import QuizSession, QuizResponse
from app.database import db
import json

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

@quiz_bp.route("/", methods=["GET", "POST"])
def quiz():
    if "name" not in session or "session_id" not in session:
        print("DEBUG: Missing session data, redirecting to home")
        return redirect(url_for("home.home"))  # Make sure `home.home` is correct

    name = session["name"]
    session_id = session["session_id"]

    # Retrieve quiz session from DB
    quiz_session = QuizSession.query.filter_by(session_id=session_id).first()
    if not quiz_session:
        print(f"DEBUG: No session found for {name}, redirecting to home")
        return redirect(url_for("home.home"))

    user_questions = json.loads(quiz_session.question_data)  # Convert JSON to list

    # Ensure session tracking variables exist
    if "current_q" not in session:
        session["current_q"] = 0
    if "answers" not in session:
        session["answers"] = {}

    if request.method == "POST":
        action = request.form.get("action")
        selected_answer = request.form.get("answer")

        if selected_answer:
            session["answers"][str(session["current_q"])] = selected_answer  # ✅ Save selected answer

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

        # Navigation Handling
        if action == "next" and session["current_q"] < len(user_questions) - 1:
            session["current_q"] += 1
        elif action == "previous" and session["current_q"] > 0:
            session["current_q"] -= 1
        elif action == "submit":
            return redirect(url_for("result.result"))

    session["current_q"] = max(0, min(session["current_q"], len(user_questions) - 1))
    question = user_questions[session["current_q"]]
    previous_answer = session["answers"].get(str(session["current_q"]), "")

    return render_template("quiz.html", question=question, question_num=session["current_q"] + 1,
        total_questions=len(user_questions),
        previous_answer=previous_answer  # ✅ Pass selected answer to frontend
    )
