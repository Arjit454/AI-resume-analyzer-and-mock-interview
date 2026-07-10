from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

from app import db
from models.roadmap import LearningRoadmap

learning_bp = Blueprint("learning", __name__)


@learning_bp.route("/learning")
@login_required
def index():
    roadmap = LearningRoadmap.get_or_create_default(current_user.id)
    weeks = [
        {"number": i + 1, "topic": topic, "completed": roadmap.is_week_completed(i + 1)}
        for i, topic in enumerate(roadmap.items())
    ]
    return render_template("learning.html", roadmap=roadmap, weeks=weeks)


@learning_bp.route("/learning/toggle/<int:week_number>", methods=["POST"])
@login_required
def toggle_week(week_number):
    roadmap = LearningRoadmap.get_or_create_default(current_user.id)
    if not (1 <= week_number <= len(roadmap.items())):
        return jsonify(success=False, error="Invalid week."), 400

    completed = roadmap.toggle_week(week_number)
    db.session.commit()

    return jsonify(success=True, completed=completed, progress=roadmap.progress_percent())
