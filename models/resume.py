import json
from datetime import datetime
from app import db


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500))

    ats_score = db.Column(db.Integer, default=0)
    resume_score = db.Column(db.Integer, default=0)  # overall AI-judged quality score

    # parsed contact info
    candidate_name = db.Column(db.String(150))
    candidate_email = db.Column(db.String(150))
    candidate_phone = db.Column(db.String(40))

    # parsed sections — stored as plain text blocks
    education = db.Column(db.Text)
    experience = db.Column(db.Text)
    projects = db.Column(db.Text)
    certifications = db.Column(db.Text)

    extracted_skills = db.Column(db.Text)      # comma-separated
    missing_skills = db.Column(db.Text)        # comma-separated, filled in by AI analysis
    target_role = db.Column(db.String(120))

    raw_text = db.Column(db.Text)              # full extracted text, used by the AI analysis step

    # AI analysis results (populated once /resume/<id>/analyze has run)
    strengths = db.Column(db.Text)             # JSON list
    weaknesses = db.Column(db.Text)            # JSON list
    grammar_suggestions = db.Column(db.Text)   # JSON list
    formatting_suggestions = db.Column(db.Text)  # JSON list
    recommended_technologies = db.Column(db.Text)  # JSON list
    best_job_role = db.Column(db.String(150))
    career_advice = db.Column(db.Text)
    learning_path = db.Column(db.Text)         # JSON list

    ats_breakdown = db.Column(db.Text)         # JSON dict, category -> {score, max}
    analyzed_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="resumes")

    def skills_list(self):
        return [s.strip() for s in (self.extracted_skills or "").split(",") if s.strip()]

    def missing_skills_list(self):
        return [s.strip() for s in (self.missing_skills or "").split(",") if s.strip()]

    def _json_list(self, field_value):
        if not field_value:
            return []
        try:
            return json.loads(field_value)
        except (ValueError, TypeError):
            return []

    def strengths_list(self):
        return self._json_list(self.strengths)

    def weaknesses_list(self):
        return self._json_list(self.weaknesses)

    def grammar_suggestions_list(self):
        return self._json_list(self.grammar_suggestions)

    def formatting_suggestions_list(self):
        return self._json_list(self.formatting_suggestions)

    def recommended_technologies_list(self):
        return self._json_list(self.recommended_technologies)

    def learning_path_list(self):
        return self._json_list(self.learning_path)

    def ats_breakdown_dict(self):
        if not self.ats_breakdown:
            return {}
        try:
            return json.loads(self.ats_breakdown)
        except (ValueError, TypeError):
            return {}

    @property
    def is_analyzed(self):
        return self.analyzed_at is not None
