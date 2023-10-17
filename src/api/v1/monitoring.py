import logging

from fastapi import APIRouter, HTTPException, status, Depends

from core.config import app_settings
from schemas.dbs import DBStatusSchema
from services.db import DBService
from .dependencies import db_service

router = APIRouter(
    prefix='/monitorng',
    tags=['Monitoring'],
)

logger = logging.getLogger(__name__)


@router.get(
    '/db_health_check',
    response_model=DBStatusSchema,
    description='Get information about database availability',
    response_description='Availability of Database',
)
async def check_db_status(
    db_service: DBService = Depends(
        lambda: db_service(app_settings.database_dsn)
    ),
):
    is_alive = await db_service.check_db_status()
    if not is_alive:
        logger.error('Database is unavailable.')
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Database is unavailable'
        )
    logger.info('Database is abailable.')
    return {'detail': 'Database is abailable'}
