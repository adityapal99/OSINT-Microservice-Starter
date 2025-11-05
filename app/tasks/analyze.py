from app.core.celery_app import celery_app
from app.services.logic import process_identifier
from app.core.logging import get_logger

log = get_logger(__name__)

@celery_app.task(name="app.tasks.analyze.run_analysis")
def run_analysis(payload: dict):
    log.info(f"Processing payload: {payload}")
    result = process_identifier(payload["identifier"])
    return {"status": "complete", "data": result}
