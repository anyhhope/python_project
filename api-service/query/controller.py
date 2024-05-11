from asyncpg.pool import PoolConnectionProxy
from .schema import  Message, QueryOnlyId, QueryInit, StateEnum, MessageState, ServiceSenderEnum
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

async def produce_from_outbox(db_conn: PoolConnectionProxy, producer: AIOProducer, message_to_produce: Message):
    try:
        async with db_conn.transaction():
            rows = await db.get_unprocessed_rows_from_outbox(db_conn)
            print(rows)

            for row in rows:
                await produce(producer, message_to_produce)
                await db.update_processed_rows_in_outbox(db_conn, row['id'])

    except Exception as e:
        print(f"Error occurred during message production or database update: {e}")


async def process(db_conn: PoolConnectionProxy, query: QueryInit):
    new_id: int = None 

    try:
        query_row = QueryDto(
            rtsp_src=query.rtsp_src,
            state=StateEnum.STARTUP_PROCESS.value,
        )
        new_id = await db.insert_rows_transaction(db_conn, query_row)
        return new_id

    except Exception as e:
        raise e

    finally:

        producer: AIOProducer = get_query_producer()
        message_to_produce: Message = {"id": str(new_id), "rtsp_src": query.rtsp_src}

        await produce_from_outbox(db_conn, producer, message_to_produce)

async def process_shutdown(db_conn: PoolConnectionProxy, query: QueryOnlyId):
    row_exists = await db.check_row_exists(db_conn, int(query.id))
    if not row_exists:
        raise ValueError(f"Row with id {query.id} does not exist")
    
    await db.update_row(db_conn, int(query.id), StateEnum.SHUTDOWN_PROCESS.value)
    producer: AIOProducer = get_state_producer()
    message_to_produce: MessageState = {"id" : query.id, "state" : StateEnum.SHUTDOWN.value, "error": False, "sender": ServiceSenderEnum.API.value}
    await produce(producer, message_to_produce)
    return 


async def get_detection_result(db_conn: PoolConnectionProxy, query_id):
    result = await db.get_detection_results_by_query_id(db_conn, int(query_id))
    return result
