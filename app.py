from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from uuid import uuid4  # Unique session IDs
from app.models import db, QuizSession, QuizResponse
from app import create_app  # Import from app/__init__.py
from app.home import home_bp  # Import the home blueprint
from app.database import db

# Create Flask app using factory function
app = create_app()

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
    app.run(debug=True)

