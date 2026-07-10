import json
from flask import current_app

from utils.interview_scorer import evaluate_answer as rule_based_evaluate


def _build_prompt(question, answer, question_type, difficulty):
    return f"""You are an experienced interviewer scoring a candidate's answer in a
{difficulty} difficulty {question_type} interview round. Respond with ONLY a
valid JSON object — no markdown, no commentary — matching exactly this shape:

{{
  "grammar": 0-100,
  "confidence": 0-100,
  "technical": 0-100,
  "communication": 0-100,
  "problem_solving": 0-100,
  "feedback": "one or two direct, specific sentences of feedback"
}}

Scoring guidance:
- grammar: sentence structure, filler words, clarity of language.
- confidence: decisiveness of tone, hedging language, ownership of the answer.
- technical: accuracy and depth of technical content (for HR questions, judge overall substance instead).
- communication: structure, conciseness, whether the answer actually addresses the question.
- problem_solving: quality of reasoning — for behavioral questions, reward STAR-style structure (Situation, Task, Action, Result).

Question: {question}

Candidate's answer:
\"\"\"
{answer[:2000]}
\"\"\"
"""


def evaluate_answer_ai(question, answer, question_type, difficulty, keywords):
    """
    Tries Groq first; falls back to the deterministic rule-based scorer if
    no API key is configured or the call fails for any reason. Returns
    (scores_dict, used_ai: bool).
    """
    api_key = current_app.config.get("GROQ_API_KEY")
    if not api_key:
        return rule_based_evaluate(question_type, keywords, answer), False

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=current_app.config.get("GROQ_MODEL", "openai/gpt-oss-120b"),
            messages=[{"role": "user", "content": _build_prompt(question, answer, question_type, difficulty)}],
            temperature=0.3,
            max_tokens=400,
        )
        raw = completion.choices[0].message.content.strip()
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:]
        data = json.loads(raw.strip())

        scores = {
            "grammar": int(data.get("grammar", 0)),
            "confidence": int(data.get("confidence", 0)),
            "technical": int(data.get("technical", 0)),
            "communication": int(data.get("communication", 0)),
            "problem_solving": int(data.get("problem_solving", 0)),
            "feedback": data.get("feedback") or "No feedback provided.",
        }
        return scores, True

    except Exception:
        current_app.logger.exception("Groq interview scoring failed, falling back to rule-based")
        return rule_based_evaluate(question_type, keywords, answer), False
