import os
import uuid
from datetime import datetime
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

# Configure upload directory
UPLOAD_DIR = "backend/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Poppler path (Windows only)
POPPLER_PATH = r"C:\Program Files\poppler-25.07.0\Library\bin" if os.name == 'nt' else None

def save_uploaded_file(file, original_filename: str) -> str:
    """Save uploaded file with unique name and return full path."""
    ext = os.path.splitext(original_filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}_{int(datetime.now().timestamp())}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    
    with open(file_path, "wb") as f:
        f.write(file)
    return file_path

def extract_text_from_image(image_path: str) -> str:
    image = Image.open(image_path)
    return pytesseract.image_to_string(image).strip()

def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        images = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"PDF OCR failed: {str(e)}")

def extract_text_from_file(file_path: str) -> str:
    """Extract text from a saved file (PDF or image)."""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
        return extract_text_from_image(file_path)
    else:
        raise ValueError("Unsupported file type")