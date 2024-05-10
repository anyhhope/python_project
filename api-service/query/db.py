from . import models
from asyncpg.pool import PoolConnectionProxy
import datetime

# взаимодействие с бд
async def insert_new_row(db: PoolConnectionProxy, new_row: models.QueryDto ):
    """Добавление новой строки"""
    query = 'INSERT INTO stream_status(rtsp_src, state, created_at) VALUES($1, $2, $3) RETURNING id'
    result = await db.fetchval(query, new_row.rtsp_src, new_row.state, datetime.datetime.now())
    return result

async def insert_rows_transaction(db: PoolConnectionProxy, new_row: models.QueryDto):
    try:
        async with db.transaction():
            # Insert rows into the first table
            query = 'INSERT INTO stream_status(rtsp_src, state, created_at) VALUES($1, $2, $3) RETURNING id'
            result_id = await db.fetchval(query, new_row.rtsp_src, new_row.state, datetime.datetime.now())
            # Insert rows into the second table
            query = 'INSERT INTO outbox(rtsp_src) VALUES($1)'
            await db.execute(query, new_row.rtsp_src)

    except Exception as e:
        # Rollback the transaction in case of any exception
        await db.rollback()
        raise e
    
async def get_row_from_outbox(db: PoolConnectionProxy):
    query = 'SELECT id, rtsp_src FROM outbox ORDER BY id LIMIT 1'
    row = await db.fetchval(query)
    return row

async def delete_row_from_outbox(db: PoolConnectionProxy, id):
    query = 'DELETE FROM outbox WHERE id = $1'
    row = await db.fetchval(query, id)
    return row

async def update_row(db: PoolConnectionProxy, row_id: int, new_state: str):
    """Обновление состояния текущей строки по идентификатору"""
    query = 'UPDATE stream_status SET state = $1 WHERE id = $2'
    await db.execute(query, new_state, row_id)


async def check_row_exists(db: PoolConnectionProxy, row_id: int) -> bool:
    """Проверка существования строки с заданным идентификатором"""
    query = 'SELECT COUNT(*) FROM stream_status WHERE id = $1'
    result = await db.fetchval(query, row_id)
    return result > 0

async def get_detection_results_by_query_id(db: PoolConnectionProxy, query_id: int):
    """Retrieve all rows from detection_result table with the specified query_id"""
    query = 'SELECT * FROM detection_result WHERE query_id = $1'
    results = await db.fetch(query, query_id)
    return results


