"""Authenticated dataset upload and processing-status endpoints."""
import re
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Request, UploadFile

from app.config.database import MongoDB
from app.config.settings import settings
from app.services.dataset_service import DatasetService

router = APIRouter(prefix="/api/logs", tags=["datasets"])


def _safe_name(filename: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", Path(filename or "upload.csv").name)


@router.post("/upload", status_code=202)
async def upload_file(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    user_id = getattr(request.state, "user", {}).get("userId", "anonymous")
    safe_name, content = _safe_name(file.filename), await file.read()
    DatasetService.validate_upload(safe_name, file.content_type, len(content))

    upload_dir = Path(settings.UPLOAD_DIR).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    dataset_id, file_path = str(uuid.uuid4()), None
    file_path = upload_dir / f"{dataset_id}_{safe_name}"
    file_path.write_bytes(content)

    try:
        DatasetService.validate_csv_header(str(file_path))
    except Exception:
        file_path.unlink(missing_ok=True)
        raise

    if MongoDB.get_db() is not None:
        await MongoDB.get_db().datasets.insert_one({
            "dataset_id": dataset_id, "user_id": user_id, "file_name": safe_name,
            "original_name": file.filename, "file_size": len(content), "dataset_type": "CICIDS2017",
            "status": "UPLOADED", "progress": 5, "uploaded_at": datetime.utcnow(),
            "total_records": 0, "processed_records": 0, "normal_records": 0, "attack_records": 0,
        })
    else:
        DatasetService.set_dataset_state(dataset_id, user_id, "UPLOADED", 5, file_name=safe_name, original_name=file.filename,
                                        file_size=len(content), dataset_type="CICIDS2017", uploaded_at=datetime.utcnow().isoformat(),
                                        total_records=0, processed_records=0, normal_records=0, attack_records=0)

    background_tasks.add_task(DatasetService.process_dataset, dataset_id, user_id, str(file_path))
    return {"success": True, "message": "Dataset uploaded successfully. Processing started.", "datasetId": dataset_id, "dataset_id": dataset_id}


@router.get("/{dataset_id}/status")
async def get_upload_status(dataset_id: str, request: Request):
    user_id = getattr(request.state, "user", {}).get("userId", "anonymous")
    db = MongoDB.get_db()
    if db is not None:
        dataset = await db.datasets.find_one({"dataset_id": dataset_id, "user_id": user_id}, {"_id": 0})
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found.")
        return {"success": True, **dataset}

    dataset = DatasetService.get_dataset_state(dataset_id)
    if not dataset or dataset.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return {"success": True, **dataset}


@router.get("/")
async def list_datasets(request: Request):
    user_id = getattr(request.state, "user", {}).get("userId", "anonymous")
    db = MongoDB.get_db()
    if db is not None:
        datasets = await db.datasets.find({"user_id": user_id}, {"_id": 0}).sort("uploaded_at", -1).to_list(100)
        return {"success": True, "datasets": datasets}
    return {"success": True, "datasets": DatasetService.list_datasets_for_user(user_id)}
