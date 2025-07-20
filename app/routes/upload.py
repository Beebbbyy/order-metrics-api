from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl
import uuid
from app.services.file_handler import download_csv_file

router = APIRouter()

class UploadRequest(BaseModel):
    url: HttpUrl

class UploadResponse(BaseModel):
    file_id: str
    message: str

@router.post("/upload", response_model=UploadResponse)
def upload_file(request: UploadRequest):
    try:
        file_id = str(uuid.uuid4())
        download_csv_file(request.url, file_id)
        return UploadResponse(file_id=file_id, message="File successfully uploaded and saved.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
