"""Model base class and metaclass"""

from typing import Any, Dict, List, Optional, Type, ClassVar
from datetime import datetime

from .fields import Field, ForeignKeyField, DateTimeField, DateField
from .query import QueryBuilder, Q
from .exceptions import DoesNotExist, MultipleObjectsReturned, ConfigurationError


class ModelOptions:
    """Model metadata"""

    def __init__(self, meta=None):
        self.table_name = None
        self.database = None
        self.indexes = []
        self.ordering = []
        
        if meta:
            for attr in dir(meta):
                if not attr.startswith('_'):
                    setattr(self, attr, getattr(meta, attr))


class ModelMeta(type):
    """Metaclass for Model"""

    def __new__(mcs, name, bases, attrs):
        # Don't process Model class itself
        if name == 'Model':
            return super().__new__(mcs, name, bases, attrs)

        # Collect fields
        fields = {}
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                value.name = key
                fields[key] = value

        # Get Meta options
        meta = attrs.pop('Meta', None)
        options = ModelOptions(meta)

        # Set table name
        if not options.table_name:
            options.table_name = name.lower() + 's'

        # Create new class
        new_class = super().__new__(mcs, name, bases, attrs)
        new_class._meta = options
        new_class._fields = fields

        # Set model reference in fields
        for field in fields.values():
            field.model = new_class

        return new_class


class Model(metaclass=ModelMeta):
    """Base model class"""

    _meta: ClassVar[ModelOptions]
    _fields: ClassVar[Dict[str, Field]]

    def __init__(self, **kwargs):
        self._data = {}
        self._is_saved = False

        # Set primary key
        if 'id' not in self._fields:
            from .fields import IntField
            id_field = IntField(primary_key=True, auto_increment=True)
            id_field.name = 'id'
            id_field.model = self.__class__
            self._fields['id'] = id_field

        # Initialize fields with defaults
        for name, field in self._fields.items():
            if name in kwargs:
                setattr(self, name, kwargs[name])
            elif field.default is not None:
                setattr(self, name, field.get_default())
            else:
                self._data[name] = None

    def __setattr__(self, name: str, value: Any):
        if name.startswith('_'):
            super().__setattr__(name, value)
        elif name in self._fields:
            self._data[name] = value
        else:
            super().__setattr__(name, value)

    def __getattribute__(self, name: str):
        if name.startswith('_') or name in ('save', 'delete', 'refresh', 'to_dict'):
            return super().__getattribute__(name)
        
        fields = super().__getattribute__('_fields')
        if name in fields:
            data = super().__getattribute__('_data')
            return data.get(name)
        
        return super().__getattribute__(name)

    @classmethod
    def select(cls, *fields) -> QueryBuilder:
        """Create a SELECT query"""
        query = QueryBuilder(cls)
        if fields:
            query._select_fields = list(fields)
        return query

    @classmethod
    async def get(cls, **kwargs) -> 'Model':
        """Get a single object"""
        results = await cls.select().where(**kwargs).execute()
        
        if not results:
            raise DoesNotExist(f"{cls.__name__} matching query does not exist")
        
        if len(results) > 1:
            raise MultipleObjectsReturned(f"get() returned more than one {cls.__name__}")
        
        return results[0]

    @classmethod
    async def get_or_none(cls, **kwargs) -> Optional['Model']:
        """Get a single object or None"""
        try:
            return await cls.get(**kwargs)
        except DoesNotExist:
            return None

    @classmethod
    async def create(cls, **kwargs) -> 'Model':
        """Create and save a new object"""
        instance = cls(**kwargs)
        await instance.save()
        return instance

    @classmethod
    async def get_or_create(cls, defaults=None, **kwargs) -> tuple['Model', bool]:
        """Get or create an object"""
        try:
            instance = await cls.get(**kwargs)
            return instance, False
        except DoesNotExist:
            create_kwargs = kwargs.copy()
            if defaults:
                create_kwargs.update(defaults)
            instance = await cls.create(**create_kwargs)
            return instance, True

    @classmethod
    async def filter(cls, **kwargs) -> List['Model']:
        """Filter objects"""
        return await cls.select().where(**kwargs).execute()

    @classmethod
    async def all(cls) -> List['Model']:
        """Get all objects"""
        return await cls.select().execute()

    async def save(self, force_insert: bool = False, force_update: bool = False):
        """Save the object to database"""
        database = self._meta.database
        if not database:
            raise ConfigurationError("No database configured for this model")

        table_name = self._meta.table_name
        placeholder = database.get_placeholder()

        # Update auto_now fields
        for name, field in self._fields.items():
            if isinstance(field, (DateTimeField, DateField)):
                if field.auto_now:
                    self._data[name] = datetime.now()

        # Get primary key field
        pk_field = None
        for name, field in self._fields.items():
            if field.primary_key:
                pk_field = name
                break

        pk_value = self._data.get(pk_field) if pk_field else None

        if force_insert or (not self._is_saved and not pk_value):
            # INSERT
            fields_to_insert = []
            values = []
            
            for name, field in self._fields.items():
                if field.auto_increment and not self._data.get(name):
                    continue
                if name in self._data and self._data[name] is not None:
                    fields_to_insert.append(field.get_column_name())
                    values.append(field.to_db(self._data[name]))

            if not fields_to_insert:
                return

            placeholders = ', '.join([placeholder] * len(values))
            query = f"INSERT INTO {table_name} ({', '.join(fields_to_insert)}) VALUES ({placeholders})"
            
            # Handle PostgreSQL RETURNING clause
            if isinstance(database, type(database)) and database.__class__.__name__ == 'PostgreSQLDatabase':
                query += f" RETURNING {pk_field}"
                result = await database.fetch_one(query, tuple(values))
                if result and pk_field:
                    self._data[pk_field] = result[pk_field]
            else:
                await database.execute(query, tuple(values))
                if pk_field and not self._data.get(pk_field):
                    self._data[pk_field] = await database.get_last_insert_id()

        else:
            # UPDATE
            if not pk_value:
                raise ValueError("Cannot update object without primary key")

            fields_to_update = []
            values = []
            
            for name, field in self._fields.items():
                if field.primary_key:
                    continue
                if name in self._data:
                    fields_to_update.append(f"{field.get_column_name()} = {placeholder}")
                    values.append(field.to_db(self._data[name]))

            if not fields_to_update:
                return

            values.append(pk_value)
            query = f"UPDATE {table_name} SET {', '.join(fields_to_update)} WHERE {pk_field} = {placeholder}"
            await database.execute(query, tuple(values))

        self._is_saved = True

    async def delete(self):
        """Delete the object from database"""
        database = self._meta.database
        if not database:
            raise ConfigurationError("No database configured for this model")

        # Get primary key
        pk_field = None
        for name, field in self._fields.items():
            if field.primary_key:
                pk_field = name
                break

        if not pk_field or not self._data.get(pk_field):
            raise ValueError("Cannot delete object without primary key")

        table_name = self._meta.table_name
        placeholder = database.get_placeholder()
        query = f"DELETE FROM {table_name} WHERE {pk_field} = {placeholder}"
        
        await database.execute(query, (self._data[pk_field],))
        self._is_saved = False

    async def refresh(self):
        """Refresh object from database"""
        pk_field = None
        for name, field in self._fields.items():
            if field.primary_key:
                pk_field = name
                break

        if not pk_field or not self._data.get(pk_field):
            raise ValueError("Cannot refresh object without primary key")

        refreshed = await self.__class__.get(**{pk_field: self._data[pk_field]})
        self._data = refreshed._data
        self._is_saved = refreshed._is_saved

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {}
        for name, field in self._fields.items():
            value = self._data.get(name)
            if value is not None:
                result[name] = field.to_python(value)
        return result

    @classmethod
    def _from_db(cls, row: Dict[str, Any]) -> 'Model':
        """Create instance from database row"""
        instance = cls.__new__(cls)
        instance._data = {}
        instance._is_saved = True
        
        for name, field in cls._fields.items():
            column_name = field.get_column_name()
            if column_name in row:
                instance._data[name] = field.to_python(row[column_name])
        
        return instance

    @classmethod
    async def create_table(cls, safe: bool = True):
        """Create table for this model"""
        database = cls._meta.database
        if not database:
            raise ConfigurationError("No database configured for this model")

        table_name = cls._meta.table_name
        database_type = database.__class__.__name__.replace('Database', '').lower()

        columns = []
        for name, field in cls._fields.items():
            column_def = f"{field.get_column_name()} {field.get_sql_type(database_type)}"
            
            if field.primary_key:
                column_def += " PRIMARY KEY"
                if field.auto_increment:
                    if database_type == 'sqlite':
                        column_def += " AUTOINCREMENT"
                    elif database_type == 'mysql':
                        column_def += " AUTO_INCREMENT"
                    elif database_type == 'postgresql':
                        column_def = f"{field.get_column_name()} SERIAL PRIMARY KEY"
            
            if field.unique and not field.primary_key:
                column_def += " UNIQUE"
            
            if not field.null and not field.primary_key:
                column_def += " NOT NULL"
            
            if field.default is not None and not field.auto_increment and not callable(field.default):
                if isinstance(field.default, str):
                    column_def += f" DEFAULT '{field.default}'"
                else:
                    column_def += f" DEFAULT {field.default}"

            columns.append(column_def)

        # Add foreign key constraints
        for name, field in cls._fields.items():
            if isinstance(field, ForeignKeyField):
                related_table = field.related_model._meta.table_name
                fk_constraint = f"FOREIGN KEY ({field.get_column_name()}) REFERENCES {related_table}(id) ON DELETE {field.on_delete} ON UPDATE {field.on_update}"
                columns.append(fk_constraint)

        safe_clause = "IF NOT EXISTS " if safe else ""
        query = f"CREATE TABLE {safe_clause}{table_name} ({', '.join(columns)})"
        
        await database.execute(query)

    @classmethod
    async def drop_table(cls, safe: bool = True):
        """Drop table for this model"""
        database = cls._meta.database
        if not database:
            raise ConfigurationError("No database configured for this model")

        table_name = cls._meta.table_name
        safe_clause = "IF EXISTS " if safe else ""
        query = f"DROP TABLE {safe_clause}{table_name}"
        
        await database.execute(query)

    def __repr__(self):
        pk_field = None
        for name, field in self._fields.items():
            if field.primary_key:
                pk_field = name
                break
        
        pk_value = self._data.get(pk_field) if pk_field else None
        return f"<{self.__class__.__name__}: {pk_value}>"