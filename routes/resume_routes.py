import os
import json
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, current_app, abort, flash
from flask_login import login_required, current_user

from app import db
from models.resume import Resume
from models.activity import ActivityLog
from models.roadmap import LearningRoadmap
from utils.file_utils import allowed_file, save_upload
from utils.resume_parser import extract_text
from utils.resume_extractor import parse_resume
from utils.ats_scorer import score_resume
from ai_services.groq_service import analyze_resume_with_ai

resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/upload")
@login_required
def upload_page():
    return render_template("upload.html")


@resume_bp.route("/upload", methods=["POST"])
@login_required
def upload_file():
    if "resume" not in request.files:
        return jsonify(success=False, error="No file was sent."), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify(success=False, error="No file selected."), 400

    allowed = current_app.config["ALLOWED_EXTENSIONS"]
    if not allowed_file(file.filename, allowed):
        return jsonify(success=False, error="Only PDF and DOCX files are supported."), 400

    try:
        original_name, saved_path = save_upload(
            file, current_app.config["UPLOAD_FOLDER"], current_user.id
        )
        extension = original_name.rsplit(".", 1)[1].lower()

        raw_text = extract_text(saved_path, extension)
        if not raw_text or len(raw_text.strip()) < 30:
            return jsonify(
                success=False,
                error="Couldn't read text from this file. Try a text-based PDF or DOCX, not a scanned image.",
            ), 422

        parsed = parse_resume(raw_text)

        resume = Resume(
            user_id=current_user.id,
            filename=original_name,
            file_path=saved_path,
            candidate_name=parsed["name"],
            candidate_email=parsed["email"],
            candidate_phone=parsed["phone"],
            education=parsed["education"],
            experience=parsed["experience"],
            projects=parsed["projects"],
            certifications=parsed["certifications"],
            extracted_skills=", ".join(parsed["skills"]),
            raw_text=parsed["raw_text"],
        )
        db.session.add(resume)
        db.session.commit()

        ActivityLog.log(
            current_user.id,
            "Resume uploaded",
            f"{original_name} — {len(parsed['skills'])} skills detected",
            icon="doc",
        )

        return jsonify(success=True, resume_id=resume.id)

    except Exception as exc:
        current_app.logger.exception("Resume upload failed")
        return jsonify(success=False, error="Something went wrong while processing this file."), 500


@resume_bp.route("/resume/<int:resume_id>")
@login_required
def resume_detail(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)
    return render_template("resume_detail.html", resume=resume)


@resume_bp.route("/resume/<int:resume_id>/analyze", methods=["POST"])
@login_required
def analyze_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)

    # rule-based ATS score — always runs, no API key required
    ats_total, ats_breakdown = score_resume(resume)
    resume.ats_score = ats_total
    resume.ats_breakdown = json.dumps(ats_breakdown)

    # AI analysis — needs GROQ_API_KEY, degrades gracefully without one
    ai_data, ai_error = analyze_resume_with_ai(resume.raw_text or "")

    if ai_data:
        resume.strengths = json.dumps(ai_data["strengths"])
        resume.weaknesses = json.dumps(ai_data["weaknesses"])
        resume.grammar_suggestions = json.dumps(ai_data["grammar_suggestions"])
        resume.formatting_suggestions = json.dumps(ai_data["formatting_suggestions"])
        resume.recommended_technologies = json.dumps(ai_data["recommended_technologies"])
        resume.best_job_role = ai_data["best_job_role"][:150]
        resume.career_advice = ai_data["career_advice"]
        resume.learning_path = json.dumps(ai_data["learning_path"])
        resume.missing_skills = ", ".join(ai_data["missing_skills"])

        # a simple, distinct "quality" score that reacts to what the AI found,
        # not just the mechanical ATS checks
        quality_adjustment = (len(ai_data["strengths"]) - len(ai_data["weaknesses"])) * 3
        resume.resume_score = max(0, min(100, ats_total + quality_adjustment))

        LearningRoadmap.replace_with_ai_plan(current_user.id, ai_data["learning_path"])
    else:
        # still record the ATS score even if AI analysis couldn't run
        resume.resume_score = ats_total
        flash(ai_error, "info")

    resume.analyzed_at = datetime.utcnow()
    db.session.commit()

    ActivityLog.log(
        current_user.id,
        "Resume analyzed",
        f"{resume.filename} — ATS score {ats_total}",
        icon="doc",
    )

    return jsonify(success=True, ai_error=ai_error)
