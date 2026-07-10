import os
import uuid
from werkzeug.utils import secure_filename


def allowed_file(filename, allowed_extensions):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed_extensions
    )


def save_upload(file_storage, upload_folder, user_id):
    """
    Saves the uploaded file under a per-user folder with a unique name,
    so two people uploading "resume.pdf" never collide or overwrite
    each other. Returns (saved_filename, full_path).
    """
    original_name = secure_filename(file_storage.filename)
    ext = original_name.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex[:10]}.{ext}"

    user_folder = os.path.join(upload_folder, str(user_id))
    os.makedirs(user_folder, exist_ok=True)

    full_path = os.path.join(user_folder, unique_name)
    file_storage.save(full_path)

    return original_name, full_path
