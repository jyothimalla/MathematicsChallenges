from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime 

app = Flask(__name__)
app.secret_key = "super_secure_random_key"

# Load quiz questions
with open("quiz_questions.json", "r", encoding="utf-8") as f:
    ALL_QUESTIONS = json.load(f)

# Temporary storage for user quiz questions
user_questions = {}

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return "Error: Name is required!"

        session["name"] = name
        session["score"] = 0
        session["current_q"] = 0
        session["answers"] = {}  # Store user-selected answers

        # Take the first 20 questions in order
        user_questions[name] = ALL_QUESTIONS[:20]

        return redirect(url_for("quiz"))
    
    return render_template("home.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "name" not in session:
        return redirect(url_for("home"))

    name = session["name"]
    if name not in user_questions:
        return redirect(url_for("home"))

    if "answers" not in session:
        session["answers"] = {}

    # Ensure session["current_q"] is an integer
    session["current_q"] = int(session.get("current_q", 0))

    if request.method == "POST":
        action = request.form.get("action")  # "next", "previous", or "submit"
        selected_answer = request.form.get("answer")

        # Store selected answer
        if selected_answer:
            session["answers"][str(session["current_q"])] = selected_answer  # Store as string key

        # Handle navigation
        if action == "next" and session["current_q"] < len(user_questions[name]) - 1:
            session["current_q"] += 1  # Move forward

        elif action == "previous" and session["current_q"] > 0:
            session["current_q"] -= 1  # Move back

        elif action == "submit":
            return redirect(url_for("result"))

    # Ensure current_q stays in range
    session["current_q"] = max(0, min(session["current_q"], len(user_questions[name]) - 1))

    question = user_questions[name][session["current_q"]]
    previous_answer = session["answers"].get(str(session["current_q"]), "")  # Fetch stored answer

    return render_template("quiz.html", question=question, question_num=session["current_q"] + 1, previous_answer=previous_answer)

LEADERBOARD_FILE = "quiz_leaderboard.json"

def save_score(name, score):
    """ Save the user's score to the leaderboard JSON file """
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            leaderboard = json.load(f)
    else:
        leaderboard = []

    leaderboard.append({"name": name, "score": score, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(leaderboard, f, indent=4)

@app.route("/result")
def result():
    if "name" not in session:
        return redirect(url_for("home"))

    name = session["name"]
    score = sum(1 for i, ans in session["answers"].items() if ans == user_questions[name][int(i)]["answer"])

    save_score(name, score)

    return render_template("result.html", name=name, score=score)

@app.route("/leaderboard")
def leaderboard():
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            leaderboard = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        leaderboard = []

    return render_template("leaderboard.html", leaderboard=leaderboard)

if __name__ == "__main__":
    app.run(debug=True)
