"""
Static reference data for the Skill Gap Analyzer and Job Recommendation
features. Skill names here are kept in sync with SKILL_KEYWORDS in
utils/resume_extractor.py so they can actually be matched against what
gets pulled out of a resume.
"""

# target roles the user can pick in the Skill Gap Analyzer
TARGET_ROLES = {
    "Python Developer": {
        "Python": {"priority": "High", "difficulty": "Easy", "course": "Python for Everybody — Coursera"},
        "Flask": {"priority": "High", "difficulty": "Easy", "course": "Flask Mega-Tutorial — Miguel Grinberg"},
        "Django": {"priority": "Medium", "difficulty": "Medium", "course": "Django for Everybody — Coursera"},
        "SQL": {"priority": "High", "difficulty": "Easy", "course": "SQL for Data Science — Coursera"},
        "REST API": {"priority": "High", "difficulty": "Medium", "course": "REST APIs with Flask — freeCodeCamp"},
        "Git": {"priority": "High", "difficulty": "Easy", "course": "Git & GitHub Crash Course — freeCodeCamp"},
        "Docker": {"priority": "Medium", "difficulty": "Medium", "course": "Docker for Beginners — Docker Docs"},
        "PostgreSQL": {"priority": "Medium", "difficulty": "Medium", "course": "PostgreSQL Tutorial — freeCodeCamp"},
        "Pytest": {"priority": "Low", "difficulty": "Easy", "course": "Testing with Pytest — Real Python"},
        "AWS": {"priority": "Medium", "difficulty": "Hard", "course": "AWS Cloud Practitioner — AWS Skill Builder"},
    },
    "AI Engineer": {
        "Python": {"priority": "High", "difficulty": "Easy", "course": "Python for Everybody — Coursera"},
        "Machine Learning": {"priority": "High", "difficulty": "Hard", "course": "Machine Learning Specialization — Andrew Ng"},
        "Deep Learning": {"priority": "High", "difficulty": "Hard", "course": "Deep Learning Specialization — Andrew Ng"},
        "TensorFlow": {"priority": "High", "difficulty": "Medium", "course": "TensorFlow Developer Certificate — Coursera"},
        "PyTorch": {"priority": "Medium", "difficulty": "Medium", "course": "PyTorch for Deep Learning — freeCodeCamp"},
        "Pandas": {"priority": "High", "difficulty": "Easy", "course": "Data Analysis with Pandas — Kaggle"},
        "NumPy": {"priority": "High", "difficulty": "Easy", "course": "NumPy Fundamentals — Kaggle"},
        "NLP": {"priority": "Medium", "difficulty": "Hard", "course": "NLP Specialization — Coursera"},
        "Computer Vision": {"priority": "Medium", "difficulty": "Hard", "course": "CS231n — Stanford (free lectures)"},
        "Docker": {"priority": "Low", "difficulty": "Medium", "course": "Docker for Beginners — Docker Docs"},
        "AWS": {"priority": "Low", "difficulty": "Hard", "course": "AWS Machine Learning Foundations — AWS"},
    },
    "Full Stack Developer": {
        "HTML": {"priority": "High", "difficulty": "Easy", "course": "HTML Full Course — freeCodeCamp"},
        "CSS": {"priority": "High", "difficulty": "Easy", "course": "CSS Full Course — freeCodeCamp"},
        "JavaScript": {"priority": "High", "difficulty": "Medium", "course": "JavaScript Algorithms — freeCodeCamp"},
        "React": {"priority": "High", "difficulty": "Medium", "course": "React — The Complete Guide"},
        "Node.js": {"priority": "High", "difficulty": "Medium", "course": "Node.js Full Course — freeCodeCamp"},
        "Express": {"priority": "Medium", "difficulty": "Easy", "course": "Express.js Crash Course — Traversy Media"},
        "MongoDB": {"priority": "Medium", "difficulty": "Easy", "course": "MongoDB University — free courses"},
        "SQL": {"priority": "Medium", "difficulty": "Easy", "course": "SQL for Data Science — Coursera"},
        "Git": {"priority": "High", "difficulty": "Easy", "course": "Git & GitHub Crash Course — freeCodeCamp"},
        "REST API": {"priority": "High", "difficulty": "Medium", "course": "REST API Design — freeCodeCamp"},
        "Docker": {"priority": "Low", "difficulty": "Medium", "course": "Docker for Beginners — Docker Docs"},
    },
    "Data Analyst": {
        "SQL": {"priority": "High", "difficulty": "Easy", "course": "SQL for Data Science — Coursera"},
        "Excel": {"priority": "High", "difficulty": "Easy", "course": "Excel Skills for Business — Coursera"},
        "Python": {"priority": "High", "difficulty": "Easy", "course": "Python for Everybody — Coursera"},
        "Pandas": {"priority": "High", "difficulty": "Easy", "course": "Data Analysis with Pandas — Kaggle"},
        "NumPy": {"priority": "Medium", "difficulty": "Easy", "course": "NumPy Fundamentals — Kaggle"},
        "Tableau": {"priority": "High", "difficulty": "Medium", "course": "Tableau for Beginners — Tableau Public"},
        "Power BI": {"priority": "High", "difficulty": "Medium", "course": "Power BI for Beginners — Microsoft Learn"},
        "Data Analysis": {"priority": "High", "difficulty": "Medium", "course": "Google Data Analytics Certificate"},
    },
}

# roles considered for the Job Recommendation feature — a broader set,
# scored by skill overlap rather than picked by the user
JOB_ROLES = {
    "ML Engineer": {
        "skills": ["Python", "Machine Learning", "TensorFlow", "PyTorch", "Docker", "AWS"],
        "blurb": "Builds and deploys machine learning models into production systems.",
    },
    "Backend Developer": {
        "skills": ["Python", "Flask", "Django", "SQL", "REST API", "Docker", "Git"],
        "blurb": "Builds and maintains the server-side logic and APIs behind an application.",
    },
    "Data Scientist": {
        "skills": ["Python", "Pandas", "NumPy", "Machine Learning", "SQL", "Data Analysis"],
        "blurb": "Turns raw data into insights and predictive models that guide decisions.",
    },
    "AI Engineer": {
        "skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP"],
        "blurb": "Designs and ships AI-powered features, from model training to inference.",
    },
    "Cloud Engineer": {
        "skills": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Linux", "CI/CD"],
        "blurb": "Designs and manages the cloud infrastructure applications run on.",
    },
    "Full Stack Developer": {
        "skills": ["HTML", "CSS", "JavaScript", "React", "Node.js", "SQL", "Git"],
        "blurb": "Builds both the interface users see and the systems behind it.",
    },
}
