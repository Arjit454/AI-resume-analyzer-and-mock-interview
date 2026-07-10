from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from models.resume import Resume
from models.activity import ActivityLog
from utils.role_data import TARGET_ROLES
from utils.job_matcher import match_jobs

career_bp = Blueprint("career", __name__)


def _get_active_resume():
    """The resume the skill gap / job recommendation features work off of —
    just the most recently uploaded one, for now."""
    return (
        Resume.query.filter_by(user_id=current_user.id)
        .order_by(Resume.created_at.desc())
        .first()
    )


@career_bp.route("/skill-gap", methods=["GET", "POST"])
@login_required
def skill_gap():
    resume = _get_active_resume()

    if request.method == "POST":
        if not resume:
            flash("Upload a resume first so we have skills to compare.", "error")
            return redirect(url_for("resume.upload_page"))

        role = request.form.get("role")
        if role not in TARGET_ROLES:
            flash("Please choose a valid target role.", "error")
            return redirect(url_for("career.skill_gap"))

        resume.target_role = role
        db.session.commit()
        ActivityLog.log(
            current_user.id, "Skill gap analyzed", f"Target role: {role}", icon="skill"
        )
        return redirect(url_for("career.skill_gap", role=role))

    role = request.args.get("role")
    result = None

    if resume and role and role in TARGET_ROLES:
        user_skills = set(resume.skills_list())
        role_skills = TARGET_ROLES[role]

        available = []
        missing = []
        for skill, meta in role_skills.items():
            if skill in user_skills:
                available.append(skill)
            else:
                missing.append({"skill": skill, **meta})

        # highest priority gaps first, so the most important thing to learn is on top
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        missing.sort(key=lambda m: priority_order.get(m["priority"], 3))

        coverage = round(len(available) / len(role_skills) * 100) if role_skills else 0

        result = {
            "role": role,
            "available": available,
            "missing": missing,
            "coverage": coverage,
        }

    return render_template(
        "skill_gap.html",
        roles=TARGET_ROLES.keys(),
        resume=resume,
        selected_role=role,
        result=result,
    )


@career_bp.route("/jobs")
@login_required
def job_recommendations():
    resume = _get_active_resume()
    recommendations = []

    if resume:
        recommendations = match_jobs(resume.skills_list())

    return render_template("jobs.html", resume=resume, recommendations=recommendations)
