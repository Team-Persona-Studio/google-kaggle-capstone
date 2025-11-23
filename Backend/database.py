import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306)),
}

# TiDB Cloud requires SSL
if os.getenv("DB_CA"):
    DB_CONFIG["ssl_disabled"] = False
    DB_CONFIG["ssl_verify_cert"] = True
    DB_CONFIG["ssl_verify_identity"] = True

def get_db_conn():
    return mysql.connector.connect(**DB_CONFIG)
