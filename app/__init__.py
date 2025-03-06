from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from app.database import db

# Initialize the database globally
#db = SQLAlchemy()

# Flask Factory Function
def create_app():
    app = Flask(__name__, static_folder="../static", template_folder="../templates")

    # Set secret key to avoid session errors
    app.secret_key = "super_secure_random_key"

    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/maths_challenge'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = "uploads"

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize database and migrations
    db.init_app(app)
    Migrate(app, db)

    # Import and Register Blueprints
    from app.home import home_bp
    from app.quiz import quiz_bp
    from app.result import result_bp
    from app.review import review_bp
    from app.questions import questions_bp
    from app.leaderboard import leaderboard_bp
    # ✅ Prevent duplicate blueprint registration
    if "home" not in app.blueprints:
        app.register_blueprint(home_bp, url_prefix='/')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')
    if "result" not in app.blueprints:
        app.register_blueprint(result_bp, url_prefix='/result')
    if "review" not in app.blueprints:
        app.register_blueprint(review_bp, url_prefix='/review')
    if "questions" not in app.blueprints:
        app.register_blueprint(questions_bp, url_prefix='/questions')
    if "leaderboard" not in app.blueprints:
        app.register_blueprint(leaderboard_bp, url_prefix='/leaderboard')
    
    return app
