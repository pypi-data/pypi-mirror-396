"""Abstract base driver for akron drivers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union


class QueryBuilder:
    """Simple query builder for advanced filtering, sorting, and pagination."""
    
    def __init__(self):
        self.filters = {}
        self.sorts = []
        self.limit_count = None
        self.offset_count = 0
        self.joins = []
        self.select_fields = None
        self.group_by_fields = []
        self.having_conditions = {}
        
    def where(self, **conditions) -> 'QueryBuilder':
        """Add WHERE conditions. Supports: field=value, field__gt=value, field__lt=value, etc."""
        self.filters.update(conditions)
        return self
        
    def order_by(self, *fields) -> 'QueryBuilder':
        """Add ORDER BY fields. Use '-field' for DESC, 'field' for ASC."""
        for field in fields:
            if field.startswith('-'):
                self.sorts.append((field[1:], 'DESC'))
            else:
                self.sorts.append((field, 'ASC'))
        return self
        
    def limit(self, count: int) -> 'QueryBuilder':
        """Add LIMIT clause."""
        self.limit_count = count
        return self
        
    def offset(self, count: int) -> 'QueryBuilder':
        """Add OFFSET clause."""
        self.offset_count = count
        return self
        
    def paginate(self, page: int, per_page: int = 20) -> 'QueryBuilder':
        """Paginate results."""
        self.limit_count = per_page
        self.offset_count = (page - 1) * per_page
        return self
        
    def select(self, *fields) -> 'QueryBuilder':
        """Select specific fields."""
        self.select_fields = fields
        return self
        
    def join(self, table: str, on: str, join_type: str = 'INNER') -> 'QueryBuilder':
        """Add JOIN clause."""
        self.joins.append((table, on, join_type))
        return self
        
    def group_by(self, *fields) -> 'QueryBuilder':
        """Add GROUP BY clause."""
        self.group_by_fields.extend(fields)
        return self
        
    def having(self, **conditions) -> 'QueryBuilder':
        """Add HAVING conditions for aggregations."""
        self.having_conditions.update(conditions)
        return self


class BaseDriver(ABC):
    @abstractmethod
    def create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        raise NotImplementedError
        
    @abstractmethod
    def bulk_insert(self, table_name: str, data_list: List[Dict[str, Any]]) -> List[int]:
        raise NotImplementedError

    @abstractmethod
    def find(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError
        
    @abstractmethod
    def query(self, table_name: str, builder: QueryBuilder) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def update(self, table_name: str, filters: Dict[str, Any], new_values: Dict[str, Any]) -> int:
        raise NotImplementedError
        
    @abstractmethod
    def bulk_update(self, table_name: str, updates: List[Dict[str, Any]]) -> int:
        raise NotImplementedError

    @abstractmethod
    def delete(self, table_name: str, filters: Dict[str, Any]) -> int:
        raise NotImplementedError
        
    @abstractmethod
    def count(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> int:
        raise NotImplementedError
        
    @abstractmethod
    def aggregate(self, table_name: str, aggregations: Dict[str, str], 
                  filters: Optional[Dict[str, Any]] = None, 
                  group_by: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError
        
    @abstractmethod
    def raw_sql(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError
        
    @abstractmethod
    def begin_transaction(self) -> None:
        raise NotImplementedError
        
    @abstractmethod
    def commit_transaction(self) -> None:
        raise NotImplementedError
        
    @abstractmethod
    def rollback_transaction(self) -> None:
        raise NotImplementedError
        
    @abstractmethod
    def create_index(self, table_name: str, columns: List[str], unique: bool = False) -> None:
        raise NotImplementedError
        
    @abstractmethod
    def drop_index(self, index_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError
