"""Typesafe model support for Akron using Pydantic."""
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, Optional, get_origin, get_args
import sys

SQL_TYPE_MAP = {
    int: "int",
    str: "str",
    float: "float",
    bool: "bool"
}

def get_base_type(py_type):
    """Extract base type from Optional[Type] or Union types."""
    # Handle Python 3.7+ typing
    origin = get_origin(py_type)
    if origin is not None:
        # Check if it's a Union type (which Optional creates)
        if str(origin) == 'typing.Union' or origin.__name__ == 'UnionType':
            args = get_args(py_type)
            # Return first non-None type
            for arg in args:
                if arg is not type(None):
                    return arg
    return py_type

def model_to_schema(model_cls: Type[BaseModel]) -> Dict[str, str]:
    """Convert Pydantic model to Akron schema with Django-like foreign key support."""
    schema = {}
    
    # Get foreign keys from class attribute if it exists
    foreign_keys = getattr(model_cls, '__foreign_keys__', {})
    
    for name, field in model_cls.model_fields.items():
        py_type = get_base_type(field.annotation)
        sql_type = SQL_TYPE_MAP.get(py_type, "str")
        
        # Check if this field has a foreign key constraint
        if name in foreign_keys:
            fk_reference = foreign_keys[name]
            schema[name] = f"{sql_type}->{fk_reference}"
        else:
            schema[name] = sql_type
    
    return schema

class ModelMixin:
    """Enhanced ModelMixin with Django-like foreign key support.
    
    Usage:
        class User(BaseModel, ModelMixin):
            id: Optional[int] = None
            name: str
            email: str
        
        class Post(BaseModel, ModelMixin):
            id: Optional[int] = None
            title: str
            content: str
            author_id: int
            category_id: Optional[int] = None
            
            # Django-like foreign key definitions
            __foreign_keys__ = {
                'author_id': 'users.id',
                'category_id': 'categories.id'
            }
    """
    
    @classmethod
    def create_table(cls, db):
        """Create table with foreign key constraints if defined."""
        schema = model_to_schema(cls)
        db.create_table(cls.__name__.lower(), schema)

    @classmethod
    def insert(cls, db, obj):
        """Insert a model instance into the database."""
        data = obj.model_dump()
        # Remove None values for optional fields
        data = {k: v for k, v in data.items() if v is not None}
        return db.insert(cls.__name__.lower(), data)

    @classmethod
    def find(cls, db, filters=None):
        """Find records and return as model instances."""
        results = db.find(cls.__name__.lower(), filters)
        return [cls(**r) for r in results]

    @classmethod
    def find_all(cls, db):
        """Find all records and return as model instances."""
        results = db.find(cls.__name__.lower())
        return [cls(**r) for r in results]

    @classmethod
    def get_by_id(cls, db, record_id):
        """Get a single record by ID."""
        results = db.find(cls.__name__.lower(), {"id": record_id})
        return cls(**results[0]) if results else None

    @classmethod
    def update(cls, db, filters, new_values):
        """Update records matching filters."""
        return db.update(cls.__name__.lower(), filters, new_values)

    @classmethod
    def delete(cls, db, filters):
        """Delete records matching filters."""
        return db.delete(cls.__name__.lower(), filters)

    @classmethod
    def count(cls, db, filters=None):
        """Count records matching filters."""
        return db.count(cls.__name__.lower(), filters)

    @classmethod
    def exists(cls, db, filters):
        """Check if any records exist matching filters."""
        return db.exists(cls.__name__.lower(), filters)
