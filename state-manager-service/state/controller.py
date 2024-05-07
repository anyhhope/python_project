from .schema import MessageState
from .db import update_row
from asyncpg.pool import PoolConnectionProxy
from data import get_connection
from types import SimpleNamespace

async def process(msg : MessageState):
    msg_obg: MessageState = SimpleNamespace(**msg)
    db_conn: PoolConnectionProxy = await get_connection()
    await update_row(db_conn, row_id=int(msg_obg.id), new_state=msg_obg.state)
    print(f"Updated state {msg_obg.state} in {msg_obg.id} row")
    return