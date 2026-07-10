import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

_default_db_uri = "sqlite:///" + os.path.join(basedir, "instance", "app.db")
_env_db_url = os.environ.get("DATABASE_URL", "").strip()


def _resolve_db_uri(env_value, default_value):
    """
    A relative sqlite path (sqlite:///instance/app.db) resolves against
    whatever directory the process happens to be launched from — not
    necessarily the project folder — which breaks the moment someone runs
    the app from a different working directory. Any sqlite:/// URL that
    isn't already absolute gets rewritten relative to this project's
    folder instead, so it works the same regardless of where `python
    run.py` was run from.
    """
    if not env_value:
        return default_value

    if env_value.startswith("sqlite:///") and not env_value.startswith("sqlite:////"):
        relative_path = env_value[len("sqlite:///"):]
        if not os.path.isabs(relative_path):
            return "sqlite:///" + os.path.join(basedir, relative_path)

    return env_value


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")

    SQLALCHEMY_DATABASE_URI = _resolve_db_uri(_env_db_url, _default_db_uri)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(basedir, "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max resume size
    ALLOWED_EXTENSIONS = {"pdf", "docx"}

    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    # llama-3.3-70b-versatile was deprecated by Groq in June 2026 —
    # gpt-oss-120b is their recommended replacement for this kind of task
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
