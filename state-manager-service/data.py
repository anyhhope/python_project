import logging
import asyncpg as pg
from typing import Any, AsyncGenerator, Generator
from asyncpg.pool import PoolConnectionProxy
from config import Config, cfg


class Database:

    def __init__(self, cfg: Config, retry: int = 3):
        self.dsn = cfg.build_postgres_dsn
        self.retry = retry

    async def connect(self):

        pool = await pg.create_pool(dsn=self.dsn)
        if pool is None:
            for _ in range(self.retry):
                pool = await pg.create_pool(dsn=self.dsn)
                if pool is not None:
                    break
        if pool is None:
            raise Exception(f"can't connect to db in {self.retry} retries")
        print("Database pool connectionn opened")
        self.pool = pool

    async def disconnect(self):
        await self.pool.close()

db_instance = Database(cfg)

async def get_connection() -> PoolConnectionProxy:
    print("Getting connection")
    connection = await db_instance.pool.acquire()
    print("Connection acquired")
    return connection