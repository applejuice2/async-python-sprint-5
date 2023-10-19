import io

import pytest
from starlette.datastructures import UploadFile
from httpx import AsyncClient


def create_mock_file(
    filename: str = "test_file.txt",
    content: str = "Test content"
):
    return UploadFile(
        filename=filename,
        # NOTE Cоздаем  временный файл в памяти
        # без необходимости сохранять его на диск
        file=io.BytesIO(content.encode()),
    )


@pytest.mark.asyncio
async def test_upload_file(
    ac: AsyncClient,
    clean_before_filesystem,
    clean_before_database_for_file,
    token
):
    # Создаем моковый файл
    mock_file = create_mock_file()

    # Формируем данные для запроса
    files = {
        "file": (mock_file.filename, mock_file.file, mock_file.content_type)
    }
    data = {"path_data": '{"path": "/testfile"}'}
    headers = {"Authorization": f"Bearer {token}"}

    response = await ac.post(
        "/api/v1/files/upload",
        headers=headers,
        data=data,
        files=files
    )

    # Закрываем моковый файл
    mock_file.file.close()

    assert response.status_code == 201
    assert response.json()["path"] == "/testfile"
    assert response.json()["name"] == "testfile"
    assert response.json()["is_downloadable"] is True


@pytest.mark.asyncio
async def test_download_file_by_path(
    ac: AsyncClient,
    token
):
    test_file_path = "/testfile"

    response = await ac.get(
        f"/api/v1/files/download?path={test_file_path}",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(response)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_of_licenses(
    ac: AsyncClient,
    token,
    # clean_after_database_for_file,
    # clean_after_filesystem
):

    response = await ac.get(
        "/api/v1/files/list",
    )

    assert response.status_code == 200
    assert response.json["files"][0]["path"] == "/testfile"
    assert response.json["files"][0]["name"] == "testfile"
    assert response.json()["is_downloadable"] is True
