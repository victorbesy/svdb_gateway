#include "sqlite_primitive.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sqlite3.h>

/************************************************
 * Connection Management
 ************************************************/

int open_database(const char *db_path, sqlite3 **db) {
    if (sqlite3_open(db_path, db) != SQLITE_OK) {
        fprintf(stderr, "Cannot open database: %s\n", sqlite3_errmsg(*db));
        return -1;
    }
    return 0;
}

void close_database(sqlite3 *db) {
    sqlite3_close(db);
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

/************************************************
 * Single Row/Column Operations
 ************************************************/

int get_row(sqlite3 *db, const char *table, int row_id, char ***columns, char ***values, int *col_count) {
    char query[256];
    sqlite3_stmt *stmt;

    snprintf(query, sizeof(query), "SELECT * FROM %s WHERE id = ?", table);

    if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) != SQLITE_OK) {
        fprintf(stderr, "Failed to prepare statement: %s\n", sqlite3_errmsg(db));
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
        }
        sqlite3_finalize(stmt);
        return 0;
    }

    sqlite3_finalize(stmt);
    return -1;
}

int insert_row(sqlite3 *db, const char *table, const char **columns, const char **values, int count) {
    char query[1024];
    char cols[512] = "";
    char vals[512] = "";
    sqlite3_stmt *stmt;

    for (int i = 0; i < count; i++) {
        strcat(cols, columns[i]);
        strcat(vals, "?");
        if (i < count - 1) {
            strcat(cols, ", ");
            strcat(vals, ", ");
        }
    }

    snprintf(query, sizeof(query), "INSERT INTO %s (%s) VALUES (%s)", table, cols, vals);

    if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) != SQLITE_OK) {
        fprintf(stderr, "Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        return -1;
    }

    for (int i = 0; i < count; i++) {
        sqlite3_bind_text(stmt, i + 1, values[i], -1, SQLITE_STATIC);
    }

    if (sqlite3_step(stmt) != SQLITE_DONE) {
        fprintf(stderr, "Failed to execute statement: %s\n", sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return -1;
    }

    sqlite3_finalize(stmt);
    return sqlite3_last_insert_rowid(db);
}

int delete_row(sqlite3 *db, const char *table, int row_id) {
    char query[256];
    sqlite3_stmt *stmt;

    snprintf(query, sizeof(query), "DELETE FROM %s WHERE id = ?", table);

    if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) != SQLITE_OK) {
        fprintf(stderr, "Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        return -1;
    }

    sqlite3_bind_int(stmt, 1, row_id);

    if (sqlite3_step(stmt) != SQLITE_DONE) {
        fprintf(stderr, "Failed to execute statement: %s\n", sqlite3_errmsg(db));
        sqlite3_finalize(stmt);
        return -1;
    }

    sqlite3_finalize(stmt);
    return 0;
}

/************************************************
 * Multi-Row Operations
 ************************************************/

int get_all_rows(sqlite3 *db, const char *table, char ****rows, int *row_count, int *col_count) {
    char query[256];
    sqlite3_stmt *stmt;

    snprintf(query, sizeof(query), "SELECT * FROM %s", table);

    if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) != SQLITE_OK) {
        fprintf(stderr, "Failed to prepare statement: %s\n", sqlite3_errmsg(db));
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

int create_table(sqlite3 *db, const char *table_name, const char *columns) {
    char query[1024];
    snprintf(query, sizeof(query), "CREATE TABLE IF NOT EXISTS %s (%s);", table_name, columns);
    return execute_query(db, query);
}

int drop_table(sqlite3 *db, const char *table_name) {
    char query[256];
    snprintf(query, sizeof(query), "DROP TABLE IF EXISTS %s;", table_name);
    return execute_query(db, query);
}

/************************************************
 * Index Management
 ************************************************/

int create_index(sqlite3 *db, const char *index_name, const char *table, const char *column) {
    char query[256];
    snprintf(query, sizeof(query), "CREATE INDEX IF NOT EXISTS %s ON %s(%s);", index_name, table, column);
    return execute_query(db, query);
}

int drop_index(sqlite3 *db, const char *index_name) {
    char query[256];
    snprintf(query, sizeof(query), "DROP INDEX IF EXISTS %s;", index_name);
    return execute_query(db, query);
}

/************************************************
 * Transaction Control
 ************************************************/

int begin_transaction(sqlite3 *db) {
    return execute_query(db, "BEGIN TRANSACTION;");
}

int commit_transaction(sqlite3 *db) {
    return execute_query(db, "COMMIT;");
}

int rollback_transaction(sqlite3 *db) {
    return execute_query(db, "ROLLBACK;");
}

/************************************************
 * Database Maintenance
 ************************************************/

int vacuum_database(sqlite3 *db) {
    return execute_query(db, "VACUUM;");
}

int table_exists(sqlite3 *db, const char *table_name) {
    char query[256];
    sqlite3_stmt *stmt;

    snprintf(query, sizeof(query), "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='%s';", table_name);

    if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) != SQLITE_OK) {
        fprintf(stderr, "Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        return -1;
    }

    int exists = 0;
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        exists = sqlite3_column_int(stmt, 0);
    }

    sqlite3_finalize(stmt);
    return exists;
}