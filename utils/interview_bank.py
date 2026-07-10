import random

QUESTION_BANK = {
    "hr": {
        "easy": [
            {"question": "Tell me about yourself.", "keywords": []},
            {"question": "What are your greatest strengths?", "keywords": []},
            {"question": "What do you consider your biggest weakness?", "keywords": []},
            {"question": "Why do you want to work at this company?", "keywords": []},
            {"question": "Where do you see yourself in five years?", "keywords": []},
        ],
        "medium": [
            {"question": "Tell me about a time you faced a conflict with a teammate and how you resolved it.", "keywords": []},
            {"question": "Describe a situation where you failed. What did you learn from it?", "keywords": []},
            {"question": "How do you handle tight deadlines and pressure?", "keywords": []},
            {"question": "Tell me about a time you took initiative on a project.", "keywords": []},
            {"question": "How do you prioritize tasks when everything feels urgent?", "keywords": []},
        ],
        "hard": [
            {"question": "Tell me about a time you disagreed with your manager's decision. What did you do?", "keywords": []},
            {"question": "Describe the most difficult stakeholder you've worked with and how you managed the relationship.", "keywords": []},
            {"question": "Tell me about a time you had to deliver bad news to a team or client.", "keywords": []},
            {"question": "How would you handle being asked to do something you believe is unethical?", "keywords": []},
            {"question": "Describe a time you had to influence someone without direct authority over them.", "keywords": []},
        ],
    },
    "technical": {
        "easy": [
            {"question": "What is the difference between a list and a tuple in Python?", "keywords": ["mutable", "immutable", "list", "tuple"]},
            {"question": "Explain what an API is and why it's useful.", "keywords": ["api", "interface", "request", "response"]},
            {"question": "What is the difference between SQL and NoSQL databases?", "keywords": ["sql", "nosql", "schema", "relational"]},
            {"question": "What does Git do, and why is version control important?", "keywords": ["git", "version control", "commit", "branch"]},
            {"question": "What is the time complexity of binary search, and why?", "keywords": ["binary search", "log", "sorted"]},
        ],
        "medium": [
            {"question": "Explain how REST APIs typically handle authentication.", "keywords": ["token", "jwt", "oauth", "authentication", "header"]},
            {"question": "What is the difference between a process and a thread?", "keywords": ["process", "thread", "memory", "concurrency"]},
            {"question": "How would you design a database schema for a simple blog application?", "keywords": ["table", "foreign key", "schema", "relationship", "primary key"]},
            {"question": "Explain Big-O notation and why it matters when writing code.", "keywords": ["big-o", "complexity", "time", "space"]},
            {"question": "What is the difference between synchronous and asynchronous programming?", "keywords": ["async", "synchronous", "callback", "event loop"]},
        ],
        "hard": [
            {"question": "How would you design a URL-shortening service like bit.ly?", "keywords": ["hash", "database", "scalability", "cache", "load balancer"]},
            {"question": "Explain how a load balancer decides where to send incoming traffic.", "keywords": ["round robin", "load balancer", "health check", "traffic"]},
            {"question": "How would you debug a production API that's suddenly returning intermittent 500 errors?", "keywords": ["logs", "monitoring", "debug", "error", "trace"]},
            {"question": "Explain the CAP theorem and what it means for distributed systems.", "keywords": ["consistency", "availability", "partition", "cap theorem"]},
            {"question": "How would you scale a database that's struggling under heavy read traffic?", "keywords": ["read replica", "caching", "index", "sharding"]},
        ],
    },
}

SESSION_LENGTH = 5


def get_questions(mode, difficulty):
    """Returns a shuffled list of question dicts (question, keywords, type)
    for the chosen mode/difficulty, always SESSION_LENGTH long."""
    if mode == "mixed":
        hr_qs = [{**q, "type": "hr"} for q in QUESTION_BANK["hr"][difficulty]]
        tech_qs = [{**q, "type": "technical"} for q in QUESTION_BANK["technical"][difficulty]]
        random.shuffle(hr_qs)
        random.shuffle(tech_qs)
        combined = []
        for i in range(SESSION_LENGTH):
            combined.append(hr_qs[i] if i % 2 == 0 else tech_qs[i])
        return combined[:SESSION_LENGTH]

    bank = [{**q, "type": mode} for q in QUESTION_BANK[mode][difficulty]]
    random.shuffle(bank)
    return bank[:SESSION_LENGTH]
