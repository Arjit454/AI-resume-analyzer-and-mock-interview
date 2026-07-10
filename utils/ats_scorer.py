import re

ACTION_VERBS = [
    "developed", "built", "designed", "implemented", "led", "managed",
    "created", "optimized", "improved", "automated", "deployed", "engineered",
    "launched", "reduced", "increased", "analyzed", "collaborated", "architected",
]

IDEAL_LENGTH_MIN = 1200   # characters — roughly a focused one-page resume
IDEAL_LENGTH_MAX = 6000   # roughly a dense two-pager


def _section_score(section_text, max_points, good_length=150):
    """Length-based partial credit: empty section = 0, a solid paragraph
    or more = full marks, in between scales linearly."""
    length = len((section_text or "").strip())
    if length == 0:
        return 0
    return round(min(length / good_length, 1) * max_points, 1)


def score_resume(resume):
    """
    Takes a Resume model instance and returns (total_score, breakdown dict).
    Every sub-score is transparent and re-derivable from the resume itself —
    no black box here, unlike the AI writeup.
    """
    breakdown = {}

    # --- contact information (10 pts) ---
    contact_pts = 0
    if resume.candidate_name:
        contact_pts += 3
    if resume.candidate_email:
        contact_pts += 4
    if resume.candidate_phone:
        contact_pts += 3
    breakdown["contact_information"] = {"score": contact_pts, "max": 10}

    # --- education (10 pts) ---
    edu_pts = _section_score(resume.education, 10, good_length=80)
    breakdown["education"] = {"score": edu_pts, "max": 10}

    # --- experience (15 pts) ---
    exp_pts = _section_score(resume.experience, 15, good_length=200)
    breakdown["experience"] = {"score": exp_pts, "max": 15}

    # --- projects (15 pts) ---
    proj_pts = _section_score(resume.projects, 15, good_length=200)
    breakdown["projects"] = {"score": proj_pts, "max": 15}

    # --- skills (15 pts) ---
    skill_count = len(resume.skills_list())
    skill_pts = round(min(skill_count / 10, 1) * 15, 1)
    breakdown["skills"] = {"score": skill_pts, "max": 15}

    # --- formatting (15 pts) — reward having clearly separated sections ---
    sections_present = sum([
        bool((resume.education or "").strip()),
        bool((resume.experience or "").strip()),
        bool((resume.projects or "").strip()),
        bool((resume.extracted_skills or "").strip()),
    ])
    formatting_pts = round((sections_present / 4) * 15, 1)
    breakdown["formatting"] = {"score": formatting_pts, "max": 15}

    # --- keywords (10 pts) — action verbs used, a decent proxy for strong bullet points ---
    text_lower = (resume.raw_text or "").lower()
    verb_hits = sum(1 for verb in ACTION_VERBS if verb in text_lower)
    keyword_pts = round(min(verb_hits / 6, 1) * 10, 1)
    breakdown["keywords"] = {"score": keyword_pts, "max": 10}

    # --- length (10 pts) — penalize resumes that are too thin or way too long ---
    text_len = len((resume.raw_text or "").strip())
    if text_len == 0:
        length_pts = 0
    elif IDEAL_LENGTH_MIN <= text_len <= IDEAL_LENGTH_MAX:
        length_pts = 10
    elif text_len < IDEAL_LENGTH_MIN:
        length_pts = round((text_len / IDEAL_LENGTH_MIN) * 10, 1)
    else:
        overflow = text_len - IDEAL_LENGTH_MAX
        length_pts = max(round(10 - (overflow / 1500), 1), 3)
    breakdown["length"] = {"score": length_pts, "max": 10}

    total = round(sum(v["score"] for v in breakdown.values()))
    total = max(0, min(total, 100))

    return total, breakdown
