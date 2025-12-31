import os
import uuid

BASE_DIR = "backend/storage/encrypted_files"

os.makedirs(BASE_DIR, exist_ok=True)

def save_encrypted_file(data: bytes) -> str:
    """
    Saves encrypted file bytes to disk.
    Returns generated file path.
    """
    file_id = str(uuid.uuid4())
    file_path = os.path.join(BASE_DIR, file_id)

    with open(file_path, "wb") as f:
        f.write(data)

    return file_path


def load_encrypted_file(file_path: str) -> bytes:
    """
    Loads encrypted file bytes from disk.
    """
    with open(file_path, "rb") as f:
        return f.read()


def delete_encrypted_file(file_path: str) -> None:
    """Delete an encrypted file blob from disk.

    This is best-effort: if the file doesn't exist, it's treated as already deleted.
    """
    try:
        os.remove(file_path)
    except FileNotFoundError:
        return
