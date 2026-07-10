import re

EMAIL_RE = re.compile(r"[\w\.\-+]+@[\w\-]+\.[\w\.\-]+")
PHONE_RE = re.compile(r"[\+\(]?\d[\d\s\-.\(\)]{7,14}\d")

# section headers we recognise, mapped to a normalized section name
SECTION_MAP = {
    "education": "education",
    "academic background": "education",
    "academic details": "education",
    "qualification": "education",

    "experience": "experience",
    "work experience": "experience",
    "professional experience": "experience",
    "internship": "experience",
    "internships": "experience",
    "employment history": "experience",

    "projects": "projects",
    "academic projects": "projects",
    "personal projects": "projects",

    "skills": "skills",
    "technical skills": "skills",
    "core competencies": "skills",
    "key skills": "skills",

    "certifications": "certifications",
    "certificates": "certifications",
    "licenses & certifications": "certifications",

    "summary": "summary",
    "objective": "summary",
    "profile": "summary",
    "career objective": "summary",
}

# common tech / employability skills we scan the resume for
SKILL_KEYWORDS = [
    "Python", "Java", "C++", "C", "JavaScript", "TypeScript", "HTML", "CSS",
    "React", "Angular", "Vue", "Node.js", "Express", "Flask", "Django",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis",
    "Git", "GitHub", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux",
    "REST API", "GraphQL", "Machine Learning", "Deep Learning", "TensorFlow",
    "PyTorch", "Pandas", "NumPy", "Scikit-learn", "Data Structures", "Algorithms",
    "OOP", "Agile", "Scrum", "CI/CD", "Jenkins", "Figma", "Excel", "Power BI",
    "Tableau", "R", "Kotlin", "Swift", "Flutter", "React Native", "Spring Boot",
    ".NET", "PHP", "Laravel", "Kafka", "Firebase", "Bootstrap", "Tailwind CSS",
    "jQuery", "Selenium", "JUnit", "Pytest", "NLP", "Computer Vision",
    "Data Analysis", "System Design", "Microservices", "DSA", "Java Spring",
]


def _contains_skill(text_lower, skill_lower):
    """Substring match with word-boundary style checks either side, so
    'R' doesn't match inside 'Research' but 'C++' still matches fine."""
    idx = text_lower.find(skill_lower)
    while idx != -1:
        before = text_lower[idx - 1] if idx > 0 else " "
        after_idx = idx + len(skill_lower)
        after = text_lower[after_idx] if after_idx < len(text_lower) else " "
        if not before.isalnum() and not after.isalnum():
            return True
        idx = text_lower.find(skill_lower, idx + 1)
    return False


def extract_email(text):
    match = EMAIL_RE.search(text)
    return match.group(0) if match else None


def extract_phone(text):
    for match in PHONE_RE.finditer(text):
        digits = re.sub(r"\D", "", match.group(0))
        if 10 <= len(digits) <= 13:
            return match.group(0).strip()
    return None


def extract_name(text):
    """Best-effort guess: the first substantial line that isn't
    an email, phone number, or link."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or len(stripped) > 60:
            continue
        if EMAIL_RE.search(stripped) or "http" in stripped.lower():
            continue
        if re.search(r"\d{4,}", stripped):
            continue
        words = stripped.split()
        if 1 < len(words) <= 5:
            return stripped
    return None


def split_sections(text):
    """Splits resume text into named sections based on recognised headers."""
    lines = text.splitlines()
    sections = {"header": []}
    current = "header"

    for line in lines:
        stripped = line.strip()
        key = stripped.lower().strip(":").strip()
        if key in SECTION_MAP and len(stripped) < 40:
            current = SECTION_MAP[key]
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)

    return {name: "\n".join(content).strip() for name, content in sections.items()}


def extract_skills(text):
    text_lower = text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        if _contains_skill(text_lower, skill.lower()):
            found.append(skill)
    return found


def parse_resume(text):
    """Main entry point — takes raw extracted resume text, returns a dict
    of everything the dashboard and analysis features need."""
    sections = split_sections(text)

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "education": sections.get("education", ""),
        "experience": sections.get("experience", ""),
        "projects": sections.get("projects", ""),
        "certifications": sections.get("certifications", ""),
        "skills": extract_skills(text),
        "raw_text": text,
    }
