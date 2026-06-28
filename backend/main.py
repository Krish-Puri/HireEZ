from fastapi import FastAPI

from fastapi import FastAPI

from backend.api.candidate_routes import router as candidate_router
from backend.api.job_routes import router as job_router

app = FastAPI(
    title="HireEZ API",
    version="1.0.0",
)

app.include_router(candidate_router)
app.include_router(job_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "message": "Welcome to HireEZ 🚀"
    }

from backend.core.exceptions import HireEZException

from backend.core.handlers import hireez_exception_handler

app.add_exception_handler(
    HireEZException,
    hireez_exception_handler
)