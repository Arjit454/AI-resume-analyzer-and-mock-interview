import re

FILLER_WORDS = ["um", "uh", "like", "you know", "sort of", "kind of", "basically", "actually"]
HEDGE_PHRASES = ["i think", "maybe", "i guess", "not sure", "probably", "i don't know"]
DECISIVE_PHRASES = ["i am confident", "definitely", "certainly", "i led", "i built", "i solved", "i decided"]
STRUCTURE_WORDS = ["first", "second", "then", "finally", "next", "after that"]
REASONING_WORDS = ["because", "therefore", "approach", "trade-off", "alternative", "so that", "in order to"]
STAR_WORDS = ["situation", "task", "action", "result", "outcome", "impact"]


def _clamp(value):
    return max(0, min(100, round(value)))


def _count_hits(text_lower, phrases):
    return sum(1 for p in phrases if p in text_lower)


def evaluate_answer(question_type, keywords, answer_text):
    """
    Deterministic, always-available scoring — used directly when no
    GROQ_API_KEY is set, and as a safety net if the AI call fails.
    Returns a dict with the five category scores (0-100) plus feedback.
    """
    text = (answer_text or "").strip()
    text_lower = text.lower()
    word_count = len(text.split())

    if word_count == 0:
        return {
            "grammar": 0, "confidence": 0, "technical": 0,
            "communication": 0, "problem_solving": 0,
            "feedback": "No answer was given — an empty response scores zero everywhere.",
        }

    # --- grammar ---
    grammar = 80
    if word_count < 5:
        grammar -= 20
    filler_hits = _count_hits(text_lower, FILLER_WORDS)
    grammar -= min(filler_hits * 5, 20)
    if re.search(r"[.!?]", text):
        grammar += 5
    grammar = _clamp(grammar)

    # --- confidence ---
    confidence = 75
    hedge_hits = _count_hits(text_lower, HEDGE_PHRASES)
    confidence -= min(hedge_hits * 8, 30)
    decisive_hits = _count_hits(text_lower, DECISIVE_PHRASES)
    confidence += min(decisive_hits * 8, 20)
    confidence = _clamp(confidence)

    # --- communication ---
    if word_count < 15:
        communication = 40 + word_count
    elif word_count > 300:
        communication = 60
    else:
        communication = 85
    structure_hits = _count_hits(text_lower, STRUCTURE_WORDS)
    communication += min(structure_hits * 3, 10)
    communication = _clamp(communication)

    # --- technical + problem solving ---
    if question_type == "technical":
        keyword_hits = sum(1 for k in keywords if k.lower() in text_lower)
        technical = 45 + min(keyword_hits * 12, 55)

        reasoning_hits = _count_hits(text_lower, REASONING_WORDS)
        problem_solving = 45 + min(reasoning_hits * 10, 35) + min(keyword_hits * 5, 20)
    else:
        # HR / behavioral question — technical score isn't really meaningful
        # here, so it mirrors confidence rather than unfairly tanking the average
        technical = confidence

        # behavioral answers show problem-solving through structured
        # storytelling (STAR method), so score that instead of keywords
        star_hits = _count_hits(text_lower, STAR_WORDS)
        problem_solving = 50 + min(star_hits * 10, 40) + min(structure_hits * 3, 10)

    technical = _clamp(technical)
    problem_solving = _clamp(problem_solving)

    # --- feedback: point at the weakest category ---
    scores = {
        "grammar": grammar, "confidence": confidence, "technical": technical,
        "communication": communication, "problem_solving": problem_solving,
    }
    weakest = min(scores, key=scores.get)
    feedback = _feedback_for(weakest, question_type)

    return {**scores, "feedback": feedback}


def _feedback_for(category, question_type):
    tips = {
        "grammar": "Watch out for filler words like 'um' or 'like' — pausing silently reads as more confident than filling the gap.",
        "confidence": "Try stating your point directly rather than hedging with 'I think' or 'maybe' — own your answer.",
        "communication": "Aim for a focused 2-4 sentence answer — long enough to show substance, short enough to stay sharp.",
        "technical": "Try naming the specific concepts or tools involved — precision reads as expertise.",
        "problem_solving": (
            "Structure your answer with the STAR method: Situation, Task, Action, Result."
            if question_type == "hr"
            else "Walk through your reasoning step by step, and mention any trade-offs you considered."
        ),
    }
    return tips.get(category, "Solid answer overall.")
