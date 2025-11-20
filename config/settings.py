# config/settings.py
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "imadwi_data_platform")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
