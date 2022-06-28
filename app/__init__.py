from fastapi import FastAPI, status, Request
from app.main.config import Config
from app.main.nlp.analyzeSentiments.resource import analyzeSentement_resource

fast_app = FastAPI(
    title="icets-explorers",
    description= "FastAPI Setup",
    version=Config.get_application_version()
)

fast_app.include_router(
    analyzeSentement_resource.nlp_router,prefix="/api"
)