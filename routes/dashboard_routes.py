from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from models.resume import Resume
from models.interview import InterviewSession
from models.activity import ActivityLog
from models.roadmap import LearningRoadmap

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def index():
    resumes = (
        Resume.query.filter_by(user_id=current_user.id)
        .order_by(Resume.created_at.asc())
        .all()
    )
    interviews = (
        InterviewSession.query.filter_by(user_id=current_user.id)
        .order_by(InterviewSession.created_at.asc())
        .all()
    )
    activity = (
        ActivityLog.query.filter_by(user_id=current_user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(6)
        .all()
    )

    latest_resume = resumes[-1] if resumes else None
    latest_interview = interviews[-1] if interviews else None

    # skill distribution — how many resumes mention each skill, top 6
    skill_counts = {}
    for r in resumes:
        for skill in r.skills_list():
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
    top_skills = sorted(skill_counts.items(), key=lambda kv: kv[1], reverse=True)[:6]

    # learning progress — prefer real roadmap completion once one exists;
    # otherwise fall back to skill coverage as a rough proxy
    roadmap = LearningRoadmap.query.filter_by(user_id=current_user.id).first()
    if roadmap:
        learning_progress = roadmap.progress_percent()
    else:
        missing_skills = latest_resume.missing_skills_list() if latest_resume else []
        have_skills = latest_resume.skills_list() if latest_resume else []
        total_relevant = len(have_skills) + len(missing_skills)
        learning_progress = (
            round(len(have_skills) / total_relevant * 100) if total_relevant else 0
        )
    missing_skills = latest_resume.missing_skills_list() if latest_resume else []

    context = {
        "user": current_user,
        "has_data": bool(resumes or interviews),
        "resume_score": latest_resume.resume_score if latest_resume else None,
        "ats_score": latest_resume.ats_score if latest_resume else None,
        "interview_score": latest_interview.overall_score if latest_interview else None,
        "latest_resume": latest_resume,
        "activity": activity,
        "missing_skills": missing_skills,
        "learning_progress": learning_progress,
        "ats_trend_labels": [r.created_at.strftime("%b %d") for r in resumes],
        "ats_trend_data": [r.ats_score for r in resumes],
        "interview_trend_labels": [i.created_at.strftime("%b %d") for i in interviews],
        "interview_trend_data": [i.overall_score for i in interviews],
        "skill_labels": [s for s, _ in top_skills],
        "skill_data": [c for _, c in top_skills],
    }
    return render_template("dashboard.html", **context)


@dashboard_bp.route("/dashboard/seed-demo", methods=["POST"])
@login_required
def seed_demo():
    """
    Fills in sample resumes / interviews / activity for the logged-in user
    so the dashboard can be seen fully populated before the upload and
    mock-interview features are wired up. Safe to call more than once —
    it just adds another round of sample data.
    """
    now = datetime.utcnow()

    sample_resumes = [
        (62, 58, "Python,SQL,HTML,CSS", "Docker,AWS,System Design"),
        (74, 70, "Python,SQL,HTML,CSS,Flask,Git", "Docker,AWS"),
        (87, 84, "Python,SQL,HTML,CSS,Flask,Git,Docker,REST APIs", "AWS,System Design"),
    ]
    for i, (ats, score, skills, missing) in enumerate(sample_resumes):
        db.session.add(Resume(
            user_id=current_user.id,
            filename=f"resume_v{i+1}.pdf",
            ats_score=ats,
            resume_score=score,
            extracted_skills=skills,
            missing_skills=missing,
            target_role="Full Stack Developer",
            created_at=now - timedelta(days=(len(sample_resumes) - i) * 6),
        ))

    sample_interviews = [
        ("hr", "easy", 65, 70, 60, 55, 68),
        ("technical", "medium", 72, 75, 68, 74, 70),
        ("mixed", "medium", 81, 82, 78, 80, 83),
    ]
    for i, (mode, diff, overall, grammar, conf, tech, comm) in enumerate(sample_interviews):
        db.session.add(InterviewSession(
            user_id=current_user.id,
            mode=mode,
            difficulty=diff,
            overall_score=overall,
            grammar_score=grammar,
            confidence_score=conf,
            technical_score=tech,
            communication_score=comm,
            created_at=now - timedelta(days=(len(sample_interviews) - i) * 4),
        ))

    db.session.commit()

    ActivityLog.log(current_user.id, "Resume uploaded", "resume_v3.pdf — scored 87", icon="doc")
    ActivityLog.log(current_user.id, "Mock interview completed", "Mixed round — scored 81", icon="interview")
    ActivityLog.log(current_user.id, "Skill gap analyzed", "Target role: Full Stack Developer", icon="skill")

    flash("Demo data loaded — here's what your dashboard looks like with real history.", "success")
    return redirect(url_for("dashboard.index"))
