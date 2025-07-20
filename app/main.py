from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from uuid import UUID
import uuid
import requests
from pathlib import Path
from app.services.processor import PROCESSED_DATA, process_csv
import time


app = FastAPI(
    title="Order Metrics API",
    version="1.0.0",
    description="API to process CSV files and return order item metrics.",
)

@app.get("/")
def root():
    return {"message": "Welcome to the Order Metrics API"}

class UploadRequest(BaseModel):
    url: HttpUrl

import time

@app.post("/api/v1/order-items/upload")
def upload_order_items(data: UploadRequest):
    file_id = uuid.uuid4()
    file_path = Path("data") / f"{file_id}.csv"

    try:
        download_start = time.time()
        response = requests.get(data.url)
        response.raise_for_status()
        file_path.write_bytes(response.content)
        download_duration = time.time() - download_start
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save download time
    PROCESSED_DATA[str(file_id)] = {
        "download_seconds": int(download_duration),
        "formatted_download": time.strftime("%H:%M:%S", time.gmtime(download_duration))
    }

    return {
        "file_id": str(file_id),
        "status": "uploaded",
        "message": f"File uploaded successfully. Use /api/v1/order-items/uploads/{file_id}/processing-stats to get stats."
    }


@app.get("/api/v1/order-items/uploads/{file_id}/processing-stats")
def get_processing_stats(file_id: UUID):
    file_id_str = str(file_id)
    
    # Always run processing regardless of existing download stats
    try:
        return process_csv(file_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found or cannot be processed: {e}")

    
    return PROCESSED_DATA[file_id_str]
