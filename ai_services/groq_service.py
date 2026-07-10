import json
from flask import current_app

ANALYSIS_SCHEMA_EXAMPLE = """{
  "strengths": ["short point", "short point", "short point"],
  "weaknesses": ["short point", "short point"],
  "grammar_suggestions": ["short point", "short point"],
  "formatting_suggestions": ["short point", "short point"],
  "missing_skills": ["Skill A", "Skill B", "Skill C"],
  "recommended_technologies": ["Tech A", "Tech B"],
  "best_job_role": "Role name",
  "career_advice": "Two to three sentences of direct, practical advice.",
  "learning_path": ["Week 1: topic", "Week 2: topic", "Week 3: topic", "Week 4: topic"]
}"""


def _build_prompt(resume_text):
    return f"""You are an experienced technical recruiter and career coach reviewing a
student's resume. Read the resume text below and respond with ONLY a valid JSON
object — no markdown fences, no commentary before or after — matching exactly
this shape:

{ANALYSIS_SCHEMA_EXAMPLE}

Rules:
- strengths: 3-5 concrete things this resume does well.
- weaknesses: 2-4 concrete gaps or issues, specific to this resume.
- grammar_suggestions: specific wording/grammar fixes, or an empty list if writing is clean.
- formatting_suggestions: specific layout/structure fixes, or an empty list if formatting is fine.
- missing_skills: skills relevant to this candidate's apparent target field that aren't in the resume.
- recommended_technologies: technologies worth learning next, given their current skillset.
- best_job_role: the single job title that fits this resume best right now.
- career_advice: direct and specific, not generic platitudes.
- learning_path: an 8-item list, one per week, building toward the missing skills.

Resume text:
\"\"\"
{resume_text[:6000]}
\"\"\"
"""


def analyze_resume_with_ai(resume_text):
    """
    Returns (data, error). data is a dict matching ANALYSIS_SCHEMA_EXAMPLE on
    success, or None on failure — error is a short, user-facing message.
    """
    api_key = current_app.config.get("GROQ_API_KEY")
    if not api_key:
        return None, (
            "AI analysis isn't set up yet. Add a free GROQ_API_KEY to your .env "
            "file (get one at console.groq.com) to enable this."
        )

    try:
        from groq import Groq
    except ImportError:
        return None, "The groq package isn't installed. Run: pip install groq"

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=current_app.config.get("GROQ_MODEL", "openai/gpt-oss-120b"),
            messages=[{"role": "user", "content": _build_prompt(resume_text)}],
            temperature=0.4,
            max_tokens=1500,
        )
        raw = completion.choices[0].message.content.strip()
        raw = _strip_code_fences(raw)
        data = json.loads(raw)
        return _normalize(data), None

    except json.JSONDecodeError:
        return None, "The AI response wasn't valid JSON. Please try analyzing again."
    except Exception as exc:
        current_app.logger.exception("Groq analysis failed")
        return None, f"AI analysis failed: {exc}"


def _strip_code_fences(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return text.strip()


def _normalize(data):
    """Fills in safe defaults for any keys the model might have skipped,
    so templates never have to guard against missing keys."""
    return {
        "strengths": data.get("strengths") or [],
        "weaknesses": data.get("weaknesses") or [],
        "grammar_suggestions": data.get("grammar_suggestions") or [],
        "formatting_suggestions": data.get("formatting_suggestions") or [],
        "missing_skills": data.get("missing_skills") or [],
        "recommended_technologies": data.get("recommended_technologies") or [],
        "best_job_role": data.get("best_job_role") or "Not determined",
        "career_advice": data.get("career_advice") or "",
        "learning_path": data.get("learning_path") or [],
    }
