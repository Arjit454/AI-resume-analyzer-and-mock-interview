from datetime import datetime
from app import db


class ActivityLog(db.Model):
    __tablename__ = "activity_log"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    action = db.Column(db.String(120), nullable=False)   # short label, e.g. "Resume uploaded"
    detail = db.Column(db.String(255))                    # e.g. "resume_final_v3.pdf — scored 87"
    icon = db.Column(db.String(20), default="doc")        # doc / interview / skill / account

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="activity_logs")

    @staticmethod
    def log(user_id, action, detail=None, icon="doc"):
        entry = ActivityLog(user_id=user_id, action=action, detail=detail, icon=icon)
        db.session.add(entry)
        db.session.commit()
        return entry
