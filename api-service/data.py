import logging
import asyncpg as pg
from typing import Any, AsyncGenerator, Generator
from asyncpg.pool import PoolConnectionProxy
from config import Config, cfg
from fastapi import FastAPI


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

    async def create_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS stream_status (
                    id SERIAL PRIMARY KEY,
                    rtsp_src TEXT not null,
                    state TEXT not null,
                    created_at TIMESTAMP not null
                );
            ''')    
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS detection_result (
                    id SERIAL PRIMARY KEY,
                    s3_url TEXT not null,
                    query_id INTEGER not null,
                    detection_result text not null,
                    created_at TIMESTAMP not null
                );
            ''')  
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS outbox (
                                id SERIAL PRIMARY KEY,
                                rtsp_src: text not null,
                            );
            ''')  


db_instance = Database(cfg)

async def get_connection() -> AsyncGenerator[PoolConnectionProxy, None]:
    print("Getting connection")
    async with db_instance.pool.acquire() as connection:
        yield connection
    print("Releasing connection")
