
# ---------------------------------------------#
#    LEADERBOARD #
# ---------------------------------------------#
from flask import Blueprint, render_template, session, request, redirect, url_for
from app.models import QuizSession, QuizResponse
from app.database import db
from uuid import uuid4  # Unique session IDs
import os
import json
from sqlalchemy import func, desc

leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/leaderboard')

@leaderboard_bp.route("/", methods=["GET"])
def leaderboard():
    results = db.session.query(
        QuizResponse.student_name.label("name"),
        func.count().filter(QuizResponse.selected_answer == QuizResponse.correct_answer).label("score"),
        func.max(QuizResponse.timestamp).label("date")
    ).group_by(QuizResponse.student_name).order_by(desc("score")).all()

    leaderboard = [
        {"name": r.name, "score": r.score, "date": r.date.strftime("%Y-%m-%d")}
        for r in results
    ]

    return render_template("leaderboard.html", leaderboard=leaderboard)
