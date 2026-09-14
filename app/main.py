from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_fastapi import FastAPIRedis

from app.api.medical import router as medical_router
from app.core.config import settings
from app.core.logging import setup_observability
from app.lifespans.lifespan_services import lifespan

app = FastAPI(docs_url=None, openapi_url=None , redoc_url=None, lifespan=lifespan, title="Medical Analyzer API")
FastAPIRedis(app).lifespan().rate_limiting().otel()
#"http://localhost:5173"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(settings.allow_origins)],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Setup Logfire tracing
setup_observability(app)

app.include_router(medical_router)


@app.get("/")
def health_check():
    return {"message": "Welcome to Medical Analyzer AI"}
