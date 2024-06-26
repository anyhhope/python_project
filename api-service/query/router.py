from fastapi import APIRouter, Depends, HTTPException, status
from . import controller, schema
from asyncpg.pool import PoolConnectionProxy
from asyncpg import Connection
from data import get_connection
import datetime


# апи принимает данные и для обработки использует методы контроллера
router = APIRouter(prefix="/api/stream", tags=["stream"])

@router.post("/init")
async def process(query: schema.QueryInit,
    db_conn: PoolConnectionProxy = Depends(get_connection)):
    try:
        new_id: int = await controller.process(db_conn, query)
        return {"id": str(new_id)}
    except ValueError as e:
        return {"detail": str(e)}

@router.post("/shutdown")
async def shutdown(query: schema.QueryOnlyId,
    db_conn: PoolConnectionProxy = Depends(get_connection)):
    try:
        await controller.process_shutdown(db_conn, query)
        return {"id": query.id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    

@router.get("/detection_result/{query_id}")
async def detection(query_id, db_conn: PoolConnectionProxy = Depends(get_connection)):
    try:
        result = await controller.get_detection_result(db_conn, query_id)
        return {"detected": result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/state/{query_id}")
async def get_state(query_id, db_conn: PoolConnectionProxy = Depends(get_connection)):
    try:
        result = await controller.get_state(db_conn, query_id)
        return {"state": result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))