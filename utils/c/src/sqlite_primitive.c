#include "sqlite_primitive.h"
#include <string.h>
#include <stdlib.h>
#include <stdarg.h>

void dbg_print(const char *prefix, const char *func_name, const char *format, ...) {
#ifdef VERBOSE
    va_list args;
    va_start(args, format);
    fprintf(stderr, "%s SVDB [%s]: ", prefix, func_name);
    vfprintf(stderr, format, args);
    va_end(args);
#endif
}

void err_print(const char *prefix, const char *func_name, const char *format, ...) {
    va_list args;
    va_start(args, format);
    fprintf(stderr, "%s SVDB [%s]: ", prefix, func_name);
    vfprintf(stderr, format, args);
    va_end(args);
}

/************************************************
 * Connection Management
 ************************************************/

sqlite3 *sqlite_prim_open_database(const char *db_path) {
    dbg_print("C_PRIM", "sqlite_prim_open_database", "Attempting to open database at: %s\n", db_path);
    sqlite3 *db = NULL;
    int result = sqlite3_open(db_path, &db);
    if (result != SQLITE_OK) {
        err_print("C_PRIM", "sqlite_prim_open_database", "Cannot open database: %s\n", sqlite3_errmsg(db));
        err_print("C_PRIM", "sqlite_prim_open_database", "SQLite error code: %d\n", result);
        if (db) {
            sqlite3_close(db);
        }
        return NULL;
    }
    dbg_print("C_PRIM", "sqlite_prim_open_database", "Successfully opened database\n");
    return db;
}

void sqlite_prim_close_database(sqlite3 *db) {
    dbg_print("C_PRIM", "sqlite_prim_close_database", "Closing database\n");
    sqlite3_close(db);
}

int sqlite_prim_execute_query(sqlite3 *db, const char *query) {
    sqlite3_stmt *stmt;
    int result;

    dbg_print("C_PRIM", "sqlite_prim_execute_query", "Executing query: %s\n", query);

    if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) != SQLITE_OK) {
        err_print("C_PRIM", "sqlite_prim_execute_query", "Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        return -1;
    }

    // Print column headers
    int col_count = sqlite3_column_count(stmt);
    dbg_print("C_PRIM", "sqlite_prim_execute_query", "Query result columns: %d\n", col_count);

    dbg_print("C_PRIM", "sqlite_prim_execute_query", "|");
    for (int i = 0; i < col_count; i++) {
        fprintf(stderr, " %s |", sqlite3_column_name(stmt, i));
    }
    fprintf(stderr, "\n");

    if (col_count > 0) {
        dbg_print("C_PRIM", "sqlite_prim_execute_query", "|");
        for (int i = 0; i < col_count; i++) {
            fprintf(stderr, "----|");
        }
        fprintf(stderr, "\n");
    }

    // Execute query and print results
    while ((result = sqlite3_step(stmt)) == SQLITE_ROW) {
        dbg_print("C_PRIM", "sqlite_prim_execute_query", "|");
        for (int i = 0; i < col_count; i++) {
            const char *val = (const char *)sqlite3_column_text(stmt, i);
            fprintf(stderr, " %s |", val ? val : "NULL");
        }
        fprintf(stderr, "\n");
    }

    if (result != SQLITE_DONE) {
        err_print("C_PRIM", "sqlite_prim_execute_query", "SQL error: %s\n", sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return -1;
    }

    sqlite3_finalize(stmt);
    return 0;
}

/************************************************
 * Single Row/Column Operations
 ************************************************/

int sqlite_prim_get_row(sqlite3 *db, const char *table, int row_id, char ***columns, char ***values, int *col_count) {
    char query[256];
    sqlite3_stmt *stmt;

    dbg_print("C_PRIM", "sqlite_prim_get_row", "Getting row %d from table %s\n", row_id, table);

    snprintf(query, sizeof(query), "SELECT * FROM %s WHERE id = ?", table);

    if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) != SQLITE_OK) {
        err_print("C_PRIM", "sqlite_prim_get_row", "Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        return -1;
    }

    sqlite3_bind_int(stmt, 1, row_id);

    if (sqlite3_step(stmt) == SQLITE_ROW) {
        *col_count = sqlite3_column_count(stmt);
        *columns = malloc(*col_count * sizeof(char *));
        *values = malloc(*col_count * sizeof(char *));

        for (int i = 0; i < *col_count; i++) {
            (*columns)[i] = strdup(sqlite3_column_name(stmt, i));
            const char *val = (const char *)sqlite3_column_text(stmt, i);
            (*values)[i] = val ? strdup(val) : NULL;
            dbg_print("C_PRIM", "sqlite_prim_get_row", "Column %s = %s\n", (*columns)[i], (*values)[i]);
        }
        sqlite3_finalize(stmt);
        return 0;
    }

    sqlite3_finalize(stmt);
    return -1;
}

int sqlite_prim_insert_row(sqlite3 *db, const char *table, const char **columns, const char **values, int count) {
    char query[2048];
    char cols[1024] = "";
    char vals[1024] = "";
    sqlite3_stmt *stmt;
    int result;

    dbg_print("C_PRIM", "sqlite_prim_insert_row", "Inserting into table: %s\n", table);

    // Build columns and values strings
    for (int i = 0; i < count; i++) {
        strcat(cols, columns[i]);
        strcat(vals, "?");
        if (i < count - 1) {
            strcat(cols, ", ");
            strcat(vals, ", ");
        }
    }

    dbg_print("C_PRIM", "sqlite_prim_insert_row", "Columns: %s\n", cols);
    dbg_print("C_PRIM", "sqlite_prim_insert_row", "Values: ");
    for (int i = 0; i < count; i++) {
        fprintf(stderr, "%s ", values[i]);
    }
    fprintf(stderr, "\n");

    snprintf(query, sizeof(query), "INSERT INTO %s (%s) VALUES (%s)", table, cols, vals);

    if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) != SQLITE_OK) {
        err_print("C_PRIM", "sqlite_prim_insert_row", "Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        err_print("C_PRIM", "sqlite_prim_insert_row", "Query: %s\n", query);
        return -1;
    }

    for (int i = 0; i < count; i++) {
        result = sqlite3_bind_text(stmt, i + 1, values[i], -1, SQLITE_STATIC);
        if (result != SQLITE_OK) {
            err_print("C_PRIM", "sqlite_prim_insert_row", "Failed to bind value %d: %s\n", i + 1, sqlite3_errmsg(db));
            sqlite3_finalize(stmt);
            return -1;
        }
    }

    result = sqlite3_step(stmt);
    if (result != SQLITE_DONE) {
        err_print("C_PRIM", "sqlite_prim_insert_row", "Failed to execute statement: %s\n", sqlite3_errmsg(db));
        err_print("C_PRIM", "sqlite_prim_insert_row", "SQLite error code: %d\n", result);
        sqlite3_finalize(stmt);
        return -1;
    }

    result = sqlite3_last_insert_rowid(db);
    dbg_print("C_PRIM", "sqlite_prim_insert_row", "Inserted row with ID: %d\n", result);
    sqlite3_finalize(stmt);
    return result;
}

int sqlite_prim_delete_row(sqlite3 *db, const char *table, int row_id) {
    char query[256];
    sqlite3_stmt *stmt;

    snprintf(query, sizeof(query), "DELETE FROM %s WHERE id = ?", table);

    if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) != SQLITE_OK) {
        err_print("C_PRIM", "sqlite_prim_delete_row", "Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        return -1;
    }

    sqlite3_bind_int(stmt, 1, row_id);

    if (sqlite3_step(stmt) != SQLITE_DONE) {
        err_print("C_PRIM", "sqlite_prim_delete_row", "Failed to execute statement: %s\n", sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return -1;
    }

    sqlite3_finalize(stmt);
    return 0;
}

/************************************************
 * Multi-Row Operations
 ************************************************/

int sqlite_prim_get_all_rows(sqlite3 *db, const char *table, char ****rows, int *row_count, int *col_count) {
    char query[256];
    sqlite3_stmt *stmt;

    snprintf(query, sizeof(query), "SELECT * FROM %s", table);

    if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) != SQLITE_OK) {
        err_print("C_PRIM", "sqlite_prim_get_all_rows", "Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        return -1;
    }

    *row_count = 0;
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        (*row_count)++;
    }
    sqlite3_reset(stmt);

    *col_count = sqlite3_column_count(stmt);
    *rows = malloc(*row_count * sizeof(char **));

    int row = 0;
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        (*rows)[row] = malloc(*col_count * sizeof(char *));
        for (int col = 0; col < *col_count; col++) {
            const char *val = (const char *)sqlite3_column_text(stmt, col);
            (*rows)[row][col] = val ? strdup(val) : NULL;
        }
        row++;
    }

    sqlite3_finalize(stmt);
    return 0;
}

/************************************************
 * Table Operations
 ************************************************/

int sqlite_prim_create_table(sqlite3 *db, const char *table_name, const char *columns) {
    char query[1024];
    snprintf(query, sizeof(query), "CREATE TABLE IF NOT EXISTS %s (%s);", table_name, columns);
    return sqlite_prim_execute_query(db, query);
}

int sqlite_prim_drop_table(sqlite3 *db, const char *table_name) {
    char query[256];
    snprintf(query, sizeof(query), "DROP TABLE IF EXISTS %s;", table_name);
    return sqlite_prim_execute_query(db, query);
}

int sqlite_prim_read_table_schema(sqlite3 *db) {
    const char *query = "SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') ORDER BY name;";
    sqlite3_stmt *stmt;

    if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) != SQLITE_OK) {
        err_print("C_PRIM", "sqlite_prim_read_table_schema", "Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        return -1;
    }

    dbg_print("C_PRIM", "sqlite_prim_read_table_schema", "Schema:\n");
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        const char *name = (const char *)sqlite3_column_text(stmt, 0);
        const char *type = (const char *)sqlite3_column_text(stmt, 1);
        dbg_print("C_PRIM", "sqlite_prim_read_table_schema", "Name: %s, Type: %s\n", name, type);
    }

    sqlite3_finalize(stmt);
    return 0;
}

/************************************************
 * Index Management
 ************************************************/

int sqlite_prim_create_index(sqlite3 *db, const char *index_name, const char *table_name, const char *column) {
    char query[256];
    snprintf(query, sizeof(query), "CREATE INDEX IF NOT EXISTS %s ON %s(%s);", index_name, table_name, column);
    return sqlite_prim_execute_query(db, query);
}

int sqlite_prim_drop_index(sqlite3 *db, const char *index_name) {
    char query[256];
    snprintf(query, sizeof(query), "DROP INDEX IF EXISTS %s;", index_name);
    return sqlite_prim_execute_query(db, query);
}

/************************************************
 * Transaction Control
 ************************************************/

int sqlite_prim_begin_transaction(sqlite3 *db) {
    return sqlite_prim_execute_query(db, "BEGIN TRANSACTION;");
}

int sqlite_prim_commit_transaction(sqlite3 *db) {
    return sqlite_prim_execute_query(db, "COMMIT;");
}

int sqlite_prim_rollback_transaction(sqlite3 *db) {
    return sqlite_prim_execute_query(db, "ROLLBACK;");
}

/************************************************
 * Database Maintenance
 ************************************************/

int sqlite_prim_vacuum_database(sqlite3 *db) {
    return sqlite_prim_execute_query(db, "VACUUM;");
}

int sqlite_prim_table_exists(sqlite3 *db, const char *table_name) {
    char query[256];
    sqlite3_stmt *stmt;

    snprintf(query, sizeof(query), "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='%s';", table_name);

    if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) != SQLITE_OK) {
        err_print("C_PRIM", "sqlite_prim_table_exists", "Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        return -1;
    }

    int exists = 0;
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        exists = sqlite3_column_int(stmt, 0);
    }

    sqlite3_finalize(stmt);
    return exists;
}
