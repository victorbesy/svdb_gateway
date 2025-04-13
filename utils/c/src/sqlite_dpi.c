#include "sqlite_dpi.h"
#include <stdio.h>
#include <sqlite3.h>

int open_database(const char *db_path, sqlite3 **db) {
    if (sqlite3_open(db_path, db) != SQLITE_OK) {
        fprintf(stderr, "Cannot open database: %s\n", sqlite3_errmsg(*db));
        return -1;
    }
    return 0;
}

int execute_query(sqlite3 *db, const char *query) {
    char *err_msg = NULL;
    if (sqlite3_exec(db, query, 0, 0, &err_msg) != SQLITE_OK) {
        fprintf(stderr, "SQL error: %s\n", err_msg);
        sqlite3_free(err_msg);
        return -1;
    }
    return 0;
}

void close_database(sqlite3 *db) {
    sqlite3_close(db);
}

int read_schema(sqlite3 *db) {
    const char *query = "SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') ORDER BY name;";
    sqlite3_stmt *stmt;

    if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) != SQLITE_OK) {
        fprintf(stderr, "Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        return -1;
    }

    printf("Schema:\n");
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        const char *name = (const char *)sqlite3_column_text(stmt, 0);
        const char *type = (const char *)sqlite3_column_text(stmt, 1);
        printf("Name: %s, Type: %s\n", name, type);
    }

    sqlite3_finalize(stmt);
    return 0;
}

int write_schema(sqlite3 *db, const char *table_name, const char *columns) {
    char query[1024];
    snprintf(query, sizeof(query), "CREATE TABLE IF NOT EXISTS %s (%s);", table_name, columns);

    if (execute_query(db, query) != 0) {
        fprintf(stderr, "Failed to create table: %s\n", table_name);
        return -1;
    }

    printf("Table '%s' created successfully.\n", table_name);
    return 0;
}