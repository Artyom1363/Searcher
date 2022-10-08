import asyncpg
import asyncio
from .pg_config import *


async def create_db():

    create_db_command = open("docker-entrypoint-initdb.d/create_user_info.sql", "r").read()
    print("creating db")
    conn: asyncpg.Connection = await asyncpg.connect(
        host=HOST,
        user=PG_USER,
        password=PG_PASSWORD,
        database=PG_DB_NAME
    )
    await conn.execute(create_db_command)
    print("end of creating")
    await conn.close()


async def create_pool():

    return await asyncpg.create_pool(
        host=HOST,
        user=PG_USER,
        password=PG_PASSWORD,
        database=PG_DB_NAME
    )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db())
