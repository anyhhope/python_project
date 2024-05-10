from asyncpg.pool import PoolConnectionProxy
from .schema import  Message, QueryShut, QueryInit, StateEnum, MessageState, ServiceSenderEnum
from .models import QueryDto
from . import db
import asyncio
from .producer import AIOProducer, get_query_producer, get_state_producer

# бизнес-логика, принимает данные пишет в бд и кафку



async def produce(producer: AIOProducer, message_to_produce: Message):
    try:
        await producer.send(value=message_to_produce)
        print(f"Message {message_to_produce} produced")
    except Exception as e:
        print(f"An error occurred: {e}")


async def process(db_conn: PoolConnectionProxy, query: QueryInit):
    query_row = QueryDto(
        rtsp_src = query.rtsp_src,
        state = StateEnum.STARTUP_PROCESS.value,
    )
    new_id: int = await db.insert_new_row(db_conn, query_row)
    print(new_id)
    producer: AIOProducer = get_query_producer()
    message_to_produce: Message = {"id" : new_id, "rtsp_src" : query.rtsp_src}
    await produce(producer, message_to_produce)
    return new_id

async def process_shutdown(db_conn: PoolConnectionProxy, query: QueryShut):
    row_exists = await db.check_row_exists(db_conn, int(query.id))
    if not row_exists:
        raise ValueError(f"Row with id {query.id} does not exist")
    
    await db.update_row(db_conn, int(query.id), StateEnum.SHUTDOWN_PROCESS.value)
    producer: AIOProducer = get_state_producer()
    message_to_produce: MessageState = {"id" : query.id, "state" : StateEnum.SHUTDOWN.value, "error": False, "sender": ServiceSenderEnum.API.value}
    await produce(producer, message_to_produce)
    return 
