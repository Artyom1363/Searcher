from src.pg import create_pool
import asyncio


loop = asyncio.get_event_loop()
pool = loop.run_until_complete(create_pool())
