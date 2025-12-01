import mysql.connector
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

def get_db_conn():
    # Get port with proper handling of empty strings
    db_port = os.getenv("DB_PORT", "4000")
    port = int(db_port) if db_port else 4000
    
    config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "port": port,
        "autocommit": True,
    }

    # TiDB Cloud / SSL Configuration
    # If DB_SSL_CA is set, use it. Otherwise, use certifi's bundle.
    # TiDB Cloud requires SSL.
    ssl_mode = os.getenv("DB_SSL_MODE", "PREFERRED") # DISABLED, PREFERRED, REQUIRED, VERIFY_CA, VERIFY_IDENTITY
    
    if ssl_mode != "DISABLED":
        config["ssl_ca"] = os.getenv("DB_SSL_CA", certifi.where())
        config["ssl_verify_cert"] = True
        config["ssl_verify_identity"] = True

    try:
        return mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        print(f"❌ Database Connection Error: {err}")
        raise err
