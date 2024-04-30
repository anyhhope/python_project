from fastapi import APIRouter, Depends, Request, status
from . import controller, schema
from asyncpg.pool import PoolConnectionProxy
from asyncpg import Connection
from data import get_connection
import datetime

# апи принимает данные используя методы контроллера
router = APIRouter(prefix="/api/query", tags=["query"])

@router.get("/health")
async def health():
    return {"message": "Api-service is running"}

@router.post("/")
async def process(query: schema.Query,
    db_conn: PoolConnectionProxy = Depends(get_connection)):

    try:
        await controller.process(db_conn, query)
        return status.HTTP_201_CREATED
    except ValueError as e:
        return {"detail": str(e)}