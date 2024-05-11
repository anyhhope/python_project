from .schema import MessageState, StateEnum
from .db import update_row
from asyncpg.pool import PoolConnectionProxy
from data import get_connection
from types import SimpleNamespace


inactive_services = {"ml": False, "runner": False}
error = False

async def process(msg : MessageState):
    global error
    global inactive_services

    msg_obg: MessageState = SimpleNamespace(**msg)
    db_conn: PoolConnectionProxy = await get_connection()

    if msg_obg.error:
        error = True

    if msg_obg.state == StateEnum.SHUTDOWN:
        await update_row(db_conn, row_id=int(msg_obg.id), new_state=StateEnum.SHUTDOWN_PROCESS.value)
        service = msg_obg.sender
        print(f"Updated state {StateEnum.SHUTDOWN_PROCESS.value} in {msg_obg.id} row")

    if msg_obg.state == StateEnum.ML_PROCESS or msg_obg.state == StateEnum.RUNNER_PROCESS:
        await update_row(db_conn, row_id=int(msg_obg.id), new_state=msg_obg.state)
        print(f"Updated state {msg_obg.state} in {msg_obg.id} row")

    if msg_obg.state == StateEnum.INACTIVE_OK:
        service = msg_obg.sender
        if inactive_services[service] == False:
            inactive_services[service] = True
        
        if all(value == True for value in inactive_services.values()):
            if error:
                await update_row(db_conn, row_id=int(msg_obg.id), new_state=StateEnum.INACTIVE_ERROR)
                print(f"Updated state {StateEnum.INACTIVE_ERROR.value} in {msg_obg.id} row")
            else: 
                await update_row(db_conn, row_id=int(msg_obg.id), new_state=StateEnum.INACTIVE_OK)  
                print(f"Updated state {StateEnum.INACTIVE_OK.value} in {msg_obg.id} row")

            for key in inactive_services.keys():
                inactive_services[key] = False
                error = False
    return