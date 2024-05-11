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
    """Добавление строки в две таблицы за одну транзакцию"""
    try:
        async with db.transaction():

            query = 'INSERT INTO stream_status(rtsp_src, state, created_at) VALUES($1, $2, $3) RETURNING id'
            result_id = await db.fetchval(query, new_row.rtsp_src, new_row.state, datetime.datetime.now())

            query = 'INSERT INTO outbox(query_id, rtsp_src) VALUES($1, $2)'
            await db.execute(query, result_id, new_row.rtsp_src)
            return result_id

    except Exception as e:
        raise e
    
async def get_unprocessed_rows_from_outbox(db: PoolConnectionProxy):
    query = 'SELECT * FROM outbox WHERE processed = FALSE'
    rows = await db.fetch(query)
    return rows

async def update_processed_rows_in_outbox(db: PoolConnectionProxy, id):
    query = 'UPDATE outbox SET processed = TRUE WHERE id = $1'
    await db.fetchval(query, id)
    return

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


