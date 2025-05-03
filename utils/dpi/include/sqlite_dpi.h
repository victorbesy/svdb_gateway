#ifndef SQLITE_DPI_H
#define SQLITE_DPI_H

#include "sqlite_primitive.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/************************************************
 * Connection Management
 ************************************************/
sqlite3 *sqlite_dpi_open_database(const char *db_path);
void sqlite_dpi_close_database(sqlite3 *db);
int sqlite_dpi_execute_query(sqlite3 *db, const char *query);

/************************************************
 * Table Operations
 ************************************************/
int sqlite_dpi_read_schema(sqlite3 *db);
int sqlite_dpi_write_schema(sqlite3 *db, const char *table_name, const char *columns);
int sqlite_dpi_table_exists(sqlite3 *db, const char *table_name);
int sqlite_dpi_insert_row(sqlite3 *db, const char *table_name, const char *columns, const char *values);
int sqlite_dpi_delete_row(sqlite3 *db, const char *table_name, int row_id);
int sqlite_dpi_get_row(sqlite3 *db, const char *table_name, int row_id);

/************************************************
 * Transaction Control
 ************************************************/
int sqlite_dpi_begin_transaction(sqlite3 *db);
int sqlite_dpi_commit_transaction(sqlite3 *db);
int sqlite_dpi_rollback_transaction(sqlite3 *db);

/************************************************
 * Database Maintenance
 ************************************************/
int sqlite_dpi_vacuum_database(sqlite3 *db);

#endif // SQLITE_DPI_H