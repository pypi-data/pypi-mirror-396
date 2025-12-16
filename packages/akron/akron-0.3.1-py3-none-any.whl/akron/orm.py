
"""User-facing entry point for Akron."""

from contextlib import contextmanager
from typing import Dict, Optional, Any, List, Union
from .core.sqlite_driver import SQLiteDriver
from .core.base import QueryBuilder
from .exceptions import UnsupportedDriverError, AkronError


class Record:
    """Wrapper class for database records that allows dot notation access."""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
    
    def __getattr__(self, key: str) -> Any:
        """Allow attribute access like user.name"""
        if key.startswith('_'):
            return object.__getattribute__(self, key)
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(f"Record has no attribute '{key}'")
    
    def __setattr__(self, key: str, value: Any) -> None:
        """Allow setting attributes like user.name = 'Alice'"""
        if key.startswith('_'):
            object.__setattr__(self, key, value)
        else:
            self._data[key] = value
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access like user['name']"""
        return self._data[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-style setting like user['name'] = 'Alice'"""
        self._data[key] = value
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator"""
        return key in self._data
    
    def __repr__(self) -> str:
        return f"Record({self._data})"
    
    def __str__(self) -> str:
        return str(self._data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Record back to a plain dictionary."""
        return self._data.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value with a default like dict.get()"""
        return self._data.get(key, default)
    
    def keys(self):
        """Return dictionary keys."""
        return self._data.keys()
    
    def values(self):
        """Return dictionary values."""
        return self._data.values()
    
    def items(self):
        """Return dictionary items."""
        return self._data.items()


class Akron:
    """
    Universal Python ORM with simple, intuitive syntax.
    
    Examples:
        # Basic CRUD
        db = Akron("sqlite:///app.db")
        db.create_table("users", {"id": "int", "name": "str", "email": "str"})
        
        user_id = db.insert("users", {"name": "Alice", "email": "alice@example.com"})
        users = db.find("users", {"name": "Alice"})
        db.update("users", {"id": user_id}, {"email": "alice.new@example.com"})
        db.delete("users", {"id": user_id})
        
        # Advanced queries
        users = db.query("users").where(age__gt=18).order_by("-created_at").limit(10).all()
        count = db.count("users", {"active": True})
        
        # Aggregations
        stats = db.aggregate("orders", {"total": "sum", "count": "count"}, group_by=["user_id"])
        
        # Transactions
        with db.transaction():
            db.insert("users", {"name": "Bob", "email": "bob@example.com"})
            db.insert("orders", {"user_id": 1, "amount": 100})
        
        # Bulk operations
        db.bulk_insert("users", [{"name": "User1"}, {"name": "User2"}])
        
        # Raw SQL
        results = db.raw("SELECT * FROM users WHERE age > ?", (18,))
    """

    def __init__(self, db_url: str = "sqlite:///akron.db"):
        self.db_url = db_url
        self.driver = self._choose_driver(db_url)
        self._in_transaction = False

    def _choose_driver(self, url: str):
        url = url.strip()
        if url.startswith("sqlite://"):
            return SQLiteDriver(url)
        elif url.startswith("mysql://"):
            from .core.mysql_driver import MySQLDriver
            return MySQLDriver(url)
        elif url.startswith(("postgres://", "postgresql://")):
            from .core.postgres_driver import PostgresDriver
            return PostgresDriver(url)
        elif url.startswith("mongodb://"):
            from .core.mongo_driver import MongoDriver
            return MongoDriver(url)
        raise UnsupportedDriverError(f"No driver for URL: {url}")

    # ===== BASIC CRUD OPERATIONS =====
    
    def create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        """Create a table with the given schema."""
        return self.driver.create_table(table_name, schema)

    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        """Insert a single record and return the ID."""
        return self.driver.insert(table_name, data)
        
    def bulk_insert(self, table_name: str, data_list: List[Dict[str, Any]]) -> List[int]:
        """Insert multiple records efficiently."""
        return self.driver.bulk_insert(table_name, data_list)

    def find(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Record]:
        """Find records with simple filters. Returns list of Record objects."""
        results = self.driver.find(table_name, filters)
        return [Record(record) for record in results]
        
    def find_one(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> Optional[Record]:
        """Find a single record. Returns a Record object or None."""
        results = self.driver.find(table_name, filters)
        return Record(results[0]) if results else None

    def update(self, table_name: str, filters: Dict[str, Any], new_values: Dict[str, Any]) -> int:
        """Update records matching filters."""
        return self.driver.update(table_name, filters, new_values)
        
    def bulk_update(self, table_name: str, updates: List[Dict[str, Any]]) -> int:
        """Bulk update records. Each dict should include 'filters' and 'values' keys."""
        return self.driver.bulk_update(table_name, updates)

    def delete(self, table_name: str, filters: Dict[str, Any]) -> int:
        """Delete records matching filters."""
        return self.driver.delete(table_name, filters)
        
    def count(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records matching filters."""
        return self.driver.count(table_name, filters)

    # ===== ADVANCED QUERYING =====
    
    def query(self, table_name: str) -> 'QueryBuilder':
        """Start building an advanced query."""
        builder = QueryBuilder()
        builder._driver = self.driver
        builder._table_name = table_name
        
        # Add convenience methods to builder
        def all():
            return self.driver.query(table_name, builder)
        
        def first():
            builder.limit(1)
            results = self.driver.query(table_name, builder)
            return results[0] if results else None
            
        def count():
            # For count, we need to modify the query
            original_select = builder.select_fields
            builder.select_fields = ['COUNT(*) as count']
            results = self.driver.query(table_name, builder)
            builder.select_fields = original_select  # restore
            return results[0]['count'] if results else 0
            
        builder.all = all
        builder.first = first
        builder.count = count
        return builder

    def aggregate(self, table_name: str, aggregations: Dict[str, str], 
                  filters: Optional[Dict[str, Any]] = None, 
                  group_by: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Perform aggregations.
        
        Examples:
            # Count and sum by group
            db.aggregate("orders", {"total": "sum", "count": "count"}, group_by=["user_id"])
            
            # Average age of active users
            db.aggregate("users", {"avg_age": "avg"}, filters={"active": True})
        """
        return self.driver.aggregate(table_name, aggregations, filters, group_by)

    # ===== RAW SQL =====
    
    def raw(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute raw SQL query."""
        return self.driver.raw_sql(sql, params)

    # ===== TRANSACTIONS =====
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        
        Usage:
            with db.transaction():
                db.insert("users", {"name": "Alice"})
                db.insert("posts", {"title": "Hello World", "user_id": 1})
        """
        if self._in_transaction:
            # Nested transactions - just pass through
            yield self
            return
            
        self._in_transaction = True
        self.driver.begin_transaction()
        try:
            yield self
            self.driver.commit_transaction()
        except Exception:
            self.driver.rollback_transaction()
            raise
        finally:
            self._in_transaction = False

    def begin_transaction(self) -> None:
        """Begin a transaction manually."""
        self._in_transaction = True
        return self.driver.begin_transaction()
        
    def commit(self) -> None:
        """Commit the current transaction."""
        self._in_transaction = False
        return self.driver.commit_transaction()
        
    def rollback(self) -> None:
        """Rollback the current transaction."""
        self._in_transaction = False
        return self.driver.rollback_transaction()

    # ===== INDEXES =====
    
    def create_index(self, table_name: str, columns: Union[str, List[str]], 
                     unique: bool = False, name: Optional[str] = None) -> None:
        """
        Create an index on table columns.
        
        Examples:
            db.create_index("users", "email", unique=True)
            db.create_index("posts", ["user_id", "created_at"])
        """
        if isinstance(columns, str):
            columns = [columns]
        return self.driver.create_index(table_name, columns, unique)
        
    def drop_index(self, index_name: str) -> None:
        """Drop an index."""
        return self.driver.drop_index(index_name)

    # ===== SERIALIZATION =====
    
    def to_dict(self, records: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Convert records to plain dictionaries (already are, but for consistency)."""
        return records
        
    def to_json(self, records: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
        """Convert records to JSON string."""
        import json
        return json.dumps(records, default=str)

    # ===== CONVENIENCE METHODS =====
    
    def exists(self, table_name: str, filters: Dict[str, Any]) -> bool:
        """Check if any record exists matching filters."""
        return self.count(table_name, filters) > 0
        
    def get_or_create(self, table_name: str, filters: Dict[str, Any], 
                      defaults: Optional[Dict[str, Any]] = None) -> tuple[Dict[str, Any], bool]:
        """
        Get existing record or create new one.
        Returns (record, created) tuple.
        """
        record = self.find_one(table_name, filters)
        if record:
            return record, False
        
        # Create new record
        create_data = {**filters}
        if defaults:
            create_data.update(defaults)
        
        record_id = self.insert(table_name, create_data)
        new_record = self.find_one(table_name, {"id": record_id})
        return new_record, True
        
    def upsert(self, table_name: str, filters: Dict[str, Any], values: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing record or insert new one."""
        if self.exists(table_name, filters):
            self.update(table_name, filters, values)
            return self.find_one(table_name, filters)
        else:
            create_data = {**filters, **values}
            record_id = self.insert(table_name, create_data)
            return self.find_one(table_name, {"id": record_id})

    def close(self):
        """Close database connection."""
        return self.driver.close()
