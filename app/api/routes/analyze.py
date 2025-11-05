from fastapi import APIRouter, Depends, HTTPException
from celery.result import AsyncResult
from app.api.schemas.analyze import AnalyzePayload
from app.core.celery_app import celery_app
from app.core.config import settings

router = APIRouter()

async def verify_api_key(x_api_key: str):
    if x_api_key != settings.SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@router.post("/analyze", tags=["Analysis"])
async def start_analysis(payload: AnalyzePayload, x_api_key: str = Depends(verify_api_key)):
    task = celery_app.send_task("app.tasks.analyze.run_analysis", args=[payload.dict()])
    return {"task_id": task.id, "status": "ACCEPTED"}

@router.get("/results/{task_id}", tags=["Analysis"])
async def get_task_results(task_id: str, x_api_key: str = Depends(verify_api_key)):
    result = AsyncResult(task_id, app=celery_app)
    return {"task_id": task_id, "status": result.state, "result": result.result}
