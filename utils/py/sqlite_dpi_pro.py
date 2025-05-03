import sqlite3
from typing import Dict, List, Any, Optional, Tuple, Union
from contextlib import contextmanager

#################################################
# Connection Management
#################################################

def get_connection(db_path: str):
    """
    Create and return a database connection with close method.
    Use with a try-finally block for proper resource management.
    """
    conn = sqlite3.connect(db_path)
    return conn

def close_connection(conn):
    """Close a database connection."""
    if conn:
        conn.close()

#################################################
# Single Row/Column Operations
#################################################

def get_row(db_path: str, table: str, row_id: int) -> Optional[Dict[str, Any]]:
    """Get single row by primary key."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (row_id,))
    columns = [description[0] for description in cursor.description]
    row = cursor.fetchone()
    close_connection(conn)
    return dict(zip(columns, row)) if row else None

def get_column_value(db_path: str, table: str, column: str, row_id: int) -> Any:
    """Get specific column from single row."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT {column} FROM {table} WHERE id = ?", (row_id,))
    result = cursor.fetchone()
    close_connection(conn)
    return result[0] if result else None

def insert_row(db_path: str, table: str, data: Dict[str, Any]) -> int:
    """Insert single row."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, list(data.values()))
    conn.commit()
    row_id = cursor.lastrowid
    close_connection(conn)
    return row_id

def update_row(db_path: str, table: str, row_id: int, data: Dict[str, Any]) -> bool:
    """Update single row."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE id = ?"
    values = list(data.values()) + [row_id]
    cursor.execute(query, values)
    conn.commit()
    close_connection(conn)
    return cursor.rowcount > 0

def delete_row(db_path: str, table: str, row_id: int) -> bool:
    """Delete single row."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
    conn.commit()
    close_connection(conn)
    return cursor.rowcount > 0

#################################################
# Multi-Row Operations
#################################################

def get_all_rows(db_path: str, table: str) -> List[Dict[str, Any]]:
    """Get all rows from table."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    close_connection(conn)
    return [dict(zip(columns, row)) for row in rows]

def get_columns(db_path: str, table: str, columns: List[str], condition: str = None) -> List[Tuple]:
    """Get specific columns with optional condition."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    query = f"SELECT {', '.join(columns)} FROM {table}"
    if condition:
        query += f" WHERE {condition}"
    cursor.execute(query)
    columns = cursor.fetchall()
    close_connection(conn)
    return columns

def count_rows(db_path: str, table: str, condition: str = None) -> int:
    """Count rows in table with optional condition."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    query = f"SELECT COUNT(*) FROM {table}"
    if condition:
        query += f" WHERE {condition}"
    cursor.execute(query)
    result = cursor.fetchone()
    close_connection(conn)
    return result[0]

def insert_many_rows(db_path: str, table: str, data_list: List[Dict[str, Any]]) -> bool:
    """Insert multiple rows."""
    if not data_list:
        return False

    conn = get_connection(db_path)
    cursor = conn.cursor()
    columns = data_list[0].keys()
    placeholders = ', '.join(['?' for _ in columns])
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    cursor.executemany(query, [list(data.values()) for data in data_list])
    conn.commit()
    close_connection(conn)
    return True

def update_many_rows(db_path: str, table: str, set_values: Dict[str, Any], condition: str) -> int:
    """Update multiple rows based on condition."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    set_clause = ', '.join([f"{k} = ?" for k in set_values.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
    cursor.execute(query, list(set_values.values()))
    conn.commit()
    close_connection(conn)
    return cursor.rowcount

def delete_many_rows(db_path: str, table: str, condition: str) -> int:
    """Delete multiple rows based on condition."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table} WHERE {condition}")
    conn.commit()
    close_connection(conn)
    return cursor.rowcount

#################################################
# Table Operations
#################################################

def create_table(db_path: str, table: str, columns: Dict[str, str]) -> bool:
    """Create new table."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    columns_def = ', '.join([f"{name} {dtype}" for name, dtype in columns.items()])
    query = f"CREATE TABLE IF NOT EXISTS {table} ({columns_def})"
    cursor.execute(query)
    conn.commit()
    close_connection(conn)
    return True

def add_column(db_path: str, table: str, column: str, datatype: str) -> bool:
    """Add new column to existing table."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {datatype}")
    conn.commit()
    close_connection(conn)
    return True

def drop_table(db_path: str, table: str) -> bool:
    """Drop table from database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    close_connection(conn)
    return True

def list_tables(db_path: str) -> List[str]:
    """List all tables in database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    close_connection(conn)
    return [row[0] for row in tables]

def get_table_schema(db_path: str, table: str) -> List[Dict[str, Any]]:
    """Get table schema information."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    schema = cursor.fetchall()
    close_connection(conn)
    return [dict(zip(['cid', 'name', 'type', 'notnull', 'dflt_value', 'pk'], row)) for row in schema]

#################################################
# Index Management
#################################################

def create_index(db_path: str, table: str, column: str, index_name: str = None) -> bool:
    """Create index on column."""
    if not index_name:
        index_name = f"idx_{table}_{column}"

    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column})")
    conn.commit()
    close_connection(conn)
    return True

def drop_index(db_path: str, index_name: str) -> bool:
    """Drop index."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
    conn.commit()
    close_connection(conn)
    return True

#################################################
# Transaction Control
#################################################

def begin_transaction(db_path: str):
    """
    Begin a database transaction.
    Returns a connection with transaction started.
    """
    conn = get_connection(db_path)
    return conn

def commit_transaction(conn):
    """Commit a transaction."""
    if conn:
        conn.commit()

def rollback_transaction(conn):
    """Rollback a transaction."""
    if conn:
        conn.rollback()

#################################################
# Database Maintenance
#################################################

def vacuum_database(db_path: str) -> bool:
    """Optimize database with VACUUM."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("VACUUM")
    conn.commit()
    close_connection(conn)
    return True

def table_exists(db_path: str, table: str) -> bool:
    """Check if table exists."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM sqlite_master
        WHERE type='table' AND name=?
    """, (table,))
    result = cursor.fetchone()
    close_connection(conn)
    return result[0] > 0

#################################################
# Aggregate Functions
#################################################

def get_sum(db_path: str, table: str, column: str, condition: str = None) -> Union[int, float, None]:
    """Calculate sum of a column with optional condition."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    query = f"SELECT SUM({column}) FROM {table}"
    if condition:
        query += f" WHERE {condition}"
    cursor.execute(query)
    result = cursor.fetchone()
    close_connection(conn)
    return result[0] if result else None

def get_avg(db_path: str, table: str, column: str, condition: str = None) -> Union[float, None]:
    """Calculate average of a column with optional condition."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    query = f"SELECT AVG({column}) FROM {table}"
    if condition:
        query += f" WHERE {condition}"
    cursor.execute(query)
    result = cursor.fetchone()
    close_connection(conn)
    return result[0] if result else None

def get_min(db_path: str, table: str, column: str, condition: str = None) -> Any:
    """Get minimum value in a column with optional condition."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    query = f"SELECT MIN({column}) FROM {table}"
    if condition:
        query += f" WHERE {condition}"
    cursor.execute(query)
    result = cursor.fetchone()
    close_connection(conn)
    return result[0] if result else None

def get_max(db_path: str, table: str, column: str, condition: str = None) -> Any:
    """Get maximum value in a column with optional condition."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    query = f"SELECT MAX({column}) FROM {table}"
    if condition:
        query += f" WHERE {condition}"
    cursor.execute(query)
    result = cursor.fetchone()
    close_connection(conn)
    return result[0] if result else None

def get_group_by(db_path: str, table: str, group_column: str, agg_functions: List[Tuple[str, str]], 
                condition: str = None, having: str = None, order_by: str = None, limit: int = None) -> List[Dict[str, Any]]:
    """
    Perform GROUP BY query with multiple aggregate functions.
    
    Args:
        db_path: Path to SQLite database
        table: Table name
        group_column: Column to group by
        agg_functions: List of tuples (agg_func, column), e.g. [("SUM", "amount"), ("AVG", "price")]
        condition: Optional WHERE clause
        having: Optional HAVING clause
        order_by: Optional ORDER BY clause
        limit: Optional LIMIT value
    
    Returns:
        List of dictionaries with group values and aggregate results
    """
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Build select clause with group column and aggregates
    agg_parts = [f"{func}({col}) AS {func.lower()}_{col}" for func, col in agg_functions]
    select_clause = f"{group_column}, " + ", ".join(agg_parts)
    
    query = f"SELECT {select_clause} FROM {table}"
    if condition:
        query += f" WHERE {condition}"
    
    query += f" GROUP BY {group_column}"
    
    if having:
        query += f" HAVING {having}"
    
    if order_by:
        query += f" ORDER BY {order_by}"
    
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    result = cursor.fetchall()
    close_connection(conn)
    return [dict(row) for row in result]

def insert_blob(db_path: str, table: str, column: str, blob_data: bytes, row_id: int) -> bool:
    """Insert binary data into a specific column and row."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {table} SET {column} = ? WHERE id = ?", (blob_data, row_id))
    conn.commit()
    close_connection(conn)
    return True

def get_blob(db_path: str, table: str, column: str, row_id: int) -> Optional[bytes]:
    """Retrieve binary data from a specific column and row."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT {column} FROM {table} WHERE id = ?", (row_id,))
    result = cursor.fetchone()
    close_connection(conn)
    return result[0] if result else None

def add_foreign_key(db_path: str, table: str, column: str, ref_table: str, ref_column: str) -> bool:
    """Add foreign key constraint to existing table."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} INTEGER REFERENCES {ref_table}({ref_column})")
    conn.commit()
    close_connection(conn)
    return True

def list_foreign_keys(db_path: str, table: str) -> List[Dict[str, str]]:
    """List all foreign keys defined on a table."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA foreign_key_list({table})")
    result = cursor.fetchall()
    close_connection(conn)
    return [dict(zip(['id', 'seq', 'table', 'from', 'to', 'on_delete', 'on_update'], row)) for row in result]