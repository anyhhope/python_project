from . import models
from asyncpg.pool import PoolConnectionProxy
import datetime

# взаимодействие с бд
async def insert_new_row(db: PoolConnectionProxy, new_row: models.QueryDto ):
    """Добавление новой строки"""
    query = 'INSERT INTO stream_status(rtsp_src, state, created_at) VALUES($1, $2, $3)'
    await db.execute(query, new_row.rtsp_src, new_row.state, datetime.datetime.now())