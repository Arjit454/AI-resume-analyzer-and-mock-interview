import json
from datetime import datetime
from app import db


class InterviewSession(db.Model):
    __tablename__ = "interview_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    mode = db.Column(db.String(20), default="hr")          # hr / technical / mixed
    difficulty = db.Column(db.String(10), default="medium")  # easy / medium / hard

    status = db.Column(db.String(20), default="in_progress")  # in_progress / completed

    questions_json = db.Column(db.Text)   # JSON list of {question, keywords, type}
    current_index = db.Column(db.Integer, default=0)
    questions_total = db.Column(db.Integer, default=5)

    overall_score = db.Column(db.Integer, default=0)
    grammar_score = db.Column(db.Integer, default=0)
    confidence_score = db.Column(db.Integer, default=0)
    technical_score = db.Column(db.Integer, default=0)
    communication_score = db.Column(db.Integer, default=0)
    problem_solving_score = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    user = db.relationship("User", backref="interview_sessions")
    answers = db.relationship(
        "InterviewAnswer", backref="session", order_by="InterviewAnswer.question_index",
        cascade="all, delete-orphan",
    )

    def questions(self):
        try:
            return json.loads(self.questions_json or "[]")
        except (ValueError, TypeError):
            return []

    def current_question(self):
        qs = self.questions()
        if 0 <= self.current_index < len(qs):
            return qs[self.current_index]
        return None

    @property
    def is_complete(self):
        return self.status == "completed"


class InterviewAnswer(db.Model):
    __tablename__ = "interview_answers"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("interview_sessions.id"), nullable=False)

    question_index = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default="hr")  # hr / technical
    answer_text = db.Column(db.Text)

    grammar_score = db.Column(db.Integer, default=0)
    confidence_score = db.Column(db.Integer, default=0)
    technical_score = db.Column(db.Integer, default=0)
    communication_score = db.Column(db.Integer, default=0)
    problem_solving_score = db.Column(db.Integer, default=0)
    overall_score = db.Column(db.Integer, default=0)

    feedback = db.Column(db.Text)
    scored_by_ai = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
