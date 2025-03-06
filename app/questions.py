from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import json
from .models import db, Question  # Import the database and model

# Create a Blueprint for questions
questions_bp = Blueprint("questions", __name__, template_folder="templates")

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"json"}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if the file is allowed based on extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@questions_bp.route("/add_questions", methods=["GET", "POST"])
def add_question():
    """Route to manually add a question via UI."""
    if request.method == "POST":
        question_text = request.form.get("question_text")
        option_a = request.form.get("option_a")
        option_b = request.form.get("option_b")
        option_c = request.form.get("option_c")
        option_d = request.form.get("option_d")
        option_e = request.form.get("option_e")
        correct_answer = request.form.get("correct_answer")
        image_url = request.form.get("image_url", "")

        if not question_text or not correct_answer:
            flash("Please provide a valid question and answer.", "error")
            return redirect(url_for("questions.add_questions"))

        # Save the question to the database
        new_question = Question(
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            option_e=option_e,
            correct_answer=correct_answer,
            image_url=image_url,
        )
        db.session.add(new_question)
        db.session.commit()
        flash("Question added successfully!", "success")

        return redirect(url_for("questions.add_questions"))

    return render_template("add_questions.html")


@questions_bp.route("/upload_questions", methods=["POST"])
def upload_questions():
    """Upload a JSON file containing multiple questions."""
    if "file" not in request.files:
        flash("No file part", "error")
        return redirect(url_for("questions.add_questions"))

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file", "error")
        return redirect(url_for("questions.add_questions"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Read and save questions from JSON file
        with open(file_path, "r", encoding="utf-8") as f:
            questions_data = json.load(f)

        for q in questions_data:
            new_question = Question(
                question_text=q.get("question"),
                option_a=q.get("options", {}).get("A", ""),
                option_b=q.get("options", {}).get("B", ""),
                option_c=q.get("options", {}).get("C", ""),
                option_d=q.get("options", {}).get("D", ""),
                option_e=q.get("options", {}).get("E", ""),
                correct_answer=q.get("answer"),
                image_url=q.get("image", ""),
            )
            db.session.add(new_question)

        db.session.commit()
        flash("Questions uploaded successfully!", "success")
        return redirect(url_for("questions.add_question"))

    flash("Invalid file type. Please upload a JSON file.", "error")
    return redirect(url_for("questions.add_question"))


@questions_bp.route("/view_questions")
def view_questions():
    """View all questions stored in the database."""
    questions = Question.query.all()
    return render_template("view_questions.html", questions=questions)
