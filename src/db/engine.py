from datetime import datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy import insert, select, delete
from sqlalchemy.ext.asyncio import create_async_engine

from src.store.config import DBConfig
from .models import *

engine = create_async_engine(DBConfig.URL_DATABASE)


async def drop_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_premium(id: int):
    sql = select(Premium).where(Premium.id == id)
    async with engine.connect() as conn:
        res = await conn.execute(sql)
        return res.first()


async def insert_premium(id: int, type: PremiumType) -> None:
    sql = insert(Premium).values({
        "id": id,
        "expire": datetime.now() + relativedelta(months=1),
        "type": type
    })
    async with engine.begin() as conn:
        await conn.execute(sql)


async def delete_premium(id: int) -> None:
    sql = delete(Premium).where(Premium.id == id)
    async with engine.begin() as conn:
        await conn.execute(sql)


async def db_init():
    await create_tables()
