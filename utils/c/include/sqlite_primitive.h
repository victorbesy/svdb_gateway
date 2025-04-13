#ifndef SQLITE_PRIMITIVE_H
#define SQLITE_PRIMITIVE_H

#include <sqlite3.h>

/************************************************
 * Connection Management
 ************************************************/
int open_database(const char *db_path, sqlite3 **db);
void close_database(sqlite3 *db);
int execute_query(sqlite3 *db, const char *query);

/************************************************
 * Single Row/Column Operations
 ************************************************/
int get_row(sqlite3 *db, const char *table, int row_id, char ***columns, char ***values, int *col_count);
int insert_row(sqlite3 *db, const char *table, const char **columns, const char **values, int count);
int delete_row(sqlite3 *db, const char *table, int row_id);

/************************************************
 * Multi-Row Operations
 ************************************************/
int get_all_rows(sqlite3 *db, const char *table, char ****rows, int *row_count, int *col_count);

/************************************************
 * Table Operations
 ************************************************/
int create_table(sqlite3 *db, const char *table_name, const char *columns);
int drop_table(sqlite3 *db, const char *table_name);

/************************************************
 * Index Management
 ************************************************/
int create_index(sqlite3 *db, const char *index_name, const char *table, const char *column);
int drop_index(sqlite3 *db, const char *index_name);

/************************************************
 * Transaction Control
 ************************************************/
int begin_transaction(sqlite3 *db);
int commit_transaction(sqlite3 *db);
int rollback_transaction(sqlite3 *db);

/************************************************
 * Database Maintenance
 ************************************************/
int vacuum_database(sqlite3 *db);
int table_exists(sqlite3 *db, const char *table_name);

#endif // SQLITE_PRIMITIVE_H