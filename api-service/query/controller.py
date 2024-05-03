from asyncpg.pool import PoolConnectionProxy
from .schema import Query, Message
from .models import QueryDto
from .db import insert_new_row
import asyncio
from .producer import AIOWebProducer, get_query_producer

# бизнес-логика, принимает данные пишет в бд и кафку
async def process(db_conn: PoolConnectionProxy, query: Query):
    query_row = QueryDto(
        rtsp_src = query.rtsp_src,
        state = query.state,
    )
    new_id: int = await insert_new_row(db_conn, query_row)
    print(new_id)
    message_to_produce: Message = {"id" : new_id, "rtsp_src" : query.rtsp_src}
    await produce(message_to_produce)
    return new_id

async def produce(message_to_produce: Message):
    try:
        producer: AIOWebProducer = get_query_producer()
        await producer.send(value=message_to_produce)
        print(f"Message {message_to_produce} produced")
    except Exception as e:
        print(f"An error occurred: {e}")