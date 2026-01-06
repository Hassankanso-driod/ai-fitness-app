# utils.py - Utility functions for file handling
import os
import uuid
from pathlib import Path
from fastapi import UploadFile

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def save_uploaded_file(file: UploadFile, upload_dir: str = "uploads") -> str:
    """
    Save uploaded file to upload directory
    Returns the filename (uuid.jpg)
    """
    # Generate unique filename
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{file_ext}"
    upload_path = Path(upload_dir)
    upload_path.mkdir(exist_ok=True)
    filepath = upload_path / filename
    
    # Save file
    with open(filepath, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    return filename

def delete_uploaded_file(filename: str, upload_dir: str = "uploads") -> bool:
    """
    Delete file from upload directory
    Returns True if deleted, False if not found
    """
    if not filename:
        return False
    
    filepath = Path(upload_dir) / filename
    if filepath.exists():
        filepath.unlink()
        return True
    return False

