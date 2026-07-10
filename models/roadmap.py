import json
from datetime import datetime
from app import db

DEFAULT_ROADMAP = [
    "Week 1: Python revision — syntax, data structures, OOP basics",
    "Week 2: SQL — queries, joins, schema design",
    "Week 3: Data Structures & Algorithms — arrays, trees, complexity",
    "Week 4: Flask — routes, templates, REST APIs",
    "Week 5: Docker — containers, images, docker-compose",
    "Week 6: Build a portfolio project end-to-end",
    "Week 7: Interview preparation — mock HR and technical rounds",
    "Week 8: Deployment — CI/CD, hosting, final polish",
]


class LearningRoadmap(db.Model):
    __tablename__ = "learning_roadmaps"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    source = db.Column(db.String(20), default="default")  # "default" or "ai"
    items_json = db.Column(db.Text)             # JSON list of 8 "Week N: ..." strings
    completed_weeks = db.Column(db.String(50), default="")  # comma-separated week numbers

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("roadmap", uselist=False))

    def items(self):
        try:
            return json.loads(self.items_json or "[]")
        except (ValueError, TypeError):
            return []

    def completed_weeks_list(self):
        return [int(w) for w in (self.completed_weeks or "").split(",") if w.strip().isdigit()]

    def is_week_completed(self, week_number):
        return week_number in self.completed_weeks_list()

    def toggle_week(self, week_number):
        completed = set(self.completed_weeks_list())
        if week_number in completed:
            completed.remove(week_number)
        else:
            completed.add(week_number)
        self.completed_weeks = ",".join(str(w) for w in sorted(completed))
        return week_number in completed

    def progress_percent(self):
        total = len(self.items())
        if not total:
            return 0
        return round(len(self.completed_weeks_list()) / total * 100)

    @staticmethod
    def get_or_create_default(user_id):
        roadmap = LearningRoadmap.query.filter_by(user_id=user_id).first()
        if roadmap:
            return roadmap
        roadmap = LearningRoadmap(
            user_id=user_id,
            source="default",
            items_json=json.dumps(DEFAULT_ROADMAP),
            completed_weeks="",
        )
        db.session.add(roadmap)
        db.session.commit()
        return roadmap

    @staticmethod
    def replace_with_ai_plan(user_id, learning_path_items):
        """Called after a successful AI resume analysis — swaps in the
        personalized 8-week plan the AI generated, starting progress over."""
        roadmap = LearningRoadmap.query.filter_by(user_id=user_id).first()
        items = learning_path_items or DEFAULT_ROADMAP
        if roadmap:
            roadmap.source = "ai"
            roadmap.items_json = json.dumps(items)
            roadmap.completed_weeks = ""
        else:
            roadmap = LearningRoadmap(
                user_id=user_id, source="ai",
                items_json=json.dumps(items), completed_weeks="",
            )
            db.session.add(roadmap)
        db.session.commit()
        return roadmap
