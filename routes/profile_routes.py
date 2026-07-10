import os
import uuid

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user, logout_user
from werkzeug.utils import secure_filename

from app import db
from models.user import User
from models.resume import Resume
from models.interview import InterviewSession, InterviewAnswer
from models.activity import ActivityLog
from models.roadmap import LearningRoadmap

profile_bp = Blueprint("profile", __name__)

ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "webp"}


@profile_bp.route("/profile")
@login_required
def index():
    return render_template("profile.html")


@profile_bp.route("/profile/update", methods=["POST"])
@login_required
def update_info():
    name = request.form.get("name", "").strip()
    language = request.form.get("language", "English")
    notify_enabled = bool(request.form.get("notify_enabled"))

    if len(name) < 2:
        flash("Please enter a valid name.", "error")
        return redirect(url_for("profile.index"))

    current_user.name = name
    current_user.language = language
    current_user.notify_enabled = notify_enabled
    db.session.commit()

    flash("Profile updated.", "success")
    return redirect(url_for("profile.index"))


@profile_bp.route("/profile/photo", methods=["POST"])
@login_required
def upload_photo():
    file = request.files.get("photo")
    if not file or file.filename == "":
        flash("No image selected.", "error")
        return redirect(url_for("profile.index"))

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_IMAGE_EXT:
        flash("Please upload a PNG, JPG, or WEBP image.", "error")
        return redirect(url_for("profile.index"))

    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], "profile_photos")
    os.makedirs(folder, exist_ok=True)

    filename = secure_filename(f"user_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}")
    file.save(os.path.join(folder, filename))

    current_user.profile_photo = filename
    db.session.commit()

    flash("Profile photo updated.", "success")
    return redirect(url_for("profile.index"))


@profile_bp.route("/profile/change-password", methods=["POST"])
@login_required
def change_password():
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not current_user.check_password(current_password):
        flash("Current password is incorrect.", "error")
    elif len(new_password) < 6:
        flash("New password must be at least 6 characters.", "error")
    elif new_password != confirm_password:
        flash("New passwords don't match.", "error")
    else:
        current_user.set_password(new_password)
        db.session.commit()
        flash("Password changed successfully.", "success")

    return redirect(url_for("profile.index"))


@profile_bp.route("/profile/theme", methods=["POST"])
@login_required
def update_theme():
    """Fire-and-forget endpoint the navbar toggle calls, so theme choice
    persists across devices instead of only living in localStorage."""
    theme = request.json.get("theme") if request.is_json else request.form.get("theme")
    if theme not in ("dark", "light"):
        return jsonify(success=False), 400
    current_user.theme_pref = theme
    db.session.commit()
    return jsonify(success=True)


@profile_bp.route("/profile/delete-account", methods=["POST"])
@login_required
def delete_account():
    password = request.form.get("password", "")
    if not current_user.check_password(password):
        flash("Incorrect password — account not deleted.", "error")
        return redirect(url_for("profile.index"))

    user_id = current_user.id

    # clean up dependent rows manually — SQLite doesn't enforce
    # cascading deletes by default
    session_ids = [s.id for s in InterviewSession.query.filter_by(user_id=user_id).all()]
    if session_ids:
        InterviewAnswer.query.filter(InterviewAnswer.session_id.in_(session_ids)).delete(
            synchronize_session=False
        )
    InterviewSession.query.filter_by(user_id=user_id).delete(synchronize_session=False)
    Resume.query.filter_by(user_id=user_id).delete(synchronize_session=False)
    ActivityLog.query.filter_by(user_id=user_id).delete(synchronize_session=False)
    LearningRoadmap.query.filter_by(user_id=user_id).delete(synchronize_session=False)

    user = User.query.get(user_id)
    logout_user()
    db.session.delete(user)
    db.session.commit()

    flash("Your account and all associated data have been deleted.", "info")
    return redirect(url_for("main.index"))
