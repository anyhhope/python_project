from . import models
from asyncpg.pool import PoolConnectionProxy
import datetime

# взаимодействие с бд
async def insert_new_row(db: PoolConnectionProxy, new_row: models.QueryDto ):
    """Добавление новой строки"""
    query = 'INSERT INTO stream_status(rtsp_src, state, created_at) VALUES($1, $2, $3) RETURNING id'
    result = await db.fetchval(query, new_row.rtsp_src, new_row.state, datetime.datetime.now())
    return result


async def update_row(db: PoolConnectionProxy, row_id: int, new_state: str):
    """Обновление состояния текущей строки по идентификатору"""
    query = 'UPDATE stream_status SET state = $1 WHERE id = $2'
    await db.execute(query, new_state, row_id)


async def check_row_exists(db: PoolConnectionProxy, row_id: int) -> bool:
    """Проверка существования строки с заданным идентификатором"""
    query = 'SELECT COUNT(*) FROM stream_status WHERE id = $1'
    result = await db.fetchval(query, row_id)
    return result > 0