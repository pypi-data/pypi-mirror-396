from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

from promethium.core.database import get_db, Job, Dataset
from promethium.core.schemas import JobRead, JobCreate, JobStatus
from promethium.workflows.tasks import run_reconstruction_job
from promethium.core.logging import logger

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/", response_model=JobRead, status_code=201)
async def create_job(
    job_in: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a new processing job.
    """
    # Verify dataset exists
    dataset = await db.get(Dataset, job_in.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    job_id = str(uuid4())
    new_job = Job(
        id=job_id,
        dataset_id=job_in.dataset_id,
        algorithm=job_in.algorithm,
        status=JobStatus.QUEUED.value,
        params=job_in.params,
        created_at=datetime.utcnow()
    )
    
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    # Trigger Celery task
    task = run_reconstruction_job.delay(
        job_id=job_id,
        dataset_id=job_in.dataset_id,
        algorithm=job_in.algorithm,
        params=job_in.params
    )
    logger.info(f"Job submitted to queue: {job_id} (Task ID: {task.id})")
    
    return new_job

@router.get("/{job_id}", response_model=JobRead)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/", response_model=List[JobRead])
async def list_jobs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).offset(skip).limit(limit))
    jobs = result.scalars().all()
    return jobs
