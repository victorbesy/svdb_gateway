#ifndef SQLITE_DPI_H
#define SQLITE_DPI_H

#include <sqlite3.h>

// Function prototypes
int open_database(const char *db_path, sqlite3 **db);
int execute_query(sqlite3 *db, const char *query);
void close_database(sqlite3 *db);
int read_schema(sqlite3 *db);
int write_schema(sqlite3 *db, const char *table_name, const char *columns);

#endif // SQLITE_DPI_H