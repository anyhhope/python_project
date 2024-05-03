from fastapi import APIRouter, Depends, Request, status
from . import controller, schema
from asyncpg.pool import PoolConnectionProxy
from asyncpg import Connection
from data import get_connection
import datetime
from .producer import AIOWebProducer, get_query_producer


# апи принимает данные используя методы контроллера
router = APIRouter(prefix="/api/stream", tags=["stream"])

@router.get("/health")
async def health():
    return {"message": "Api-service is running"}

@router.post("/")
async def process(query: schema.Query,
    db_conn: PoolConnectionProxy = Depends(get_connection)):

    try:
        new_id: int = await controller.process(db_conn, query)
        return {"id": str(new_id)}
    except ValueError as e:
        return {"detail": str(e)}