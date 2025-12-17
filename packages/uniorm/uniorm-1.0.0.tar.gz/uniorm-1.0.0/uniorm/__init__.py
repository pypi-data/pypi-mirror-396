"""
UniORM - Universal Async ORM
A powerful async ORM supporting SQLite, MySQL, and PostgreSQL
"""

__version__ = "1.0.0"
__author__ = "oscoderuz"

from .database import (
    Database,
    SqliteDatabase,
    MySQLDatabase,
    PostgreSQLDatabase,
)
from .fields import (
    Field,
    CharField,
    TextField,
    IntField,
    BigIntField,
    FloatField,
    BoolField,
    DateField,
    DateTimeField,
    TimeField,
    JSONField,
    ForeignKeyField,
)
from .models import Model
from .query import Q
from .exceptions import (
    UniORMException,
    DatabaseError,
    IntegrityError,
    DoesNotExist,
    MultipleObjectsReturned,
)
from .migrations import MigrationManager

__all__ = [
    # Database
    "Database",
    "SqliteDatabase",
    "MySQLDatabase",
    "PostgreSQLDatabase",
    # Fields
    "Field",
    "CharField",
    "TextField",
    "IntField",
    "BigIntField",
    "FloatField",
    "BoolField",
    "DateField",
    "DateTimeField",
    "TimeField",
    "JSONField",
    "ForeignKeyField",
    # Models
    "Model",
    # Query
    "Q",
    # Exceptions
    "UniORMException",
    "DatabaseError",
    "IntegrityError",
    "DoesNotExist",
    "MultipleObjectsReturned",
    # Migrations
    "MigrationManager",
]