"""Query builder for UniORM"""

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .models import Model


class JoinType(Enum):
    """Join types"""
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL OUTER JOIN"


class Q:
    """Query condition builder"""

    def __init__(self, **kwargs):
        self.conditions = kwargs
        self.connector = "AND"
        self.negated = False
        self.children = []

    def __and__(self, other):
        """AND operation"""
        q = Q()
        q.connector = "AND"
        q.children = [self, other]
        return q

    def __or__(self, other):
        """OR operation"""
        q = Q()
        q.connector = "OR"
        q.children = [self, other]
        return q

    def __invert__(self):
        """NOT operation"""
        q = Q(**self.conditions)
        q.negated = not self.negated
        q.children = self.children
        q.connector = self.connector
        return q


class QueryBuilder:
    """SQL query builder"""

    def __init__(self, model: 'Model'):
        self.model = model
        self._where_conditions = []
        self._where_params = []
        self._order_by = []
        self._limit_value = None
        self._offset_value = None
        self._select_fields = []
        self._joins = []
        self._group_by = []
        self._having_conditions = []

    def where(self, *args, **kwargs) -> 'QueryBuilder':
        """Add WHERE conditions"""
        if args:
            for arg in args:
                if isinstance(arg, Q):
                    self._process_q_object(arg)
        
        if kwargs:
            for key, value in kwargs.items():
                self._add_condition(key, value)
        
        return self

    def _add_condition(self, key: str, value: Any):
        """Add a single condition"""
        parts = key.split('__')
        field_name = parts[0]
        operator = parts[1] if len(parts) > 1 else 'exact'

        placeholder = self.model._meta.database.get_placeholder()

        if operator == 'exact':
            self._where_conditions.append(f"{field_name} = {placeholder}")
            self._where_params.append(value)
        elif operator == 'gt':
            self._where_conditions.append(f"{field_name} > {placeholder}")
            self._where_params.append(value)
        elif operator == 'gte':
            self._where_conditions.append(f"{field_name} >= {placeholder}")
            self._where_params.append(value)
        elif operator == 'lt':
            self._where_conditions.append(f"{field_name} < {placeholder}")
            self._where_params.append(value)
        elif operator == 'lte':
            self._where_conditions.append(f"{field_name} <= {placeholder}")
            self._where_params.append(value)
        elif operator == 'ne':
            self._where_conditions.append(f"{field_name} != {placeholder}")
            self._where_params.append(value)
        elif operator == 'in':
            placeholders = ', '.join([placeholder] * len(value))
            self._where_conditions.append(f"{field_name} IN ({placeholders})")
            self._where_params.extend(value)
        elif operator == 'contains':
            self._where_conditions.append(f"{field_name} LIKE {placeholder}")
            self._where_params.append(f"%{value}%")
        elif operator == 'startswith':
            self._where_conditions.append(f"{field_name} LIKE {placeholder}")
            self._where_params.append(f"{value}%")
        elif operator == 'endswith':
            self._where_conditions.append(f"{field_name} LIKE {placeholder}")
            self._where_params.append(f"%{value}")
        elif operator == 'isnull':
            if value:
                self._where_conditions.append(f"{field_name} IS NULL")
            else:
                self._where_conditions.append(f"{field_name} IS NOT NULL")

    def _process_q_object(self, q: Q):
        """Process Q object"""
        if q.conditions:
            for key, value in q.conditions.items():
                self._add_condition(key, value)

    def order_by(self, *fields: str) -> 'QueryBuilder':
        """Add ORDER BY clause"""
        for field in fields:
            if field.startswith('-'):
                self._order_by.append(f"{field[1:]} DESC")
            else:
                self._order_by.append(f"{field} ASC")
        return self

    def limit(self, value: int) -> 'QueryBuilder':
        """Add LIMIT clause"""
        self._limit_value = value
        return self

    def offset(self, value: int) -> 'QueryBuilder':
        """Add OFFSET clause"""
        self._offset_value = value
        return self

    def join(self, model: 'Model', on: str, join_type: JoinType = JoinType.INNER) -> 'QueryBuilder':
        """Add JOIN clause"""
        self._joins.append({
            'model': model,
            'on': on,
            'type': join_type
        })
        return self

    def group_by(self, *fields: str) -> 'QueryBuilder':
        """Add GROUP BY clause"""
        self._group_by.extend(fields)
        return self

    def build_select(self) -> tuple:
        """Build SELECT query"""
        table_name = self.model._meta.table_name
        
        # SELECT clause
        if self._select_fields:
            select_clause = f"SELECT {', '.join(self._select_fields)}"
        else:
            select_clause = f"SELECT * FROM {table_name}"

        # JOIN clauses
        join_clause = ""
        if self._joins:
            join_parts = []
            for join in self._joins:
                join_type = join['type'].value
                join_table = join['model']._meta.table_name
                join_parts.append(f"{join_type} {join_table} ON {join['on']}")
            join_clause = " " + " ".join(join_parts)

        # WHERE clause
        where_clause = ""
        if self._where_conditions:
            where_clause = " WHERE " + " AND ".join(self._where_conditions)

        # GROUP BY clause
        group_by_clause = ""
        if self._group_by:
            group_by_clause = " GROUP BY " + ", ".join(self._group_by)

        # ORDER BY clause
        order_by_clause = ""
        if self._order_by:
            order_by_clause = " ORDER BY " + ", ".join(self._order_by)

        # LIMIT/OFFSET clause
        limit_clause = ""
        if self._limit_value is not None:
            limit_clause = f" LIMIT {self._limit_value}"
        if self._offset_value is not None:
            limit_clause += f" OFFSET {self._offset_value}"

        query = f"{select_clause}{join_clause}{where_clause}{group_by_clause}{order_by_clause}{limit_clause}"
        return query, tuple(self._where_params)

    async def execute(self) -> List['Model']:
        """Execute query and return results"""
        query, params = self.build_select()
        rows = await self.model._meta.database.fetch_all(query, params)
        return [self.model._from_db(row) for row in rows]

    async def first(self) -> Optional['Model']:
        """Get first result"""
        self.limit(1)
        results = await self.execute()
        return results[0] if results else None

    async def count(self) -> int:
        """Count results"""
        table_name = self.model._meta.table_name
        where_clause = ""
        if self._where_conditions:
            where_clause = " WHERE " + " AND ".join(self._where_conditions)
        
        query = f"SELECT COUNT(*) as count FROM {table_name}{where_clause}"
        result = await self.model._meta.database.fetch_one(query, tuple(self._where_params))
        return result['count'] if result else 0

    async def exists(self) -> bool:
        """Check if any results exist"""
        return await self.count() > 0

    async def delete(self) -> int:
        """Delete matching records"""
        table_name = self.model._meta.table_name
        where_clause = ""
        if self._where_conditions:
            where_clause = " WHERE " + " AND ".join(self._where_conditions)
        
        query = f"DELETE FROM {table_name}{where_clause}"
        await self.model._meta.database.execute(query, tuple(self._where_params))
        return await self.count()

    async def update(self, **kwargs) -> int:
        """Update matching records"""
        if not kwargs:
            return 0

        table_name = self.model._meta.table_name
        placeholder = self.model._meta.database.get_placeholder()
        
        set_parts = []
        params = []
        for key, value in kwargs.items():
            set_parts.append(f"{key} = {placeholder}")
            params.append(value)
        
        params.extend(self._where_params)
        
        set_clause = ", ".join(set_parts)
        where_clause = ""
        if self._where_conditions:
            where_clause = " WHERE " + " AND ".join(self._where_conditions)
        
        query = f"UPDATE {table_name} SET {set_clause}{where_clause}"
        await self.model._meta.database.execute(query, tuple(params))
        return await self.count()