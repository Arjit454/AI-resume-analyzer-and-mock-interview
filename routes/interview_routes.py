import json
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from models.interview import InterviewSession, InterviewAnswer
from models.activity import ActivityLog
from utils.interview_bank import get_questions, SESSION_LENGTH
from ai_services.interview_ai import evaluate_answer_ai

interview_bp = Blueprint("interview", __name__)

VALID_MODES = {"hr", "technical", "mixed"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}


@interview_bp.route("/interview/setup")
@login_required
def setup():
    return render_template("interview_setup.html")


@interview_bp.route("/interview/start", methods=["POST"])
@login_required
def start():
    mode = request.form.get("mode")
    difficulty = request.form.get("difficulty")

    if mode not in VALID_MODES or difficulty not in VALID_DIFFICULTIES:
        flash("Please choose a valid interview type and difficulty.", "error")
        return redirect(url_for("interview.setup"))

    questions = get_questions(mode, difficulty)

    session = InterviewSession(
        user_id=current_user.id,
        mode=mode,
        difficulty=difficulty,
        questions_json=json.dumps(questions),
        questions_total=len(questions),
        current_index=0,
        status="in_progress",
    )
    db.session.add(session)
    db.session.commit()

    return redirect(url_for("interview.question", session_id=session.id))


@interview_bp.route("/interview/<int:session_id>/question")
@login_required
def question(session_id):
    session = InterviewSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(403)

    if session.is_complete:
        return redirect(url_for("interview.result", session_id=session.id))

    current_q = session.current_question()
    if current_q is None:
        return redirect(url_for("interview.result", session_id=session.id))

    return render_template(
        "interview_question.html",
        session=session,
        current_q=current_q,
        question_number=session.current_index + 1,
    )


@interview_bp.route("/interview/<int:session_id>/answer", methods=["POST"])
@login_required
def answer(session_id):
    session = InterviewSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(403)
    if session.is_complete:
        return redirect(url_for("interview.result", session_id=session.id))

    current_q = session.current_question()
    if current_q is None:
        return redirect(url_for("interview.result", session_id=session.id))

    answer_text = request.form.get("answer", "").strip()
    if not answer_text:
        flash("Please write an answer before submitting.", "error")
        return redirect(url_for("interview.question", session_id=session.id))

    scores, used_ai = evaluate_answer_ai(
        current_q["question"], answer_text, current_q["type"],
        session.difficulty, current_q.get("keywords", []),
    )

    overall = round(
        (scores["grammar"] + scores["confidence"] + scores["technical"]
         + scores["communication"] + scores["problem_solving"]) / 5
    )

    record = InterviewAnswer(
        session_id=session.id,
        question_index=session.current_index,
        question_text=current_q["question"],
        question_type=current_q["type"],
        answer_text=answer_text,
        grammar_score=scores["grammar"],
        confidence_score=scores["confidence"],
        technical_score=scores["technical"],
        communication_score=scores["communication"],
        problem_solving_score=scores["problem_solving"],
        overall_score=overall,
        feedback=scores["feedback"],
        scored_by_ai=used_ai,
    )
    db.session.add(record)

    session.current_index += 1
    if session.current_index >= session.questions_total:
        _finalize_session(session)

    db.session.commit()

    if session.is_complete:
        return redirect(url_for("interview.result", session_id=session.id))
    return redirect(url_for("interview.question", session_id=session.id))


def _finalize_session(session):
    answers = session.answers
    if not answers:
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        return

    def avg(field):
        return round(sum(getattr(a, field) for a in answers) / len(answers))

    session.grammar_score = avg("grammar_score")
    session.confidence_score = avg("confidence_score")
    session.technical_score = avg("technical_score")
    session.communication_score = avg("communication_score")
    session.problem_solving_score = avg("problem_solving_score")
    session.overall_score = avg("overall_score")
    session.status = "completed"
    session.completed_at = datetime.utcnow()

    ActivityLog.log(
        session.user_id,
        "Mock interview completed",
        f"{session.mode.title()} round ({session.difficulty}) — scored {session.overall_score}",
        icon="interview",
    )


@interview_bp.route("/interview/<int:session_id>/result")
@login_required
def result(session_id):
    session = InterviewSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(403)
    if not session.is_complete:
        return redirect(url_for("interview.question", session_id=session.id))

    return render_template("interview_result.html", session=session)


@interview_bp.route("/interview/history")
@login_required
def history():
    sessions = (
        InterviewSession.query.filter_by(user_id=current_user.id, status="completed")
        .order_by(InterviewSession.created_at.desc())
        .all()
    )
    return render_template("interview_history.html", sessions=sessions)
