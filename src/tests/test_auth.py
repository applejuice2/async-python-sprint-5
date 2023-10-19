import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_sign_up(
    ac: AsyncClient, clean_before_database, clean_after_database
):
    response = await ac.post(
        '/api/v1/auth/sign_up',
        json={
            "username": "appleJUICE2",
            "email": "apple@juice.com",
            "password": "testPASSWORD99"
        }
    )

    assert response.status_code == 201
    assert response.json() == {"username": "appleJUICE2"}


@pytest.mark.asyncio
async def test_sign_in(
    ac: AsyncClient, clean_before_database, test_user, clean_after_database
):
    data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }

    response = await ac.post(
        "/api/v1/auth/sign_in",
        data=data,
    )

    assert response.status_code == 201
    assert response.json()["token_type"] == "bearer"
