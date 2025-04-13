import sqlite3
from typing import Dict, List, Any, Optional, Tuple, Union
from contextlib import contextmanager

#################################################
# Connection Management
#################################################

@contextmanager
def get_connection(db_path: str):
    """Context manager for database connections."""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()

#################################################
# Single Row/Column Operations
#################################################

def get_row(db_path: str, table: str, row_id: int) -> Optional[Dict[str, Any]]:
    """Get single row by primary key."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (row_id,))
        columns = [description[0] for description in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row)) if row else None

def get_column_value(db_path: str, table: str, column: str, row_id: int) -> Any:
    """Get specific column from single row."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT {column} FROM {table} WHERE id = ?", (row_id,))
        result = cursor.fetchone()
        return result[0] if result else None

def insert_row(db_path: str, table: str, data: Dict[str, Any]) -> int:
    """Insert single row."""
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, list(data.values()))
        conn.commit()
        return cursor.lastrowid

def update_row(db_path: str, table: str, row_id: int, data: Dict[str, Any]) -> bool:
    """Update single row."""
    set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE id = ?"

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        values = list(data.values()) + [row_id]
        cursor.execute(query, values)
        conn.commit()
        return cursor.rowcount > 0

def delete_row(db_path: str, table: str, row_id: int) -> bool:
    """Delete single row."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
        conn.commit()
        return cursor.rowcount > 0

#################################################
# Multi-Row Operations
#################################################

def get_all_rows(db_path: str, table: str) -> List[Dict[str, Any]]:
    """Get all rows from table."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_columns(db_path: str, table: str, columns: List[str], condition: str = None) -> List[Tuple]:
    """Get specific columns with optional condition."""
    query = f"SELECT {', '.join(columns)} FROM {table}"
    if condition:
        query += f" WHERE {condition}"

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()

def count_rows(db_path: str, table: str, condition: str = None) -> int:
    """Count rows in table with optional condition."""
    query = f"SELECT COUNT(*) FROM {table}"
    if condition:
        query += f" WHERE {condition}"

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchone()[0]

def insert_many_rows(db_path: str, table: str, data_list: List[Dict[str, Any]]) -> bool:
    """Insert multiple rows."""
    if not data_list:
        return False

    columns = data_list[0].keys()
    placeholders = ', '.join(['?' for _ in columns])
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(query, [list(data.values()) for data in data_list])
        conn.commit()
        return True

def update_many_rows(db_path: str, table: str, set_values: Dict[str, Any], condition: str) -> int:
    """Update multiple rows based on condition."""
    set_clause = ', '.join([f"{k} = ?" for k in set_values.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE {condition}"

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, list(set_values.values()))
        conn.commit()
        return cursor.rowcount

def delete_many_rows(db_path: str, table: str, condition: str) -> int:
    """Delete multiple rows based on condition."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table} WHERE {condition}")
        conn.commit()
        return cursor.rowcount

#################################################
# Table Operations
#################################################

def create_table(db_path: str, table: str, columns: Dict[str, str]) -> bool:
    """Create new table."""
    columns_def = ', '.join([f"{name} {dtype}" for name, dtype in columns.items()])
    query = f"CREATE TABLE IF NOT EXISTS {table} ({columns_def})"

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        return True

def add_column(db_path: str, table: str, column: str, datatype: str) -> bool:
    """Add new column to existing table."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {datatype}")
        conn.commit()
        return True

def drop_table(db_path: str, table: str) -> bool:
    """Drop table from database."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        conn.commit()
        return True

def list_tables(db_path: str) -> List[str]:
    """List all tables in database."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cursor.fetchall()]

def get_table_schema(db_path: str, table: str) -> List[Dict[str, Any]]:
    """Get table schema information."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        return [dict(zip(['cid', 'name', 'type', 'notnull', 'dflt_value', 'pk'], row))
                for row in cursor.fetchall()]

#################################################
# Index Management
#################################################

def create_index(db_path: str, table: str, column: str, index_name: str = None) -> bool:
    """Create index on column."""
    if not index_name:
        index_name = f"idx_{table}_{column}"

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column})")
        conn.commit()
        return True

def drop_index(db_path: str, index_name: str) -> bool:
    """Drop index."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
        conn.commit()
        return True

#################################################
# Transaction Control
#################################################

@contextmanager
def transaction(db_path: str):
    """Transaction context manager."""
    with get_connection(db_path) as conn:
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

#################################################
# Database Maintenance
#################################################

def vacuum_database(db_path: str) -> bool:
    """Optimize database with VACUUM."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("VACUUM")
        return True

def table_exists(db_path: str, table: str) -> bool:
    """Check if table exists."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='table' AND name=?
        """, (table,))
        return cursor.fetchone()[0] > 0