"""SQLite driver for akron."""

import sqlite3
import json
from typing import Dict, Any, Optional, List, Tuple, Union
from .base import BaseDriver, QueryBuilder
from ..utils import map_type, sanitize_identifier
from ..exceptions import AkronError, TableNotFoundError


class SQLiteDriver(BaseDriver):
    def __init__(self, db_url: str):
        """db_url format: sqlite:///path/to/db or sqlite:///:memory:"""
        if not db_url.startswith("sqlite://"):
            raise AkronError("SQLiteDriver requires sqlite:// URL")
        # support sqlite:///file.db and sqlite:///:memory:
        path = db_url.replace("sqlite://", "")
        # when path empty -> default to akron.db
        if path in ("", "/"):
            path = "akron.db"
        # handle in-memory database for both ':memory:' and '/:memory:'
        if path in (":memory:", "/:memory:"):
            self._path = ":memory:"
            self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            self._path = path
            self.conn = sqlite3.connect(self._path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

    def _exec(self, sql: str, params: Tuple = ()):
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
        except sqlite3.OperationalError as e:
            # common: no such table
            msg = str(e).lower()
            if "no such table" in msg:
                raise TableNotFoundError(msg)
            raise AkronError(str(e))

    def create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        """
        Create a table with optional foreign keys.
        Foreign key syntax: 'type->table.column'
        Example: {"user_id": "int->users.id"}
        """
        if not schema or not isinstance(schema, dict):
            raise AkronError("schema must be a non-empty dict")

        tname = sanitize_identifier(table_name)
        cols = []
        fks = []
        for col, dtype in schema.items():
            cname = sanitize_identifier(col)
            # Check for FK syntax
            if isinstance(dtype, str) and "->" in dtype:
                base_type, fk = dtype.split("->", 1)
                sql_type = map_type(base_type.strip())
                ref_table, ref_col = fk.strip().split(".")
                ref_table = sanitize_identifier(ref_table)
                ref_col = sanitize_identifier(ref_col)
                cols.append(f"{cname} {sql_type}")
                fks.append(f"FOREIGN KEY({cname}) REFERENCES {ref_table}({ref_col})")
            else:
                sql_type = map_type(dtype)
                if cname == "id" and sql_type.upper() == "INTEGER":
                    cols.append(f"{cname} {sql_type} PRIMARY KEY AUTOINCREMENT")
                else:
                    cols.append(f"{cname} {sql_type}")
        cols_sql = ", ".join(cols + fks)
        sql = f"CREATE TABLE IF NOT EXISTS {tname} ({cols_sql})"
        self._exec(sql)

    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        if not data or not isinstance(data, dict):
            raise AkronError("data must be a non-empty dict")
        tname = sanitize_identifier(table_name)
        keys = [sanitize_identifier(k) for k in data.keys()]
        placeholders = ", ".join(["?"] * len(keys))
        cols_sql = ", ".join(keys)
        sql = f"INSERT INTO {tname} ({cols_sql}) VALUES ({placeholders})"
        params = tuple(data.values())
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            msg = str(e)
            if "UNIQUE constraint failed" in msg:
                raise AkronError(f"Duplicate entry on unique field: {msg}")
            if "FOREIGN KEY constraint failed" in msg:
                raise AkronError(f"Foreign key constraint failed: {msg}")
            raise AkronError(msg)
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if "no such table" in msg:
                raise TableNotFoundError(msg)
            raise AkronError(str(e))
        return self.cur.lastrowid

    def find(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        tname = sanitize_identifier(table_name)
        sql = f"SELECT * FROM {tname}"
        params: Tuple = ()
        if filters:
            if not isinstance(filters, dict):
                raise AkronError("filters must be a dict")
            conds = []
            for k in filters.keys():
                conds.append(f"{sanitize_identifier(k)} = ?")
            sql += " WHERE " + " AND ".join(conds)
            params = tuple(filters.values())

        try:
            self.cur.execute(sql, params)
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if "no such table" in msg:
                raise TableNotFoundError(msg)
            raise AkronError(str(e))

        columns = [d[0] for d in self.cur.description] if self.cur.description else []
        rows = self.cur.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def update(self, table_name: str, filters: Dict[str, Any], new_values: Dict[str, Any]) -> int:
        if not filters or not isinstance(filters, dict):
            raise AkronError("filters must be a non-empty dict for update")
        if not new_values or not isinstance(new_values, dict):
            raise AkronError("new_values must be a non-empty dict for update")
        tname = sanitize_identifier(table_name)
        set_clause = ", ".join(f"{sanitize_identifier(k)} = ?" for k in new_values.keys())
        where_clause = " AND ".join(f"{sanitize_identifier(k)} = ?" for k in filters.keys())
        sql = f"UPDATE {tname} SET {set_clause} WHERE {where_clause}"
        params = tuple(new_values.values()) + tuple(filters.values())
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if "no such table" in msg:
                raise TableNotFoundError(msg)
            raise AkronError(str(e))
        return self.cur.rowcount

    def delete(self, table_name: str, filters: Dict[str, Any]) -> int:
        if not filters or not isinstance(filters, dict):
            raise AkronError("filters must be a non-empty dict for delete")
        tname = sanitize_identifier(table_name)
        where_clause = " AND ".join(f"{sanitize_identifier(k)} = ?" for k in filters.keys())
        sql = f"DELETE FROM {tname} WHERE {where_clause}"
        params = tuple(filters.values())
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if "no such table" in msg:
                raise TableNotFoundError(msg)
            raise AkronError(str(e))
        return self.cur.rowcount

    def bulk_insert(self, table_name: str, data_list: List[Dict[str, Any]]) -> List[int]:
        """Insert multiple records efficiently."""
        if not data_list or not isinstance(data_list, list):
            raise AkronError("data_list must be a non-empty list")
        
        if not all(isinstance(item, dict) for item in data_list):
            raise AkronError("All items in data_list must be dictionaries")
        
        # Use the first record to determine columns
        first_record = data_list[0]
        tname = sanitize_identifier(table_name)
        keys = [sanitize_identifier(k) for k in first_record.keys()]
        placeholders = ", ".join(["?"] * len(keys))
        cols_sql = ", ".join(keys)
        sql = f"INSERT INTO {tname} ({cols_sql}) VALUES ({placeholders})"
        
        inserted_ids = []
        try:
            for data in data_list:
                # Ensure all records have the same keys
                if set(data.keys()) != set(first_record.keys()):
                    raise AkronError("All records must have the same keys for bulk insert")
                
                params = tuple(data[k] for k in first_record.keys())
                self.cur.execute(sql, params)
                inserted_ids.append(self.cur.lastrowid)
            
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            msg = str(e)
            if "UNIQUE constraint failed" in msg:
                raise AkronError(f"Duplicate entry on unique field: {msg}")
            if "FOREIGN KEY constraint failed" in msg:
                raise AkronError(f"Foreign key constraint failed: {msg}")
            raise AkronError(msg)
        except sqlite3.OperationalError as e:
            self.conn.rollback()
            msg = str(e).lower()
            if "no such table" in msg:
                raise TableNotFoundError(msg)
            raise AkronError(str(e))
        
        return inserted_ids

    def query(self, table_name: str, builder: QueryBuilder) -> List[Dict[str, Any]]:
        """Execute advanced query with QueryBuilder."""
        tname = sanitize_identifier(table_name)
        
        # Build SELECT clause
        if builder.select_fields:
            if isinstance(builder.select_fields, (list, tuple)):
                select_clause = ", ".join(sanitize_identifier(f) for f in builder.select_fields)
            else:
                # Handle aggregation functions like COUNT(*) as count
                select_clause = str(builder.select_fields[0])
        else:
            select_clause = "*"
        
        sql = f"SELECT {select_clause} FROM {tname}"
        params = []
        
        # Build JOIN clauses
        for join_table, on_condition, join_type in builder.joins:
            join_table_clean = sanitize_identifier(join_table)
            sql += f" {join_type} JOIN {join_table_clean} ON {on_condition}"
        
        # Build WHERE clause
        if builder.filters:
            conditions = []
            for key, value in builder.filters.items():
                if "__" in key:
                    # Handle advanced operators like field__gt, field__lt
                    field, operator = key.split("__", 1)
                    field = sanitize_identifier(field)
                    
                    if operator == "gt":
                        conditions.append(f"{field} > ?")
                    elif operator == "gte":
                        conditions.append(f"{field} >= ?")
                    elif operator == "lt":
                        conditions.append(f"{field} < ?")
                    elif operator == "lte":
                        conditions.append(f"{field} <= ?")
                    elif operator == "ne":
                        conditions.append(f"{field} != ?")
                    elif operator == "in":
                        if isinstance(value, (list, tuple)):
                            placeholders = ", ".join(["?"] * len(value))
                            conditions.append(f"{field} IN ({placeholders})")
                            params.extend(value)
                            continue  # Skip adding value to params again
                        else:
                            raise AkronError("Value for 'in' operator must be a list or tuple")
                    elif operator == "like":
                        conditions.append(f"{field} LIKE ?")
                    elif operator == "isnull":
                        if value:
                            conditions.append(f"{field} IS NULL")
                        else:
                            conditions.append(f"{field} IS NOT NULL")
                        continue  # Skip adding value to params
                    else:
                        raise AkronError(f"Unknown operator: {operator}")
                    
                    params.append(value)
                else:
                    # Simple equality
                    field = sanitize_identifier(key)
                    conditions.append(f"{field} = ?")
                    params.append(value)
            
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
        
        # Build GROUP BY clause
        if builder.group_by_fields:
            group_fields = ", ".join(sanitize_identifier(f) for f in builder.group_by_fields)
            sql += f" GROUP BY {group_fields}"
        
        # Build HAVING clause
        if builder.having_conditions:
            having_conditions = []
            for key, value in builder.having_conditions.items():
                having_conditions.append(f"{sanitize_identifier(key)} = ?")
                params.append(value)
            sql += " HAVING " + " AND ".join(having_conditions)
        
        # Build ORDER BY clause
        if builder.sorts:
            order_fields = []
            for field, direction in builder.sorts:
                field_clean = sanitize_identifier(field)
                order_fields.append(f"{field_clean} {direction}")
            sql += " ORDER BY " + ", ".join(order_fields)
        
        # Build LIMIT and OFFSET
        if builder.limit_count is not None:
            sql += f" LIMIT {builder.limit_count}"
            if builder.offset_count > 0:
                sql += f" OFFSET {builder.offset_count}"
        
        # Execute query
        try:
            self.cur.execute(sql, tuple(params))
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if "no such table" in msg:
                raise TableNotFoundError(msg)
            raise AkronError(str(e))
        
        columns = [d[0] for d in self.cur.description] if self.cur.description else []
        rows = self.cur.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def bulk_update(self, table_name: str, updates: List[Dict[str, Any]]) -> int:
        """Bulk update records. Each dict should have 'filters' and 'values' keys."""
        if not updates or not isinstance(updates, list):
            raise AkronError("updates must be a non-empty list")
        
        total_updated = 0
        try:
            for update in updates:
                if not isinstance(update, dict) or "filters" not in update or "values" not in update:
                    raise AkronError("Each update must be a dict with 'filters' and 'values' keys")
                
                count = self.update(table_name, update["filters"], update["values"])
                total_updated += count
            
        except Exception:
            self.conn.rollback()
            raise
        
        return total_updated

    def count(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records matching filters."""
        tname = sanitize_identifier(table_name)
        sql = f"SELECT COUNT(*) as count FROM {tname}"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{sanitize_identifier(key)} = ?")
                params.append(value)
            sql += " WHERE " + " AND ".join(conditions)
        
        try:
            self.cur.execute(sql, tuple(params))
            result = self.cur.fetchone()
            return result[0] if result else 0
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if "no such table" in msg:
                raise TableNotFoundError(msg)
            raise AkronError(str(e))

    def aggregate(self, table_name: str, aggregations: Dict[str, str], 
                  filters: Optional[Dict[str, Any]] = None, 
                  group_by: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Perform aggregations like sum, count, avg, min, max."""
        tname = sanitize_identifier(table_name)
        
        # Build SELECT clause with aggregations
        agg_fields = []
        for alias, func_spec in aggregations.items():
            if func_spec.lower() == "count":
                agg_fields.append(f"COUNT(*) as {alias}")
            else:
                # Handle functions like sum(column), avg(column)
                if "(" in func_spec:
                    # Already formatted like "sum(amount)"
                    agg_fields.append(f"{func_spec.upper()} as {alias}")
                else:
                    # Assume it's "sum" and we need to figure out the column
                    # For now, default to * for count, but this needs improvement
                    if func_spec.lower() in ["sum", "avg", "min", "max"]:
                        # This is a simplification - in real usage, column should be specified
                        agg_fields.append(f"{func_spec.upper()}(*) as {alias}")
                    else:
                        agg_fields.append(f"{func_spec} as {alias}")
        
        select_clause = ", ".join(agg_fields)
        sql = f"SELECT {select_clause} FROM {tname}"
        params = []
        
        # Add WHERE clause
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{sanitize_identifier(key)} = ?")
                params.append(value)
            sql += " WHERE " + " AND ".join(conditions)
        
        # Add GROUP BY clause
        if group_by:
            group_fields = ", ".join(sanitize_identifier(f) for f in group_by)
            sql += f" GROUP BY {group_fields}"
            # Add group by fields to select
            sql = f"SELECT {group_fields}, {select_clause} FROM {tname}"
            if filters:
                sql += " WHERE " + " AND ".join(conditions)
            sql += f" GROUP BY {group_fields}"
        
        try:
            self.cur.execute(sql, tuple(params))
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if "no such table" in msg:
                raise TableNotFoundError(msg)
            raise AkronError(str(e))
        
        columns = [d[0] for d in self.cur.description] if self.cur.description else []
        rows = self.cur.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def raw_sql(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute raw SQL query."""
        try:
            if params:
                self.cur.execute(sql, params)
            else:
                self.cur.execute(sql)
            
            # Check if it's a SELECT query
            if sql.strip().upper().startswith("SELECT"):
                columns = [d[0] for d in self.cur.description] if self.cur.description else []
                rows = self.cur.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            else:
                # For INSERT/UPDATE/DELETE, commit and return affected rows info
                self.conn.commit()
                return [{"affected_rows": self.cur.rowcount}]
        
        except sqlite3.Error as e:
            raise AkronError(f"SQL execution error: {str(e)}")

    def begin_transaction(self) -> None:
        """Begin a transaction."""
        self.cur.execute("BEGIN TRANSACTION")

    def commit_transaction(self) -> None:
        """Commit the current transaction."""
        self.conn.commit()

    def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        self.conn.rollback()

    def create_index(self, table_name: str, columns: List[str], unique: bool = False) -> None:
        """Create an index on the specified columns."""
        tname = sanitize_identifier(table_name)
        cols = [sanitize_identifier(col) for col in columns]
        cols_str = ", ".join(cols)
        
        # Generate index name
        index_name = f"idx_{table_name}_{'_'.join(columns)}"
        index_name = sanitize_identifier(index_name)
        
        unique_str = "UNIQUE " if unique else ""
        sql = f"CREATE {unique_str}INDEX IF NOT EXISTS {index_name} ON {tname} ({cols_str})"
        
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except sqlite3.OperationalError as e:
            raise AkronError(f"Failed to create index: {str(e)}")

    def drop_index(self, index_name: str) -> None:
        """Drop an index."""
        index_name = sanitize_identifier(index_name)
        sql = f"DROP INDEX IF EXISTS {index_name}"
        
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except sqlite3.OperationalError as e:
            raise AkronError(f"Failed to drop index: {str(e)}")

    def close(self):
        try:
            self.cur.close()
        except Exception:
            pass
        try:
            self.conn.close()
        except Exception:
            pass
