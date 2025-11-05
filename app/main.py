from fastapi import FastAPI
from app.api.routes import analyze

app = FastAPI(
    title="OSINT Microservice",
    version="1.1.0"
)

app.include_router(analyze.router)

@app.get("/health")
def health():
    return {"status": "ok"}
