"""Field types for models"""

import json
from datetime import datetime, date, time
from typing import Any, Optional, Type, Callable


class Field:
    """Base field class"""

    def __init__(
        self,
        null: bool = False,
        default: Any = None,
        unique: bool = False,
        index: bool = False,
        primary_key: bool = False,
        auto_increment: bool = False,
        column_name: Optional[str] = None,
        verbose_name: Optional[str] = None,
        help_text: Optional[str] = None,
    ):
        self.null = null
        self.default = default
        self.unique = unique
        self.index = index
        self.primary_key = primary_key
        self.auto_increment = auto_increment
        self.column_name = column_name
        self.verbose_name = verbose_name
        self.help_text = help_text
        self.name = None  # Set by metaclass
        self.model = None  # Set by metaclass

    def get_column_name(self) -> str:
        """Get database column name"""
        return self.column_name or self.name

    def to_python(self, value: Any) -> Any:
        """Convert database value to Python value"""
        if value is None:
            return None
        return value

    def to_db(self, value: Any) -> Any:
        """Convert Python value to database value"""
        if value is None:
            return None
        return value

    def get_sql_type(self, database_type: str) -> str:
        """Get SQL type for this field"""
        raise NotImplementedError

    def get_default(self) -> Any:
        """Get default value"""
        if callable(self.default):
            return self.default()
        return self.default


class CharField(Field):
    """Character field"""

    def __init__(self, max_length: int = 255, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length

    def get_sql_type(self, database_type: str) -> str:
        return f"VARCHAR({self.max_length})"


class TextField(Field):
    """Text field"""

    def get_sql_type(self, database_type: str) -> str:
        return "TEXT"


class IntField(Field):
    """Integer field"""

    def to_python(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        return int(value)

    def get_sql_type(self, database_type: str) -> str:
        return "INTEGER"


class BigIntField(Field):
    """Big integer field"""

    def to_python(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        return int(value)

    def get_sql_type(self, database_type: str) -> str:
        return "BIGINT"


class FloatField(Field):
    """Float field"""

    def to_python(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        return float(value)

    def get_sql_type(self, database_type: str) -> str:
        return "REAL"


class BoolField(Field):
    """Boolean field"""

    def to_python(self, value: Any) -> Optional[bool]:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        return value in (1, '1', 'true', 'True', 'TRUE', 't', 'T')

    def to_db(self, value: Any) -> Any:
        if value is None:
            return None
        return 1 if value else 0

    def get_sql_type(self, database_type: str) -> str:
        if database_type == "postgresql":
            return "BOOLEAN"
        return "INTEGER"


class DateField(Field):
    """Date field"""

    def __init__(self, auto_now: bool = False, auto_now_add: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add

    def to_python(self, value: Any) -> Optional[date]:
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value).date()
        return value

    def to_db(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, date):
            return value.isoformat()
        return value

    def get_sql_type(self, database_type: str) -> str:
        return "DATE"


class DateTimeField(Field):
    """DateTime field"""

    def __init__(self, auto_now: bool = False, auto_now_add: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add
        if auto_now_add and not self.default:
            self.default = datetime.now

    def to_python(self, value: Any) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value

    def to_db(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    def get_sql_type(self, database_type: str) -> str:
        if database_type == "postgresql":
            return "TIMESTAMP"
        return "DATETIME"


class TimeField(Field):
    """Time field"""

    def to_python(self, value: Any) -> Optional[time]:
        if value is None:
            return None
        if isinstance(value, time):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(f"2000-01-01 {value}").time()
        return value

    def to_db(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, time):
            return value.isoformat()
        return value

    def get_sql_type(self, database_type: str) -> str:
        return "TIME"


class JSONField(Field):
    """JSON field"""

    def to_python(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            return json.loads(value)
        return value

    def to_db(self, value: Any) -> Any:
        if value is None:
            return None
        return json.dumps(value)

    def get_sql_type(self, database_type: str) -> str:
        if database_type == "postgresql":
            return "JSONB"
        return "TEXT"


class ForeignKeyField(Field):
    """Foreign key field"""

    def __init__(self, model: Type['Model'], on_delete: str = "CASCADE",
                 on_update: str = "CASCADE", **kwargs):
        super().__init__(**kwargs)
        self.related_model = model
        self.on_delete = on_delete
        self.on_update = on_update

    def get_sql_type(self, database_type: str) -> str:
        return "INTEGER"

    def get_column_name(self) -> str:
        """Get column name with _id suffix"""
        base_name = self.column_name or self.name
        if not base_name.endswith('_id'):
            base_name += '_id'
        return base_name