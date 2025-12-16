"""PostgreSQL driver for akron."""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, Optional, List, Tuple
from .base import BaseDriver, QueryBuilder
from ..exceptions import AkronError, TableNotFoundError

class PostgresDriver(BaseDriver):
    def __init__(self, db_url: str):
        """db_url format: postgres://user:password@host:port/dbname or postgresql://..."""
        import re
        # Support both postgres:// and postgresql://
        pattern = r"postgres(?:ql)?://(.*?):(.*?)@(.*?):(.*?)/(.*?)$"
        match = re.match(pattern, db_url)
        if not match:
            raise AkronError("Invalid Postgres URL format. Expected: postgres://user:password@host:port/dbname")
        user, password, host, port, database = match.groups()
        try:
            self.conn = psycopg2.connect(
                user=user,
                password=password,
                host=host,
                port=int(port),
                dbname=database
            )
            self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        except psycopg2.Error as e:
            raise AkronError(f"Failed to connect to PostgreSQL: {str(e)}")

    def create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        cols = []
        fks = []
        for col, dtype in schema.items():
            # Foreign key syntax: 'type->table.column'
            if isinstance(dtype, str) and "->" in dtype:
                base_type, fk = dtype.split("->", 1)
                sql_type = "INTEGER" if base_type.strip() == "int" else "VARCHAR(255)" if base_type.strip() == "str" else base_type.strip().upper()
                ref_table, ref_col = fk.strip().split(".")
                cols.append(f"{col} {sql_type}")
                fks.append(f"FOREIGN KEY({col}) REFERENCES {ref_table}({ref_col})")
            else:
                sql_type = "INTEGER" if dtype == "int" else "VARCHAR(255)" if dtype == "str" else dtype.upper()
                if col == "id" and sql_type == "INTEGER":
                    cols.append(f"{col} {sql_type} PRIMARY KEY GENERATED ALWAYS AS IDENTITY")
                else:
                    cols.append(f"{col} {sql_type}")
        cols_sql = ", ".join(cols + fks)
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({cols_sql})"
        self.cur.execute(sql)
        self.conn.commit()

    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        keys = list(data.keys())
        placeholders = ", ".join(["%s"] * len(keys))
        cols_sql = ", ".join(keys)
        sql = f"INSERT INTO {table_name} ({cols_sql}) VALUES ({placeholders}) RETURNING id"
        params = tuple(data.values())
        self.cur.execute(sql, params)
        self.conn.commit()
        return self.cur.fetchone()["id"]

    def find(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        sql = f"SELECT * FROM {table_name}"
        params = ()
        if filters:
            conds = [f"{k} = %s" for k in filters.keys()]
            sql += " WHERE " + " AND ".join(conds)
            params = tuple(filters.values())
        self.cur.execute(sql, params)
        return self.cur.fetchall()

    def update(self, table_name: str, filters: Dict[str, Any], new_values: Dict[str, Any]) -> int:
        set_clause = ", ".join(f"{k} = %s" for k in new_values.keys())
        where_clause = " AND ".join(f"{k} = %s" for k in filters.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        params = tuple(new_values.values()) + tuple(filters.values())
        self.cur.execute(sql, params)
        self.conn.commit()
        return self.cur.rowcount

    def delete(self, table_name: str, filters: Dict[str, Any]) -> int:
        if not filters or not isinstance(filters, dict):
            raise AkronError("filters must be a non-empty dict for delete")
        where_clause = " AND ".join(f"{k} = %s" for k in filters.keys())
        sql = f"DELETE FROM {table_name} WHERE {where_clause}"
        params = tuple(filters.values())
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
            return self.cur.rowcount
        except psycopg2.Error as e:
            self.conn.rollback()
            raise AkronError(f"Delete failed: {str(e)}")

    def bulk_insert(self, table_name: str, data_list: List[Dict[str, Any]]) -> List[int]:
        """Insert multiple records efficiently."""
        if not data_list or not isinstance(data_list, list):
            raise AkronError("data_list must be a non-empty list")
        
        if not all(isinstance(item, dict) for item in data_list):
            raise AkronError("All items in data_list must be dictionaries")
        
        first_record = data_list[0]
        keys = list(first_record.keys())
        placeholders = ", ".join(["%s"] * len(keys))
        cols_sql = ", ".join(keys)
        sql = f"INSERT INTO {table_name} ({cols_sql}) VALUES ({placeholders}) RETURNING id"
        
        inserted_ids = []
        try:
            for data in data_list:
                if set(data.keys()) != set(first_record.keys()):
                    raise AkronError("All records must have the same keys for bulk insert")
                
                params = tuple(data[k] for k in keys)
                self.cur.execute(sql, params)
                result = self.cur.fetchone()
                if result:
                    inserted_ids.append(result["id"])
            
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise AkronError(f"Bulk insert failed: {str(e)}")
        
        return inserted_ids

    def query(self, table_name: str, builder: QueryBuilder) -> List[Dict[str, Any]]:
        """Execute advanced query with QueryBuilder."""
        # Build SELECT clause
        if builder.select_fields:
            if isinstance(builder.select_fields, (list, tuple)):
                select_clause = ", ".join(builder.select_fields)
            else:
                select_clause = str(builder.select_fields[0])
        else:
            select_clause = "*"
        
        sql = f"SELECT {select_clause} FROM {table_name}"
        params = []
        
        # Build JOIN clauses
        for join_table, on_condition, join_type in builder.joins:
            sql += f" {join_type} JOIN {join_table} ON {on_condition}"
        
        # Build WHERE clause
        if builder.filters:
            conditions = []
            for key, value in builder.filters.items():
                if "__" in key:
                    field, operator = key.split("__", 1)
                    
                    if operator == "gt":
                        conditions.append(f"{field} > %s")
                    elif operator == "gte":
                        conditions.append(f"{field} >= %s")
                    elif operator == "lt":
                        conditions.append(f"{field} < %s")
                    elif operator == "lte":
                        conditions.append(f"{field} <= %s")
                    elif operator == "ne":
                        conditions.append(f"{field} != %s")
                    elif operator == "in":
                        if isinstance(value, (list, tuple)):
                            placeholders = ", ".join(["%s"] * len(value))
                            conditions.append(f"{field} IN ({placeholders})")
                            params.extend(value)
                            continue
                        else:
                            raise AkronError("Value for 'in' operator must be a list or tuple")
                    elif operator == "like":
                        conditions.append(f"{field} LIKE %s")
                    elif operator == "isnull":
                        if value:
                            conditions.append(f"{field} IS NULL")
                        else:
                            conditions.append(f"{field} IS NOT NULL")
                        continue
                    else:
                        raise AkronError(f"Unknown operator: {operator}")
                    
                    params.append(value)
                else:
                    conditions.append(f"{field} = %s")
                    params.append(value)
            
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
        
        # Build GROUP BY clause
        if builder.group_by_fields:
            group_fields = ", ".join(builder.group_by_fields)
            sql += f" GROUP BY {group_fields}"
        
        # Build HAVING clause
        if builder.having_conditions:
            having_conditions = []
            for key, value in builder.having_conditions.items():
                having_conditions.append(f"{key} = %s")
                params.append(value)
            sql += " HAVING " + " AND ".join(having_conditions)
        
        # Build ORDER BY clause
        if builder.sorts:
            order_fields = []
            for field, direction in builder.sorts:
                order_fields.append(f"{field} {direction}")
            sql += " ORDER BY " + ", ".join(order_fields)
        
        # Build LIMIT and OFFSET
        if builder.limit_count is not None:
            sql += f" LIMIT {builder.limit_count}"
            if builder.offset_count > 0:
                sql += f" OFFSET {builder.offset_count}"
        
        try:
            self.cur.execute(sql, tuple(params))
            return self.cur.fetchall()
        except psycopg2.Error as e:
            raise AkronError(f"Query failed: {str(e)}")

    def bulk_update(self, table_name: str, updates: List[Dict[str, Any]]) -> int:
        """Bulk update records."""
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
        sql = f"SELECT COUNT(*) as count FROM {table_name}"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = %s")
                params.append(value)
            sql += " WHERE " + " AND ".join(conditions)
        
        try:
            self.cur.execute(sql, tuple(params))
            result = self.cur.fetchone()
            return result["count"] if result else 0
        except psycopg2.Error as e:
            raise AkronError(f"Count failed: {str(e)}")

    def aggregate(self, table_name: str, aggregations: Dict[str, str], 
                  filters: Optional[Dict[str, Any]] = None, 
                  group_by: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Perform aggregations like sum, count, avg, min, max."""
        # Build SELECT clause with aggregations
        agg_fields = []
        for alias, func_spec in aggregations.items():
            if func_spec.lower() == "count":
                agg_fields.append(f"COUNT(*) as {alias}")
            else:
                if "(" in func_spec:
                    agg_fields.append(f"{func_spec.upper()} as {alias}")
                else:
                    if func_spec.lower() in ["sum", "avg", "min", "max"]:
                        agg_fields.append(f"{func_spec.upper()}(*) as {alias}")
                    else:
                        agg_fields.append(f"{func_spec} as {alias}")
        
        select_clause = ", ".join(agg_fields)
        sql = f"SELECT {select_clause} FROM {table_name}"
        params = []
        
        # Add WHERE clause
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = %s")
                params.append(value)
            sql += " WHERE " + " AND ".join(conditions)
        
        # Add GROUP BY clause
        if group_by:
            group_fields = ", ".join(group_by)
            sql = f"SELECT {group_fields}, {select_clause} FROM {table_name}"
            if filters:
                sql += " WHERE " + " AND ".join(conditions)
            sql += f" GROUP BY {group_fields}"
        
        try:
            self.cur.execute(sql, tuple(params))
            return self.cur.fetchall()
        except psycopg2.Error as e:
            raise AkronError(f"Aggregation failed: {str(e)}")

    def raw_sql(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute raw SQL query."""
        try:
            if params:
                self.cur.execute(sql, params)
            else:
                self.cur.execute(sql)
            
            # Check if it's a SELECT query
            if sql.strip().upper().startswith("SELECT"):
                return self.cur.fetchall()
            else:
                self.conn.commit()
                return [{"affected_rows": self.cur.rowcount}]
        
        except psycopg2.Error as e:
            self.conn.rollback()
            raise AkronError(f"SQL execution error: {str(e)}")

    def begin_transaction(self) -> None:
        """Begin a transaction."""
        try:
            self.conn.autocommit = False
        except psycopg2.Error as e:
            raise AkronError(f"Failed to begin transaction: {str(e)}")

    def commit_transaction(self) -> None:
        """Commit the current transaction."""
        try:
            self.conn.commit()
        except psycopg2.Error as e:
            raise AkronError(f"Failed to commit transaction: {str(e)}")

    def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        try:
            self.conn.rollback()
        except psycopg2.Error as e:
            raise AkronError(f"Failed to rollback transaction: {str(e)}")

    def create_index(self, table_name: str, columns: List[str], unique: bool = False) -> None:
        """Create an index on the specified columns."""
        cols_str = ", ".join(columns)
        index_name = f"idx_{table_name}_{'_'.join(columns)}"
        unique_str = "UNIQUE " if unique else ""
        sql = f"CREATE {unique_str}INDEX IF NOT EXISTS {index_name} ON {table_name} ({cols_str})"
        
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise AkronError(f"Failed to create index: {str(e)}")

    def drop_index(self, index_name: str) -> None:
        """Drop an index."""
        sql = f"DROP INDEX IF EXISTS {index_name}"
        
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise AkronError(f"Failed to drop index: {str(e)}")

    def close(self):
        """Close database connection."""
        try:
            if self.cur:
                self.cur.close()
        except Exception:
            pass
        try:
            if self.conn:
                self.conn.close()
        except Exception:
            pass
