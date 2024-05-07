from fastapi import APIRouter, Depends, HTTPException, status
from . import controller, schema
from asyncpg.pool import PoolConnectionProxy
from asyncpg import Connection
from data import get_connection
import datetime


# апи принимает данные используя методы контроллера
router = APIRouter(prefix="/api/stream", tags=["stream"])

@router.get("/health")
async def health():
    return {"message": "Api-service is running"}

@router.post("/init")
async def process(query: schema.QueryInit,
    db_conn: PoolConnectionProxy = Depends(get_connection)):
    try:
        new_id: int = await controller.process(db_conn, query)
        return {"id": str(new_id)}
    except ValueError as e:
        return {"detail": str(e)}

@router.post("/shutdown")
async def shutdown(query: schema.QueryShut,
    db_conn: PoolConnectionProxy = Depends(get_connection)):
    try:
        await controller.process_shutdown(db_conn, query)
        return {"id": query.id}
    except ValueError as e:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))