import logging
from pathlib import Path
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi import UploadFile, File
from fastapi.responses import FileResponse

from .dependencies import file_service, get_upload_schema, get_user_from_token
from schemas.file import FileDownloadSchema, UploadedFileSchema
from schemas.file import UploadFileSchema
from schemas.file import ListofUploadFilesSchema
from services.file import FileService
from models.entities import User


router = APIRouter(
    prefix='/files',
    tags=['Files'],
)

logger = logging.getLogger(__name__)


@router.post(
    '/upload',
    response_model=UploadedFileSchema,
    status_code=status.HTTP_201_CREATED,
    description='Upload a new File',
    response_description='Uploaded File information',
)
async def add_file(
    file: UploadFile = File(...),
    file_service: FileService = Depends(file_service),
    user: User = Depends(get_user_from_token),
    path_data: UploadFileSchema = Depends(get_upload_schema),
):
    file_info = await file_service.add_file(user, file, path_data)
    if not file_info:
        logger.warning(
            'Error when uploading new file.'
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='File was not uploaded.'
        )
    logger.info(f'New file {file_info} was created.')
    return file_info


@router.get(
    '/list',
    response_model=ListofUploadFilesSchema,
    description='Get information about all of your uploaded files',
    response_description='Information about user uploaded files',
)
async def get_uploaded_files(
    user: User = Depends(get_user_from_token),
    file_service: FileService = Depends(file_service),
):
    user_files = await file_service.get_user_files(user)
    return {'account_id': str(user.id), 'files': user_files}


@router.get(
    '/files/download',
    status_code=status.HTTP_200_OK,
    description='Download File',
    response_description='Downloaded File',
)
async def download_file(
    path: Optional[str] = None,
    id: Optional[UUID] = None,
    file_service: FileService = Depends(file_service),
    user: User = Depends(get_user_from_token),
):
    file_data = FileDownloadSchema(path=path, id=id)
    file_path = await file_service.get_file_path(file_data, user)
    if not file_path:
        raise HTTPException(status_code=404, detail='File not found.')

    return FileResponse(
        file_path,
        filename=Path(file_path).name,
        media_type='application/octet-stream'
    )
