import asyncio

import asyncpg
from pydantic_core import MultiHostUrl


class DBService:
    def __init__(
        self,
        dsn: MultiHostUrl
    ):
        self.dsn: MultiHostUrl = dsn

    async def check_db_status(self, timeout=5):
        try:
            dsn_str = str(self.dsn).replace('+asyncpg', '')
            conn = await asyncpg.connect(dsn=dsn_str, timeout=timeout)
            await conn.close()
            return True
        except asyncio.exceptions.TimeoutError:
            return False
