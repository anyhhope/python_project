from . import models
from asyncpg.pool import PoolConnectionProxy

async def update_row(db: PoolConnectionProxy, row_id: int, new_state: str):
    """Обновление состояния текущей строки по идентификатору"""
    query = 'UPDATE stream_status SET state = $1 WHERE id = $2'
    await db.execute(query, new_state, row_id)
