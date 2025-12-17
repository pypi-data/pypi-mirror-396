"""Database migration system"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .database import Database
from .models import Model
from .exceptions import MigrationError


class Migration:
    """Single migration"""

    def __init__(self, name: str, operations: List[Dict[str, Any]]):
        self.name = name
        self.operations = operations
        self.applied_at = None

    async def apply(self, database: Database):
        """Apply migration"""
        for operation in self.operations:
            await self._execute_operation(database, operation)

    async def _execute_operation(self, database: Database, operation: Dict[str, Any]):
        """Execute single operation"""
        op_type = operation.get('type')
        
        if op_type == 'create_table':
            await self._create_table(database, operation)
        elif op_type == 'drop_table':
            await self._drop_table(database, operation)
        elif op_type == 'add_column':
            await self._add_column(database, operation)
        elif op_type == 'drop_column':
            await self._drop_column(database, operation)
        elif op_type == 'raw_sql':
            await database.execute(operation['sql'])

    async def _create_table(self, database: Database, operation: Dict[str, Any]):
        """Create table operation"""
        model = operation['model']
        await model.create_table()

    async def _drop_table(self, database: Database, operation: Dict[str, Any]):
        """Drop table operation"""
        table_name = operation['table_name']
        await database.execute(f"DROP TABLE IF EXISTS {table_name}")

    async def _add_column(self, database: Database, operation: Dict[str, Any]):
        """Add column operation"""
        table_name = operation['table_name']
        column_name = operation['column_name']
        column_type = operation['column_type']
        
        query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        await database.execute(query)

    async def _drop_column(self, database: Database, operation: Dict[str, Any]):
        """Drop column operation"""
        table_name = operation['table_name']
        column_name = operation['column_name']
        
        # SQLite doesn't support DROP COLUMN directly
        database_type = database.__class__.__name__
        if 'Sqlite' in database_type:
            raise MigrationError("SQLite doesn't support DROP COLUMN. Use raw SQL with table recreation.")
        
        query = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
        await database.execute(query)


class MigrationManager:
    """Migration manager"""

    def __init__(self, database: Database, migrations_dir: str = "migrations"):
        self.database = database
        self.migrations_dir = Path(migrations_dir)
        self.migrations_dir.mkdir(exist_ok=True)
        self._migrations: List[Migration] = []

    async def init(self):
        """Initialize migration system"""
        await self._create_migrations_table()

    async def _create_migrations_table(self):
        """Create migrations tracking table"""
        query = """
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) UNIQUE NOT NULL,
            applied_at DATETIME NOT NULL
        )
        """
        await self.database.execute(query)

    def create_migration(self, name: str, operations: List[Dict[str, Any]]) -> Migration:
        """Create a new migration"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        migration_name = f"{timestamp}_{name}"
        
        migration = Migration(migration_name, operations)
        
        # Save to file
        migration_file = self.migrations_dir / f"{migration_name}.json"
        with open(migration_file, 'w') as f:
            json.dump({
                'name': migration_name,
                'operations': operations
            }, f, indent=2)
        
        return migration

    def load_migrations(self) -> List[Migration]:
        """Load all migrations from directory"""
        migrations = []
        
        for file_path in sorted(self.migrations_dir.glob("*.json")):
            with open(file_path, 'r') as f:
                data = json.load(f)
                migration = Migration(data['name'], data['operations'])
                migrations.append(migration)
        
        return migrations

    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations"""
        rows = await self.database.fetch_all("SELECT name FROM migrations ORDER BY applied_at")
        return [row['name'] for row in rows]

    async def migrate(self):
        """Apply pending migrations"""
        all_migrations = self.load_migrations()
        applied = await self.get_applied_migrations()
        
        pending = [m for m in all_migrations if m.name not in applied]
        
        for migration in pending:
            print(f"Applying migration: {migration.name}")
            await migration.apply(self.database)
            
            # Record migration
            placeholder = self.database.get_placeholder()
            await self.database.execute(
                f"INSERT INTO migrations (name, applied_at) VALUES ({placeholder}, {placeholder})",
                (migration.name, datetime.now().isoformat())
            )
            print(f"✓ Applied: {migration.name}")

    async def rollback(self, steps: int = 1):
        """Rollback migrations"""
        applied = await self.get_applied_migrations()
        
        if not applied:
            print("No migrations to rollback")
            return
        
        to_rollback = applied[-steps:]
        
        for migration_name in reversed(to_rollback):
            print(f"Rolling back: {migration_name}")
            placeholder = self.database.get_placeholder()
            await self.database.execute(
                f"DELETE FROM migrations WHERE name = {placeholder}",
                (migration_name,)
            )
            print(f"✓ Rolled back: {migration_name}")

    def make_migrations(self, models: List[type]):
        """Auto-generate migrations from models"""
        operations = []
        
        for model in models:
            if not issubclass(model, Model):
                continue
            
            operations.append({
                'type': 'create_table',
                'model': model
            })
        
        if operations:
            migration = self.create_migration("auto_generated", operations)
            print(f"Created migration: {migration.name}")
            return migration
        else:
            print("No changes detected")
            return None