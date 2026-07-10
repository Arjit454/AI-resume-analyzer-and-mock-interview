from utils.role_data import JOB_ROLES


def match_jobs(user_skills):
    """
    Scores every role in JOB_ROLES against a set of the user's detected
    skills. Returns a list of dicts sorted by match percentage, highest first.
    """
    user_skills = set(user_skills)
    results = []

    for title, data in JOB_ROLES.items():
        role_skills = set(data["skills"])
        matched = sorted(user_skills & role_skills)
        match_pct = round(len(matched) / len(role_skills) * 100) if role_skills else 0
        results.append({
            "title": title,
            "blurb": data["blurb"],
            "matched": matched,
            "missing": sorted(role_skills - user_skills),
            "match_pct": match_pct,
        })

    results.sort(key=lambda r: r["match_pct"], reverse=True)
    return results
