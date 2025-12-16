"""Akron Schema Management - Prisma-like schema handling for akron.json files."""
import json
import os
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .exceptions import SchemaError


@dataclass
class ColumnDefinition:
    """Represents a single column definition in a table."""
    type: str
    primary_key: bool = False
    auto_increment: bool = False
    unique: bool = False
    nullable: bool = True
    default: Optional[Any] = None
    foreign_key: Optional[Dict[str, str]] = None
    
    def to_akron_type(self) -> str:
        """Convert column definition to Akron's simple type format."""
        if self.foreign_key:
            ref_table = self.foreign_key["references"].split(".")[0]
            ref_column = self.foreign_key["references"].split(".")[1]
            return f"{self.type}->{ref_table}.{ref_column}"
        return self.type


@dataclass
class TableDefinition:
    """Represents a complete table definition."""
    name: str
    columns: Dict[str, ColumnDefinition]
    
    def to_akron_schema(self) -> Dict[str, str]:
        """Convert table definition to Akron's schema format."""
        schema = {}
        for col_name, col_def in self.columns.items():
            schema[col_name] = col_def.to_akron_type()
        return schema


@dataclass
class DatabaseConfig:
    """Database configuration from akron.json."""
    provider: str
    url: str


@dataclass
class AkronSchema:
    """Complete Akron schema representation."""
    database: DatabaseConfig
    tables: Dict[str, TableDefinition]
    
    @classmethod
    def from_file(cls, file_path: str = "akron.json") -> "AkronSchema":
        """Load schema from akron.json file."""
        if not os.path.exists(file_path):
            raise SchemaError(f"Schema file {file_path} not found")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise SchemaError(f"Invalid JSON in {file_path}: {e}")
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AkronSchema":
        """Create schema from dictionary representation."""
        # Parse database configuration
        db_config = DatabaseConfig(
            provider=data["database"]["provider"],
            url=data["database"]["url"]
        )
        
        # Parse tables
        tables = {}
        for table_name, table_data in data.get("tables", {}).items():
            columns = {}
            for col_name, col_data in table_data["columns"].items():
                # Handle foreign key references
                foreign_key = None
                if "foreignKey" in col_data:
                    foreign_key = {
                        "references": col_data["foreignKey"]["references"],
                        "onDelete": col_data["foreignKey"].get("onDelete", "RESTRICT")
                    }
                
                columns[col_name] = ColumnDefinition(
                    type=col_data["type"],
                    primary_key=col_data.get("primaryKey", False),
                    auto_increment=col_data.get("autoIncrement", False),
                    unique=col_data.get("unique", False),
                    nullable=col_data.get("nullable", True),
                    default=col_data.get("default"),
                    foreign_key=foreign_key
                )
            
            tables[table_name] = TableDefinition(name=table_name, columns=columns)
        
        return cls(database=db_config, tables=tables)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schema back to dictionary representation."""
        tables_dict = {}
        for table_name, table_def in self.tables.items():
            columns_dict = {}
            for col_name, col_def in table_def.columns.items():
                col_dict = {
                    "type": col_def.type,
                    "nullable": col_def.nullable
                }
                
                if col_def.primary_key:
                    col_dict["primaryKey"] = True
                if col_def.auto_increment:
                    col_dict["autoIncrement"] = True
                if col_def.unique:
                    col_dict["unique"] = True
                if col_def.default is not None:
                    col_dict["default"] = col_def.default
                if col_def.foreign_key:
                    col_dict["foreignKey"] = col_def.foreign_key
                
                columns_dict[col_name] = col_dict
            
            tables_dict[table_name] = {"columns": columns_dict}
        
        return {
            "database": {
                "provider": self.database.provider,
                "url": self.database.url
            },
            "tables": tables_dict
        }
    
    def save_to_file(self, file_path: str = "akron.json"):
        """Save schema to akron.json file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def get_checksum(self) -> str:
        """Generate a checksum for the current schema state."""
        schema_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(schema_str.encode()).hexdigest()


class SchemaManager:
    """Manages Akron schema operations."""
    
    def __init__(self, schema_file: str = "akron.json", snapshots_dir: str = ".akron"):
        self.schema_file = schema_file
        self.snapshots_dir = snapshots_dir
        self.snapshots_file = os.path.join(snapshots_dir, "schema_snapshots.json")
        
        # Create snapshots directory if it doesn't exist
        os.makedirs(snapshots_dir, exist_ok=True)
    
    def load_schema(self) -> AkronSchema:
        """Load the current schema from akron.json."""
        return AkronSchema.from_file(self.schema_file)
    
    def save_snapshot(self, schema: AkronSchema, description: str = ""):
        """Save a snapshot of the current schema."""
        snapshots = self._load_snapshots()
        
        snapshot = {
            "timestamp": self._get_timestamp(),
            "checksum": schema.get_checksum(),
            "schema": schema.to_dict(),
            "description": description
        }
        
        snapshots.append(snapshot)
        
        with open(self.snapshots_file, 'w') as f:
            json.dump(snapshots, f, indent=2)
    
    def _load_snapshots(self) -> List[Dict[str, Any]]:
        """Load existing snapshots."""
        if not os.path.exists(self.snapshots_file):
            return []
        
        with open(self.snapshots_file, 'r') as f:
            return json.load(f)
    
    def get_last_snapshot(self) -> Optional[AkronSchema]:
        """Get the last saved snapshot."""
        snapshots = self._load_snapshots()
        if not snapshots:
            return None
        
        last_snapshot = snapshots[-1]
        return AkronSchema.from_dict(last_snapshot["schema"])
    
    def has_schema_changed(self) -> bool:
        """Check if schema has changed since last snapshot."""
        try:
            current_schema = self.load_schema()
            last_snapshot = self.get_last_snapshot()
            
            if last_snapshot is None:
                return True
            
            return current_schema.get_checksum() != last_snapshot.get_checksum()
        except (FileNotFoundError, SchemaError):
            return True
    
    def generate_migration_steps(self) -> List[Dict[str, Any]]:
        """Generate migration steps by comparing current schema with last snapshot."""
        current_schema = self.load_schema()
        last_snapshot = self.get_last_snapshot()
        
        if last_snapshot is None:
            # First migration - create all tables
            steps = []
            for table_name, table_def in current_schema.tables.items():
                steps.append({
                    "action": "create_table",
                    "table": table_name,
                    "schema": table_def.to_akron_schema()
                })
            return steps
        
        steps = []
        current_tables = current_schema.tables
        old_tables = last_snapshot.tables
        
        # Find new tables
        for table_name in current_tables:
            if table_name not in old_tables:
                steps.append({
                    "action": "create_table",
                    "table": table_name,
                    "schema": current_tables[table_name].to_akron_schema()
                })
        
        # Find dropped tables
        for table_name in old_tables:
            if table_name not in current_tables:
                steps.append({
                    "action": "drop_table",
                    "table": table_name
                })
        
        # Find modified tables
        for table_name in current_tables:
            if table_name in old_tables:
                current_table = current_tables[table_name]
                old_table = old_tables[table_name]
                
                # Compare columns
                current_columns = current_table.columns
                old_columns = old_table.columns
                
                # New columns
                for col_name in current_columns:
                    if col_name not in old_columns:
                        steps.append({
                            "action": "add_column",
                            "table": table_name,
                            "column": col_name,
                            "definition": current_columns[col_name].to_akron_type()
                        })
                
                # Dropped columns
                for col_name in old_columns:
                    if col_name not in current_columns:
                        steps.append({
                            "action": "drop_column",
                            "table": table_name,
                            "column": col_name
                        })
                
                # Modified columns
                for col_name in current_columns:
                    if col_name in old_columns:
                        current_col = current_columns[col_name]
                        old_col = old_columns[col_name]
                        
                        if current_col.to_akron_type() != old_col.to_akron_type():
                            steps.append({
                                "action": "modify_column",
                                "table": table_name,
                                "column": col_name,
                                "from": old_col.to_akron_type(),
                                "to": current_col.to_akron_type()
                            })
        
        return steps
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()


def create_default_schema(provider: str = "sqlite", database_url: str = "sqlite://app.db") -> Dict[str, Any]:
    """Create a default akron.json schema template."""
    return {
        "database": {
            "provider": provider,
            "url": database_url
        },
        "tables": {
            "User": {
                "columns": {
                    "id": {
                        "type": "int",
                        "primaryKey": True,
                        "autoIncrement": True
                    },
                    "email": {
                        "type": "string",
                        "unique": True,
                        "nullable": False
                    },
                    "name": {
                        "type": "string",
                        "nullable": True
                    },
                    "createdAt": {
                        "type": "datetime",
                        "default": "now"
                    }
                }
            }
        }
    }
