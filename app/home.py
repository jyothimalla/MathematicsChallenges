# ----------------------- #
#  HOME PAGE             #
# ----------------------- #
# 

from flask import Blueprint, render_template, session, request, redirect, url_for
from app.models import QuizSession, QuizResponse
from app.database import db
from uuid import uuid4  # Unique session IDs
import os
import json

# Load questions from JSON
with open("quiz_questions_original.json", "r", encoding="utf-8") as f:
    ALL_QUESTIONS = json.load(f)

# Create Blueprint
home_bp = Blueprint('home', __name__, template_folder="../templates")  # Explicit path

@home_bp.route("/", methods=["GET", "POST"])
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

        return redirect(url_for("quiz.quiz"))

    return render_template("home.html")
