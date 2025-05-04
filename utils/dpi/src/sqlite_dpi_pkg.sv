/*
============================================================================
Title: sqlite_dpi_pkg.sv
 Copyright (c) 2016-2025 IC Verimeter. All rights reserved.

               Licensed under the MIT License.

               See LICENSE file in the project root for full license information.

Description : SQLite DPI bridge
               System Verilog to SQLite Database Interface
 ============================================================================
*/
`timescale 1ns/1ps

package sqlite_dpi_pkg;

`define SQLITE_MAX_PATH = 256;
`define SQLITE_MAX_QUERY = 1024;

   //Title: Utilities: System Verilog to C SQLite DPI bridge

   //Section: Data exchange structures and utilities

   /*
    Variable: sqlite_data_type_e
    (start code)
    *SQLite data types:*

    SQLITE_NULL     - NULL value
    SQLITE_INTEGER  - 64-bit signed integer
    SQLITE_FLOAT    - 64-bit IEEE floating point number
    SQLITE_TEXT     - UTF-8 or UTF-16 string
    SQLITE_BLOB     - Binary large object

    typedef enum {SQLITE_NULL, SQLITE_INTEGER, SQLITE_FLOAT, SQLITE_TEXT, SQLITE_BLOB} sqlite_data_type_e;
    (end)
    */

   /* verilator lint_off UNDRIVEN */
   typedef enum {SQLITE_NULL, SQLITE_INTEGER, SQLITE_FLOAT, SQLITE_TEXT, SQLITE_BLOB} sqlite_data_type_e;
   /* verilator lint_on UNDRIVEN */

   //Section: SQLite database operations

   /*
    Function: sqlite_dpi_open_database
    Open a SQLite database connection

    Parameters:
    db_path - path to the SQLite database file

    Returns:
    Database handle on success, null on failure

    Disable function `define: NO_SQLITE_DPI_OPEN_DATABASE
    */
`ifndef NO_SQLITE_DPI_OPEN_DATABASE
   import "DPI-C" function chandle sqlite_dpi_open_database(input string db_path);
`endif

   /*
    Function: sqlite_dpi_close_database
    Close a SQLite database connection

    Parameters:
    db - database handle to close

    Returns:
    N/A

    Disable function `define: NO_SQLITE_DPI_CLOSE_DATABASE
    */
`ifndef NO_SQLITE_DPI_CLOSE_DATABASE
   import "DPI-C" function void sqlite_dpi_close_database(input chandle db);
`endif

   /*
    Function: sqlite_dpi_execute_query
    Execute an SQL query

    Parameters:
    db - database handle
    query - SQL query string

    Returns:
    0 on success, -1 on failure

    Disable function `define: NO_SQLITE_DPI_EXECUTE_QUERY
    */
`ifndef NO_SQLITE_DPI_EXECUTE_QUERY
   import "DPI-C" function int sqlite_dpi_execute_query(input chandle db, input string query);
`endif

   /*
    Function: sqlite_dpi_read_schema
    Read the database schema

    Parameters:
    db - database handle

    Returns:
    0 on success, -1 on failure

    Disable function `define: NO_SQLITE_DPI_READ_SCHEMA
    */
`ifndef NO_SQLITE_DPI_READ_SCHEMA
   import "DPI-C" function int sqlite_dpi_read_schema(input chandle db);
`endif

   /*
    Function: sqlite_dpi_write_schema
    Create a new table in the database

    Parameters:
    db - database handle
    table_name - name of the table to create
    columns - column definitions

    Returns:
    0 on success, -1 on failure

    Disable function `define: NO_SQLITE_DPI_WRITE_SCHEMA
    */
`ifndef NO_SQLITE_DPI_WRITE_SCHEMA
   import "DPI-C" function int sqlite_dpi_write_schema(input chandle db, input string table_name, input string columns);
`endif

   /*
    Function: sqlite_dpi_table_exists
    Check if a table exists in the database

    Parameters:
    db - database handle
    table_name - name of the table to check

    Returns:
    1 if table exists, 0 if not, -1 on error

    Disable function `define: NO_SQLITE_DPI_TABLE_EXISTS
    */
`ifndef NO_SQLITE_DPI_TABLE_EXISTS
   import "DPI-C" function int sqlite_dpi_table_exists(input chandle db, input string table_name);
`endif

   /*
    Function: sqlite_dpi_get_row
    Retrieve a single row from a table

    Parameters:
    db - database handle
    table_name - name of the table to retrieve
    row_id - ID of the row to retrieve

    Returns:
    0 on success, -1 on failure

    Disable function `define: NO_SQLITE_DPI_GET_ROW
    */
`ifndef NO_SQLITE_DPI_GET_ROW
   import "DPI-C" function int sqlite_dpi_get_row(input chandle db, input string table_name, input int row_id);
`endif

   /*
    Function: sqlite_dpi_insert_row
    Insert a row into a table

    Parameters:
    db - database handle
    table - table name
    columns - JSON string containing column names
    values - JSON string containing values to insert

    Returns:
    ID of the inserted row, -1 on failure

    Disable function `define: NO_SQLITE_DPI_INSERT_ROW
    */
`ifndef NO_SQLITE_DPI_INSERT_ROW
   import "DPI-C" function int sqlite_dpi_insert_row(input chandle db, input string table_name, input string columns, input string values);
`endif

   /*
    Function: sqlite_dpi_delete_row
    Delete a row from a table

    Parameters:
    db - database handle
    table - table name
    row_id - ID of the row to delete

    Returns:
    0 on success, -1 on failure

    Disable function `define: NO_SQLITE_DPI_DELETE_ROW
    */
`ifndef NO_SQLITE_DPI_DELETE_ROW
   import "DPI-C" function int sqlite_dpi_delete_row(input chandle db, input string table_name, input int row_id);
`endif

   /*
    Function: sqlite_dpi_create_table
    Create a new table in the database

    Parameters:
    db - database handle
    table_name - name of the table to create
    columns - column definitions

    Returns:
    0 on success, -1 on failure

    Disable function `define: NO_SQLITE_DPI_CREATE_TABLE
    */
`ifndef NO_SQLITE_DPI_CREATE_TABLE
   import "DPI-C" function int sqlite_dpi_create_table(input chandle db, input string table_name, input string columns);
`endif

   /*
    Function: sqlite_dpi_drop_table
    Drop a table from the database

    Parameters:
    db - database handle
    table_name - name of the table to drop

    Returns:
    0 on success, -1 on failure

    Disable function `define: NO_SQLITE_DPI_DROP_TABLE
    */
`ifndef NO_SQLITE_DPI_DROP_TABLE
   import "DPI-C" function int sqlite_dpi_drop_table(input chandle db, input string table_name);
`endif

   /*
    Function: sqlite_dpi_get_all_rows
    Retrieve all rows from a table

    Parameters:
    db - database handle
    table_name - name of the table
    rows - output pointer to rows data
    row_count - output pointer to row count
    col_count - output pointer to column count

    Returns:
    0 on success, -1 on failure

    Disable function `define: NO_SQLITE_DPI_GET_ALL_ROWS
    */
`ifndef NO_SQLITE_DPI_GET_ALL_ROWS
   import "DPI-C" function int sqlite_dpi_get_all_rows(input chandle db, input string table_name, output chandle rows, output int row_count, output int col_count);
`endif

   /*
    Function: sqlite_dpi_create_index
    Create an index on a table column

    Parameters:
    db - database handle
    index_name - name of the index to create
    table - name of the table
    column - name of the column to index

    Returns:
    0 on success, -1 on failure

    Disable function `define: NO_SQLITE_DPI_CREATE_INDEX
    */
`ifndef NO_SQLITE_DPI_CREATE_INDEX
   import "DPI-C" function int sqlite_dpi_create_index(input chandle db, input string index_name, input string table_name, input string column);
`endif

   /*
    Function: sqlite_dpi_drop_index
    Drop an index from the database

    Parameters:
    db - database handle
    index_name - name of the index to drop

    Returns:
    0 on success, -1 on failure

    Disable function `define: NO_SQLITE_DPI_DROP_INDEX
    */
`ifndef NO_SQLITE_DPI_DROP_INDEX
   import "DPI-C" function int sqlite_dpi_drop_index(input chandle db, input string index_name);
`endif

   /*
    Function: sqlite_dpi_begin_transaction
    Begin a transaction

    Parameters:
    db - database handle

    Returns:
    0 on success, -1 on failure

    Disable function `define: NO_SQLITE_DPI_BEGIN_TRANSACTION
    */
`ifndef NO_SQLITE_DPI_BEGIN_TRANSACTION
   import "DPI-C" function int sqlite_dpi_begin_transaction(input chandle db);
`endif

   /*
    Function: sqlite_dpi_commit_transaction
    Commit a transaction

    Parameters:
    db - database handle

    Returns:
    0 on success, -1 on failure

    Disable function `define: NO_SQLITE_DPI_COMMIT_TRANSACTION
    */
`ifndef NO_SQLITE_DPI_COMMIT_TRANSACTION
   import "DPI-C" function int sqlite_dpi_commit_transaction(input chandle db);
`endif

   /*
    Function: sqlite_dpi_rollback_transaction
    Rollback a transaction

    Parameters:
    db - database handle

    Returns:
    0 on success, -1 on failure

    Disable function `define: NO_SQLITE_DPI_ROLLBACK_TRANSACTION
    */
`ifndef NO_SQLITE_DPI_ROLLBACK_TRANSACTION
   import "DPI-C" function int sqlite_dpi_rollback_transaction(input chandle db);
`endif

   /*
    Function: sqlite_dpi_vacuum_database
    Optimize the database by rebuilding it

    Parameters:
    db - database handle

    Returns:
    0 on success, -1 on failure

    Disable function `define: NO_SQLITE_DPI_VACUUM_DATABASE
    */
`ifndef NO_SQLITE_DPI_VACUUM_DATABASE
   import "DPI-C" function int sqlite_dpi_vacuum_database(input chandle db);
`endif

endpackage : sqlite_dpi_pkg

