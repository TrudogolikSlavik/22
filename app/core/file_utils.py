import secrets
from pathlib import Path
from typing import Dict

import aiofiles
from fastapi import HTTPException, UploadFile

# Create directories for file storage
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    "txt", "pdf", "doc", "docx", "md",
    "jpg", "jpeg", "png", "gif"
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


async def save_upload_file(file: UploadFile, user_id: int) -> Dict:
    """Save uploaded file and return metadata"""

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size is {MAX_FILE_SIZE // 1024 // 1024}MB"
        )

    # Check file extension
    file_extension = ""
    if "." in file.filename:
        file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Create user directory
    user_dir = UPLOAD_DIR / str(user_id)
    user_dir.mkdir(exist_ok=True)

    # Generate unique filename
    file_name = f"{secrets.token_hex(8)}_{file.filename}"
    file_path = user_dir / file_name

    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    return {
        "file_name": file.filename,
        "file_path": str(file_path),
        "file_size": file_size,
        "file_type": file_extension
    }


def delete_file(file_path: str) -> bool:
    """Delete file by path"""
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    except Exception:
        return False
