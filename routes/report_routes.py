from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.resume import Resume
from models.interview import InterviewSession
from models.roadmap import LearningRoadmap
from utils.job_matcher import match_jobs

report_bp = Blueprint("report", __name__)

INTERVIEW_CATEGORY_LABELS = {
    "grammar_score": "Grammar",
    "confidence_score": "Confidence",
    "technical_score": "Technical",
    "communication_score": "Communication",
    "problem_solving_score": "Problem solving",
}

ATS_CATEGORY_LABELS = {
    "contact_information": "Contact info",
    "education": "Education",
    "experience": "Experience",
    "projects": "Projects",
    "skills": "Skills",
    "formatting": "Formatting",
    "keywords": "Keywords",
    "length": "Length",
}


@report_bp.route("/report")
@login_required
def index():
    resume = (
        Resume.query.filter_by(user_id=current_user.id)
        .order_by(Resume.created_at.desc())
        .first()
    )
    interview = (
        InterviewSession.query.filter_by(user_id=current_user.id, status="completed")
        .order_by(InterviewSession.created_at.desc())
        .first()
    )
    roadmap = LearningRoadmap.query.filter_by(user_id=current_user.id).first()

    has_resume = bool(resume and resume.is_analyzed)
    has_interview = bool(interview)

    # --- overall score: weighted blend of resume quality and interview performance ---
    overall_score = None
    if has_resume and has_interview:
        overall_score = round(resume.resume_score * 0.6 + interview.overall_score * 0.4)
    elif has_resume:
        overall_score = resume.resume_score
    elif has_interview:
        overall_score = interview.overall_score

    # --- strengths / weaknesses: resume's AI output, plus a couple of
    #     interview-derived call-outs based on clear score thresholds ---
    strengths = list(resume.strengths_list()) if has_resume else []
    weaknesses = list(resume.weaknesses_list()) if has_resume else []

    if has_interview:
        for field, label in INTERVIEW_CATEGORY_LABELS.items():
            score = getattr(interview, field)
            if score >= 80:
                strengths.append(f"Strong {label.lower()} in mock interview answers ({score}/100)")
            elif score < 55:
                weaknesses.append(f"{label} needs work in interview answers ({score}/100)")

    recommended_improvements = []
    if has_resume:
        recommended_improvements.extend(resume.formatting_suggestions_list())
        recommended_improvements.extend(resume.grammar_suggestions_list())
        if resume.missing_skills_list():
            skills = ", ".join(resume.missing_skills_list()[:4])
            recommended_improvements.append(f"Close skill gaps in: {skills}")
    if not recommended_improvements:
        recommended_improvements = [
            "Upload and analyze a resume to get specific, tailored improvement suggestions here."
        ]

    # --- job suggestions, reusing the same matcher as the Job Recommendations page ---
    job_suggestions = match_jobs(resume.skills_list())[:3] if has_resume else []

    # --- chart data ---
    ats_chart_labels, ats_chart_data = [], []
    if has_resume:
        breakdown = resume.ats_breakdown_dict()
        for key, label in ATS_CATEGORY_LABELS.items():
            item = breakdown.get(key, {"score": 0, "max": 1})
            pct = round((item["score"] / item["max"]) * 100) if item.get("max") else 0
            ats_chart_labels.append(label)
            ats_chart_data.append(pct)

    interview_chart_labels = list(INTERVIEW_CATEGORY_LABELS.values()) if has_interview else []
    interview_chart_data = (
        [getattr(interview, field) for field in INTERVIEW_CATEGORY_LABELS] if has_interview else []
    )

    return render_template(
        "report.html",
        has_resume=has_resume,
        has_interview=has_interview,
        resume=resume,
        interview=interview,
        roadmap=roadmap,
        overall_score=overall_score,
        strengths=strengths,
        weaknesses=weaknesses,
        recommended_improvements=recommended_improvements,
        job_suggestions=job_suggestions,
        ats_chart_labels=ats_chart_labels,
        ats_chart_data=ats_chart_data,
        interview_chart_labels=interview_chart_labels,
        interview_chart_data=interview_chart_data,
    )
