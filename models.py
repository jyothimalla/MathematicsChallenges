from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    option_e = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(5), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)

class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)

class QuizResponse(db.Model):
    __tablename__ = "quiz_responses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_name = db.Column(db.String(100), nullable=False)  # Correct field name
    session_id = db.Column(db.String(100), nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    selected_answer = db.Column(db.String(5), nullable=False)
    correct_answer = db.Column(db.String(5), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, student_name, session_id, question_id, selected_answer, correct_answer):
        self.student_name = student_name
        self.session_id = session_id
        self.question_id = question_id
        self.selected_answer = selected_answer
        self.correct_answer = correct_answer

class QuizSession(db.Model):
    __tablename__ = 'quiz_session'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)  
    session_id = db.Column(db.String(255), nullable=False, unique=True)
    question_data = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    
    
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
