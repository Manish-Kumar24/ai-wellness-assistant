from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.cv_service import save_uploaded_file, extract_text_from_file
import os

router = APIRouter()

@router.post("/upload_report")
async def upload_report(file: UploadFile = File(...)):
    """Save file permanently and return its path."""
    try:
        contents = await file.read()
        file_path = save_uploaded_file(contents, file.filename)
        return {
            "message": "File uploaded successfully",
            "file_path": file_path,
            "filename": os.path.basename(file_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

