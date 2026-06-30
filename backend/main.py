from fastapi import FastAPI

from backend.api.candidate_routes import router as candidate_router
from backend.api.job_routes import router as job_router
from backend.api.test_routes import router as test_router
from backend.api.interview_routes import router as interview_router
from backend.api.admin_routes import router as admin_router
from backend.api.google_auth_routes import router as google_auth_router

app = FastAPI(
    title="HireEZ API",
    version="1.0.0",
)

app.include_router(candidate_router)
app.include_router(job_router)
app.include_router(test_router)
app.include_router(interview_router)
app.include_router(admin_router)
app.include_router(google_auth_router)

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


@app.on_event("startup")
def on_startup():
    from backend.database.init_db import init_database
    init_database()
