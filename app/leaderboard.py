
# ---------------------------------------------#
#    LEADERBOARD #
# ---------------------------------------------#
from flask import Blueprint, render_template, session, request, redirect, url_for
from app.models import QuizSession, QuizResponse
from app.database import db
from uuid import uuid4  # Unique session IDs
import os
import json

# Create Blueprint
leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/leaderboard')

@leaderboard_bp.route("/", methods=["GET", "POST"])

def leaderboard():
    try:
        with open("quiz_leaderboard.json", "r", encoding="utf-8") as f:
            leaderboard = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        leaderboard = []

    return render_template("leaderboard.html", leaderboard=leaderboard)
