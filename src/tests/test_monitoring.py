import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_monitoring(ac: AsyncClient):
    response = await ac.get(
        '/api/v1/monitoring/db_health_check',
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "Database is abailable"}
