from . import models
from asyncpg.pool import PoolConnectionProxy
import datetime

# взаимодействие с бд
async def insert_new_row(db: PoolConnectionProxy, new_row: models.DetectionDto ):
    """Добавление новой строки"""
    query = 'INSERT INTO detection_result(s3_url, query_id, detection_result, created_at) VALUES($1, $2, $3, $4)'
    await db.fetchval(query, new_row.s3_url, new_row.query_id, new_row.detection_result, datetime.datetime.now())
    return