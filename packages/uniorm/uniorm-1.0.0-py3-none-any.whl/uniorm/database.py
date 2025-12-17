"""Database connection and management"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from contextlib import asynccontextmanager

try:
    import aiosqlite
except ImportError:
    aiosqlite = None

try:
    import asyncmy
except ImportError:
    asyncmy = None

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    psycopg = None

from .exceptions import DatabaseError, ConfigurationError


class Database(ABC):
    """Abstract base class for database connections"""

    def __init__(self, database: str, **kwargs):
        self.database = database
        self.connection_params = kwargs
        self._connection = None
        self._is_connected = False
        self._pool = None

    @abstractmethod
    async def connect(self):
        """Establish database connection"""
        pass

    @abstractmethod
    async def close(self):
        """Close database connection"""
        pass

    @abstractmethod
    async def execute(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute a query"""
        pass

    @abstractmethod
    async def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict]:
        """Fetch one row"""
        pass

    @abstractmethod
    async def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """Fetch all rows"""
        pass

    @abstractmethod
    async def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Execute query multiple times"""
        pass

    @abstractmethod
    def get_placeholder(self) -> str:
        """Get parameter placeholder for this database"""
        pass

    @abstractmethod
    async def get_last_insert_id(self) -> int:
        """Get last inserted ID"""
        pass

    @abstractmethod
    async def begin_transaction(self):
        """Begin a transaction"""
        pass

    @abstractmethod
    async def commit(self):
        """Commit transaction"""
        pass

    @abstractmethod
    async def rollback(self):
        """Rollback transaction"""
        pass

    @asynccontextmanager
    async def transaction(self):
        """Context manager for transactions"""
        await self.begin_transaction()
        try:
            yield
            await self.commit()
        except Exception:
            await self.rollback()
            raise

    async def create_tables(self, models: List['Model']):
        """Create tables for given models"""
        for model in models:
            await model.create_table()

    async def drop_tables(self, models: List['Model']):
        """Drop tables for given models"""
        for model in models:
            await model.drop_table()

    @property
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._is_connected


class SqliteDatabase(Database):
    """SQLite database implementation"""

    def __init__(self, database: str, **kwargs):
        if aiosqlite is None:
            raise ConfigurationError("aiosqlite is not installed. Install it with: pip install aiosqlite")
        super().__init__(database, **kwargs)

    async def connect(self):
        """Connect to SQLite database"""
        if not self._is_connected:
            self._connection = await aiosqlite.connect(self.database, **self.connection_params)
            self._connection.row_factory = aiosqlite.Row
            self._is_connected = True

    async def close(self):
        """Close SQLite connection"""
        if self._connection:
            await self._connection.close()
            self._is_connected = False

    async def execute(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute query"""
        if not self._is_connected:
            await self.connect()
        cursor = await self._connection.execute(query, params or ())
        await self._connection.commit()
        return cursor

    async def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict]:
        """Fetch one row"""
        if not self._is_connected:
            await self.connect()
        cursor = await self._connection.execute(query, params or ())
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """Fetch all rows"""
        if not self._is_connected:
            await self.connect()
        cursor = await self._connection.execute(query, params or ())
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Execute many"""
        if not self._is_connected:
            await self.connect()
        await self._connection.executemany(query, params_list)
        await self._connection.commit()

    def get_placeholder(self) -> str:
        """Get placeholder"""
        return "?"

    async def get_last_insert_id(self) -> int:
        """Get last insert ID"""
        cursor = await self._connection.execute("SELECT last_insert_rowid()")
        row = await cursor.fetchone()
        return row[0]

    async def begin_transaction(self):
        """Begin transaction"""
        await self._connection.execute("BEGIN")

    async def commit(self):
        """Commit transaction"""
        await self._connection.commit()

    async def rollback(self):
        """Rollback transaction"""
        await self._connection.rollback()


class MySQLDatabase(Database):
    """MySQL database implementation"""

    def __init__(self, database: str, host: str = "localhost", port: int = 3306,
                 user: str = "root", password: str = "", **kwargs):
        if asyncmy is None:
            raise ConfigurationError("asyncmy is not installed. Install it with: pip install asyncmy")
        super().__init__(database, **kwargs)
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    async def connect(self):
        """Connect to MySQL"""
        if not self._is_connected:
            self._connection = await asyncmy.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.database,
                **self.connection_params
            )
            self._is_connected = True

    async def close(self):
        """Close connection"""
        if self._connection:
            self._connection.close()
            await self._connection.wait_closed()
            self._is_connected = False

    async def execute(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute query"""
        if not self._is_connected:
            await self.connect()
        async with self._connection.cursor() as cursor:
            await cursor.execute(query, params or ())
            await self._connection.commit()
            return cursor

    async def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict]:
        """Fetch one row"""
        if not self._is_connected:
            await self.connect()
        async with self._connection.cursor(asyncmy.DictCursor) as cursor:
            await cursor.execute(query, params or ())
            return await cursor.fetchone()

    async def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """Fetch all rows"""
        if not self._is_connected:
            await self.connect()
        async with self._connection.cursor(asyncmy.DictCursor) as cursor:
            await cursor.execute(query, params or ())
            return await cursor.fetchall()

    async def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Execute many"""
        if not self._is_connected:
            await self.connect()
        async with self._connection.cursor() as cursor:
            await cursor.executemany(query, params_list)
            await self._connection.commit()

    def get_placeholder(self) -> str:
        """Get placeholder"""
        return "%s"

    async def get_last_insert_id(self) -> int:
        """Get last insert ID"""
        async with self._connection.cursor() as cursor:
            await cursor.execute("SELECT LAST_INSERT_ID()")
            row = await cursor.fetchone()
            return row[0]

    async def begin_transaction(self):
        """Begin transaction"""
        await self._connection.begin()

    async def commit(self):
        """Commit"""
        await self._connection.commit()

    async def rollback(self):
        """Rollback"""
        await self._connection.rollback()


class PostgreSQLDatabase(Database):
    """PostgreSQL database implementation"""

    def __init__(self, database: str, host: str = "localhost", port: int = 5432,
                 user: str = "postgres", password: str = "", **kwargs):
        if psycopg is None:
            raise ConfigurationError("psycopg is not installed. Install it with: pip install psycopg[binary]")
        super().__init__(database, **kwargs)
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    async def connect(self):
        """Connect to PostgreSQL"""
        if not self._is_connected:
            conninfo = f"host={self.host} port={self.port} dbname={self.database} user={self.user} password={self.password}"
            self._connection = await psycopg.AsyncConnection.connect(conninfo, row_factory=dict_row)
            self._is_connected = True

    async def close(self):
        """Close connection"""
        if self._connection:
            await self._connection.close()
            self._is_connected = False

    async def execute(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute query"""
        if not self._is_connected:
            await self.connect()
        async with self._connection.cursor() as cursor:
            await cursor.execute(query, params or ())
            await self._connection.commit()
            return cursor

    async def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict]:
        """Fetch one row"""
        if not self._is_connected:
            await self.connect()
        async with self._connection.cursor() as cursor:
            await cursor.execute(query, params or ())
            return await cursor.fetchone()

    async def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """Fetch all rows"""
        if not self._is_connected:
            await self.connect()
        async with self._connection.cursor() as cursor:
            await cursor.execute(query, params or ())
            return await cursor.fetchall()

    async def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Execute many"""
        if not self._is_connected:
            await self.connect()
        async with self._connection.cursor() as cursor:
            for params in params_list:
                await cursor.execute(query, params)
            await self._connection.commit()

    def get_placeholder(self) -> str:
        """Get placeholder"""
        return "%s"

    async def get_last_insert_id(self) -> int:
        """Get last insert ID (PostgreSQL uses RETURNING clause)"""
        # This is handled in the insert query itself
        return 0

    async def begin_transaction(self):
        """Begin transaction"""
        await self._connection.execute("BEGIN")

    async def commit(self):
        """Commit"""
        await self._connection.commit()

    async def rollback(self):
        """Rollback"""
        await self._connection.rollback()