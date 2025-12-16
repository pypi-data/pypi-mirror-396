"""
Database configuration and connection management
"""
from contextlib import contextmanager
from typing import Generator, Optional
import psycopg2
import psycopg2.pool
from psycopg2.extras import RealDictCursor
from .settings import db_settings
from .logging import get_logger

logger = get_logger("database")

# Database connection pool
_connection_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None


class DatabaseConfig:
    """Database configuration and connection management"""

    def __init__(self):
        self.settings = db_settings
        self.database_url = self.settings.database_url
        self.pool_size = 5
        self.max_overflow = 10

    def get_connection_params(self) -> dict:
        """Get database connection parameters"""
        if self.settings.DATABASE_URL:
            # Use full DATABASE_URL if available
            return {
                "dsn": self.settings.DATABASE_URL,
                "cursor_factory": RealDictCursor,
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
                "connect_timeout": 10
            }

        # fallback to individual DB_* variables
        return {
            "host": self.settings.DB_HOST,
            "port": self.settings.DB_PORT,
            "database": self.settings.DB_NAME,
            "user": self.settings.DB_USER,
            "password": self.settings.DB_PASSWORD,
            "cursor_factory": RealDictCursor,
            "application_name": f"{self.settings.APP_NAME}_{self.settings.ENVIRONMENT}",
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
            "connect_timeout": 10
        }

    def create_connection_pool(self) -> psycopg2.pool.ThreadedConnectionPool:
        """Create a connection pool for psycopg2"""
        try:
            pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=self.pool_size,
                **self.get_connection_params()
            )
            logger.info(f"Database connection pool created with {self.pool_size} connections")
            return pool
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with psycopg2.connect(**self.get_connection_params()) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    if result:
                        logger.info("Database connection test successful")
                        return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
        return False


# Global database configuration
db_config = DatabaseConfig()


def initialize_database():
    """Initialize database connections and pool"""
    global _connection_pool

    try:
        # Test connection first
        if not db_config.test_connection():
            raise Exception("Database connection test failed")

        # Create connection pool
        _connection_pool = db_config.create_connection_pool()

        logger.info("Database initialization completed successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


def get_connection_pool() -> psycopg2.pool.ThreadedConnectionPool:
    """Get the database connection pool"""
    global _connection_pool
    if _connection_pool is None:
        error_msg = (
            "Database not initialized. This usually means:\n"
            "1. Missing or incorrect .env file in app/ directory\n"
            "2. Database credentials are wrong\n"
            "3. Database container is not running\n"
            "4. Database initialization failed during startup\n"
            "Please check the startup logs for more details."
        )
        logger.error(error_msg)
        raise Exception(error_msg)
    return _connection_pool


def _validate_connection(conn) -> bool:
    """Validate if a connection is still alive"""
    try:
        # Test if connection is alive with a simple query
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
        return False


@contextmanager
def get_db_connection():
    """Get a database connection from the pool (context manager)"""
    pool = get_connection_pool()
    conn = None
    try:
        conn = pool.getconn()

        # Validate connection before using it
        if not _validate_connection(conn):
            logger.warning("Stale connection detected, getting new connection")
            pool.putconn(conn, close=True)
            conn = pool.getconn()

        logger.debug("Database connection acquired from pool")
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        if conn:
            try:
                # Only rollback if connection is still open
                if not conn.closed:
                    conn.rollback()
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as rollback_error:
                logger.warning(f"Could not rollback closed connection: {str(rollback_error)}")
        raise
    finally:
        if conn:
            try:
                # If connection is broken, close it instead of returning to pool
                if conn.closed:
                    pool.putconn(conn, close=True)
                else:
                    pool.putconn(conn)
                logger.debug("Database connection returned to pool")
            except Exception as put_error:
                logger.error(f"Error returning connection to pool: {str(put_error)}")


@contextmanager
def get_db_cursor():
    """Get a database cursor (context manager)"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            if not conn.closed:
                conn.commit()
        except Exception as e:
            if not conn.closed:
                try:
                    conn.rollback()
                except (psycopg2.OperationalError, psycopg2.InterfaceError) as rollback_error:
                    logger.warning(f"Could not rollback transaction on closed connection: {str(rollback_error)}")
            logger.error(f"Database cursor error: {str(e)}")
            raise
        finally:
            try:
                cursor.close()
            except Exception as close_error:
                logger.warning(f"Error closing cursor: {str(close_error)}")


class DatabaseManager:
    """Database manager for common operations"""

    @staticmethod
    def execute_query(query: str, params: tuple = None) -> list:
        """Execute a SELECT query and return results"""
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def execute_update(query: str, params: tuple = None) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount

    @staticmethod
    def execute_scalar(query: str, params: tuple = None):
        """Execute a query and return a single value"""
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result:
                # Handle RealDictRow (dictionary-like) result
                if hasattr(result, 'get'):
                    # For RealDictRow, get the first value
                    return list(result.values())[0] if result else None
                else:
                    # Handle tuple result
                    return result[0] if len(result) > 0 else None
            return None

    @staticmethod
    @contextmanager
    def transaction():
        """
        Context manager for database transactions.
        Wraps multiple operations in a single transaction.

        Usage:
            with DatabaseManager.transaction() as cursor:
                cursor.execute("INSERT INTO table1 ...")
                cursor.execute("INSERT INTO table2 ...")
                # Auto-commits on success, auto-rollbacks on exception
        """
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
                if not conn.closed:
                    conn.commit()
                    logger.debug("Transaction committed successfully")
            except Exception as e:
                if not conn.closed:
                    try:
                        conn.rollback()
                        logger.warning(f"Transaction rolled back due to error: {str(e)}")
                    except (psycopg2.OperationalError, psycopg2.InterfaceError) as rollback_error:
                        logger.error(f"Could not rollback transaction: {str(rollback_error)}")
                raise
            finally:
                try:
                    cursor.close()
                except Exception as close_error:
                    logger.warning(f"Error closing transaction cursor: {str(close_error)}")

    @staticmethod
    def health_check() -> dict:
        """Perform database health check"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT version(), current_database(), current_user")
                result = cursor.fetchone()

                if result:
                    # Handle RealDictRow (dictionary-like) result
                    if hasattr(result, 'get'):
                        return {
                            "status": "healthy",
                            "database": result.get('current_database', 'unknown'),
                            "user": result.get('current_user', 'unknown'),
                            "version": result.get('version', 'unknown')
                        }
                    else:
                        # Handle tuple result
                        return {
                            "status": "healthy",
                            "database": result[1] if len(result) > 1 else "unknown",
                            "user": result[2] if len(result) > 2 else "unknown",
                            "version": result[0] if len(result) > 0 else "unknown"
                        }
                else:
                    return {
                        "status": "unhealthy",
                        "error": "No result from database query"
                    }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# NOTE: Database initialization is NOT automatic
# You must call initialize_database() explicitly in your application startup
# Example in FastAPI:
#   @app.on_event("startup")
#   async def startup_event():
#       initialize_database()