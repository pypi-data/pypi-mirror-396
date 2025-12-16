"""MongoDB driver for akron."""

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import Dict, Any, Optional, List
from .base import BaseDriver, QueryBuilder
from ..exceptions import AkronError

class MongoDriver(BaseDriver):
    def __init__(self, db_url: str):
        """db_url format: mongodb://host:port/dbname"""
        # Example: mongodb://localhost:27017/akron_test
        import re
        pattern = r"mongodb://(.*?):(\d+)/(.*?)$"
        match = re.match(pattern, db_url)
        if not match:
            raise AkronError("Invalid MongoDB URL format")
        host, port, database = match.groups()
        self.client = MongoClient(host, int(port))
        self.db = self.client[database]

    def create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        # MongoDB is schemaless; just create collection if not exists
        self.db.create_collection(table_name)

    def insert(self, table_name: str, data: Dict[str, Any]) -> Any:
        result = self.db[table_name].insert_one(data)
        return result.inserted_id

    def find(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if filters is None:
            filters = {}
        return list(self.db[table_name].find(filters))

    def update(self, table_name: str, filters: Dict[str, Any], new_values: Dict[str, Any]) -> int:
        result = self.db[table_name].update_many(filters, {"$set": new_values})
        return result.modified_count

    def delete(self, table_name: str, filters: Dict[str, Any]) -> int:
        if not filters or not isinstance(filters, dict):
            raise AkronError("filters must be a non-empty dict for delete")
        try:
            result = self.db[table_name].delete_many(filters)
            return result.deleted_count
        except PyMongoError as e:
            raise AkronError(f"Delete failed: {str(e)}")

    def bulk_insert(self, table_name: str, data_list: List[Dict[str, Any]]) -> List[Any]:
        """Insert multiple documents efficiently."""
        if not data_list or not isinstance(data_list, list):
            raise AkronError("data_list must be a non-empty list")
        
        try:
            result = self.db[table_name].insert_many(data_list)
            return result.inserted_ids
        except PyMongoError as e:
            raise AkronError(f"Bulk insert failed: {str(e)}")

    def query(self, table_name: str, builder: QueryBuilder) -> List[Dict[str, Any]]:
        """Execute advanced query with QueryBuilder."""
        filters = {}
        
        # Build MongoDB query from filters
        if builder.filters:
            for key, value in builder.filters.items():
                if "__" in key:
                    field, operator = key.split("__", 1)
                    
                    if operator == "gt":
                        filters[field] = {"$gt": value}
                    elif operator == "gte":
                        filters[field] = {"$gte": value}
                    elif operator == "lt":
                        filters[field] = {"$lt": value}
                    elif operator == "lte":
                        filters[field] = {"$lte": value}
                    elif operator == "ne":
                        filters[field] = {"$ne": value}
                    elif operator == "in":
                        filters[field] = {"$in": value}
                    elif operator == "like":
                        # MongoDB uses regex for LIKE
                        filters[field] = {"$regex": value}
                    elif operator == "isnull":
                        if value:
                            filters[field] = None
                        else:
                            filters[field] = {"$ne": None}
                    else:
                        raise AkronError(f"Unknown operator: {operator}")
                else:
                    filters[key] = value
        
        try:
            cursor = self.db[table_name].find(filters)
            
            # Apply sorting
            if builder.sorts:
                sort_list = []
                for field, direction in builder.sorts:
                    sort_list.append((field, 1 if direction == "ASC" else -1))
                cursor = cursor.sort(sort_list)
            
            # Apply limit and offset
            if builder.offset_count > 0:
                cursor = cursor.skip(builder.offset_count)
            if builder.limit_count is not None:
                cursor = cursor.limit(builder.limit_count)
            
            return list(cursor)
        except PyMongoError as e:
            raise AkronError(f"Query failed: {str(e)}")

    def bulk_update(self, table_name: str, updates: List[Dict[str, Any]]) -> int:
        """Bulk update documents."""
        if not updates or not isinstance(updates, list):
            raise AkronError("updates must be a non-empty list")
        
        total_updated = 0
        try:
            for update in updates:
                if not isinstance(update, dict) or "filters" not in update or "values" not in update:
                    raise AkronError("Each update must be a dict with 'filters' and 'values' keys")
                
                count = self.update(table_name, update["filters"], update["values"])
                total_updated += count
        except PyMongoError as e:
            raise AkronError(f"Bulk update failed: {str(e)}")
        
        return total_updated

    def count(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching filters."""
        if filters is None:
            filters = {}
        try:
            return self.db[table_name].count_documents(filters)
        except PyMongoError as e:
            raise AkronError(f"Count failed: {str(e)}")

    def aggregate(self, table_name: str, aggregations: Dict[str, str], 
                  filters: Optional[Dict[str, Any]] = None, 
                  group_by: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Perform aggregations using MongoDB aggregation pipeline."""
        pipeline = []
        
        # Add match stage for filters
        if filters:
            pipeline.append({"$match": filters})
        
        # Add group stage
        if group_by:
            group_stage = {"_id": {}}
            for field in group_by:
                group_stage["_id"][field] = f"${field}"
            
            for alias, func_spec in aggregations.items():
                if func_spec.lower() == "count":
                    group_stage[alias] = {"$sum": 1}
                elif func_spec.lower() == "sum":
                    group_stage[alias] = {"$sum": f"${alias}"}
                elif func_spec.lower() == "avg":
                    group_stage[alias] = {"$avg": f"${alias}"}
                elif func_spec.lower() == "min":
                    group_stage[alias] = {"$min": f"${alias}"}
                elif func_spec.lower() == "max":
                    group_stage[alias] = {"$max": f"${alias}"}
            
            pipeline.append({"$group": group_stage})
        else:
            # Simple aggregation without grouping
            group_stage = {"_id": None}
            for alias, func_spec in aggregations.items():
                if func_spec.lower() == "count":
                    group_stage[alias] = {"$sum": 1}
                elif func_spec.lower() == "sum":
                    group_stage[alias] = {"$sum": f"${alias}"}
                elif func_spec.lower() == "avg":
                    group_stage[alias] = {"$avg": f"${alias}"}
                elif func_spec.lower() == "min":
                    group_stage[alias] = {"$min": f"${alias}"}
                elif func_spec.lower() == "max":
                    group_stage[alias] = {"$max": f"${alias}"}
            
            pipeline.append({"$group": group_stage})
        
        try:
            return list(self.db[table_name].aggregate(pipeline))
        except PyMongoError as e:
            raise AkronError(f"Aggregation failed: {str(e)}")

    def raw_sql(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """MongoDB doesn't support SQL. Raise an error."""
        raise AkronError("MongoDB does not support raw SQL queries. Use find() or query() methods instead.")

    def begin_transaction(self) -> None:
        """Begin a transaction."""
        # MongoDB transactions require replica sets
        # For now, this is a no-op for compatibility
        pass

    def commit_transaction(self) -> None:
        """Commit the current transaction."""
        # No-op for MongoDB without transaction support
        pass

    def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        # No-op for MongoDB without transaction support
        pass

    def create_index(self, table_name: str, columns: List[str], unique: bool = False) -> None:
        """Create an index on the specified columns."""
        try:
            index_fields = [(col, 1) for col in columns]  # 1 for ascending
            self.db[table_name].create_index(index_fields, unique=unique)
        except PyMongoError as e:
            raise AkronError(f"Failed to create index: {str(e)}")

    def drop_index(self, index_name: str) -> None:
        """Drop an index."""
        raise AkronError("MongoDB index dropping requires collection name. Use MongoDB client directly.")

    def close(self):
        """Close database connection."""
        try:
            if self.client:
                self.client.close()
        except Exception:
            pass
