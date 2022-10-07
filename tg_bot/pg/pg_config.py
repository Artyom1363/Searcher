import os
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv("PG_HOST")
PG_DB_NAME = os.getenv("PG_DB_NAME")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_USER = os.getenv("PG_USER")