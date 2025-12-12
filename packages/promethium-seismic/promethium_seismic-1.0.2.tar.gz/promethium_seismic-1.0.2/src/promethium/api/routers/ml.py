from fastapi import APIRouter, HTTPException, BackgroundTasks
from uuid import uuid4
from datetime import datetime

from promethium.api.schemas import TrainingRequest, InferenceRequest, JobResponse, JobStatus
from promethium.workflows.tasks import train_model_task, run_inference_task

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

@router.post("/train", response_model=JobResponse)
async def submit_training_job(request: TrainingRequest):
    """
    Submit a new model training job.
    """
    # 1. Validation (Check if dataset exists)
    # verify_dataset(request.dataset_id)
    
    # 2. Submit to Celery
    task = train_model_task.delay(request.model_dump())
    
    return JobResponse(
        job_id=task.id,
        status=JobStatus.QUEUED,
        created_at=datetime.utcnow()
    )

@router.post("/predict", response_model=JobResponse)
async def submit_inference_job(request: InferenceRequest):
    """
    Submit a batch inference job.
    """
    task = run_inference_task.delay(request.model_dump())
    
    return JobResponse(
        job_id=task.id,
        status=JobStatus.QUEUED,
        created_at=datetime.utcnow()
    )

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Check status of a background job.
    """
    # Check ResultBackend
    from celery.result import AsyncResult
    from promethium.workflows.tasks import celery_app
    
    res = AsyncResult(job_id, app=celery_app)
    
    return {
        "job_id": job_id,
        "status": res.state,
        "result": res.result if res.ready() else None
    }
