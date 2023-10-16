import logging

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core.config import app_settings
from api.v1.routers import routers

logger = logging.getLogger(__name__)

app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

for router in routers:
    app.include_router(router, prefix='/api/v1')
