import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from mysql.connector import pooling, Error, errors
from contextlib import contextmanager
from makefast.base_model.mysql import MySQLBase

load_dotenv()


class MySQLDatabaseInit:
    pool = None
    last_pool_recreation = 0
    POOL_RECREATION_INTERVAL = 300

    @staticmethod
    def init(app: FastAPI):
        @app.on_event("startup")
        async def startup_db_client():
            print("🔄 Initializing MySQL pool...")
            MySQLDatabaseInit.wait_for_database()
            MySQLBase.set_database(MySQLDatabaseInit.pool)
            print("✅ MySQL pool initialized.")

        @app.on_event("shutdown")
        async def shutdown_db_client():
            print("🛑 Closing MySQL pool...")
            if MySQLDatabaseInit.pool:
                try:
                    MySQLDatabaseInit.pool._remove_connections()
                except:
                    pass
        
        @app.middleware("http")
        async def db_connection_middleware(request: Request, call_next):
            try:
                response = await call_next(request)
                return response
            except (errors.InterfaceError, errors.OperationalError) as e:
                print(f"⚠️ Database connection error: {e}")
                # Try to recreate pool on connection error
                MySQLDatabaseInit.recreate_pool_if_needed(force=True)
                # Retry the request
                response = await call_next(request)
                return response

    @staticmethod
    def recreate_pool_if_needed(force=False):
        current_time = time.time()
        if force or (current_time - MySQLDatabaseInit.last_pool_recreation > MySQLDatabaseInit.POOL_RECREATION_INTERVAL):
            print("♻️ Recreating MySQL connection pool...")
            try:
                old_pool = MySQLDatabaseInit.pool
                MySQLDatabaseInit.pool = MySQLDatabaseInit.create_pool()
                
                # Test the new pool
                conn = MySQLDatabaseInit.pool.get_connection()
                conn.close()
                
                if old_pool:
                    try:
                        old_pool._remove_connections()
                    except:
                        pass
                
                MySQLDatabaseInit.last_pool_recreation = current_time
                MySQLBase.set_database(MySQLDatabaseInit.pool)
                print("✅ MySQL pool recreated successfully.")
            except Exception as e:
                print(f"❌ Failed to recreate pool: {e}")
                # Keep old pool if recreation failed
                if not MySQLDatabaseInit.pool and old_pool:
                    MySQLDatabaseInit.pool = old_pool

    @staticmethod
    def create_pool():
        return pooling.MySQLConnectionPool(
            pool_name=f"main_pool_{int(time.time())}",
            pool_size=5,
            pool_reset_session=True,
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
            port=int(os.getenv("DB_PORT", 3306)),
            connect_timeout=30,
            autocommit=True,
            connection_timeout=30,
            use_pure=True,
            buffered=True,
            retries=3,
            delay=1,
            pool_recycle=3600,
        )

    @staticmethod
    def wait_for_database(retries=30, delay=2):  # Increased retries and delay
        for attempt in range(1, retries + 1):
            try:
                print(f"⏳ Connecting to MySQL... attempt {attempt}/{retries}")
                MySQLDatabaseInit.pool = MySQLDatabaseInit.create_pool()

                # Test one connection with a simple query
                conn = MySQLDatabaseInit.pool.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                conn.close()

                print("✔ MySQL is reachable.")
                MySQLDatabaseInit.last_pool_recreation = time.time()
                return
            except Error as e:
                print(f"🚫 MySQL not ready: {str(e)}")
                if attempt == retries:
                    print("⚠️ Last attempt failed, will continue but connection may be unstable")
                    # Create pool anyway to allow application to start
                    MySQLDatabaseInit.pool = MySQLDatabaseInit.create_pool()
                    MySQLDatabaseInit.last_pool_recreation = time.time()
                    return
                time.sleep(delay)

    @staticmethod
    @contextmanager
    def get_connection():
        """Context manager for getting connections with retry logic"""
        max_retries = 3
        for retry in range(max_retries):
            try:
                if MySQLDatabaseInit.pool is None:
                    MySQLDatabaseInit.wait_for_database()
                
                conn = MySQLDatabaseInit.pool.get_connection()
                # Test connection before yielding
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                
                yield conn
                break  # Success, exit retry loop
                
            except (errors.InterfaceError, errors.OperationalError) as e:
                print(f"⚠️ Connection failed (attempt {retry + 1}/{max_retries}): {e}")
                
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
                
                if retry < max_retries - 1:
                    # Recreate pool on connection error
                    MySQLDatabaseInit.recreate_pool_if_needed(force=True)
                    time.sleep(1)
                else:
                    raise Exception(f"❌ Failed to get database connection after {max_retries} retries")
            finally:
                if 'conn' in locals() and conn:
                    try:
                        conn.close()
                    except:
                        pass
