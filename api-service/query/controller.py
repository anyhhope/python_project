from asyncpg.pool import PoolConnectionProxy
from .schema import Query
from .models import QueryDto
from .db import insert_new_row

# бизнес-логика, принимает данные пишет в бд и кафку
async def process(db_conn: PoolConnectionProxy, query: Query):
    query_row = QueryDto(
        rtsp_src = query.rtsp_src,
        state = query.state,
    )
    return await insert_new_row(db_conn, query_row)
    

# import методы из db
# kafka client

#  предметные области