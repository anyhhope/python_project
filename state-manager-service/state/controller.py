from .schema import MessageState, StateEnum, ServiceSenderEnum
from .db import update_row
from asyncpg.pool import PoolConnectionProxy
from data import get_connection
from types import SimpleNamespace


inactive_services = {}
error = False

async def process(msg : MessageState):
    global error
    global inactive_services

    msg_obg: MessageState = SimpleNamespace(**msg)
    db_conn: PoolConnectionProxy = await get_connection()
    message_id = msg_obg.id

    print(msg_obg)

    if message_id not in inactive_services:
        inactive_services[message_id] = {"ml": False, "runner": False, "error": False}

    if msg_obg.error:
        inactive_services[message_id]["error"] = True

    if msg_obg.state == StateEnum.SHUTDOWN:
        await update_row(db_conn, row_id=int(msg_obg.id), new_state=StateEnum.SHUTDOWN_PROCESS.value)
        service = msg_obg.sender
        if service != ServiceSenderEnum.API.value:
            inactive_services[message_id][service] = True
        print(inactive_services)
        print(f"Updated state {StateEnum.SHUTDOWN_PROCESS.value} in {msg_obg.id} row")

    if msg_obg.state == StateEnum.ML_PROCESS or msg_obg.state == StateEnum.RUNNER_PROCESS:
        await update_row(db_conn, row_id=int(msg_obg.id), new_state=msg_obg.state)
        print(f"Updated state {msg_obg.state} in {msg_obg.id} row")

    if msg_obg.state == StateEnum.INACTIVE_OK:
        service = msg_obg.sender
        
        inactive_services[message_id][service] = True

        print(inactive_services)
        
        if all(value for key, value in inactive_services[message_id].items() if key != "error"):
            new_state = StateEnum.INACTIVE_ERROR if inactive_services[message_id]["error"] else StateEnum.INACTIVE_OK
            await update_row(db_conn, row_id=int(msg_obg.id), new_state=new_state.value)
            print(f"Updated state {new_state.value} in {msg_obg.id} row")
    
            inactive_services.pop(message_id)
    return