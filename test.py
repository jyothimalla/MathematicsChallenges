from app import db, QuizSession

test_session = QuizSession(username="John", session_id="test123", question_data=[])
db.session.add(test_session)
db.session.commit()

print(QuizSession.query.all())  # ✅ If this works, the table exists 🎉
