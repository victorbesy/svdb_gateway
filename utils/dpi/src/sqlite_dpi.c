#include "sqlite_dpi.h"
#include <string.h>
#include <stdlib.h>

/************************************************
 * Connection Management
 ************************************************/

sqlite3 *sqlite_dpi_open_database(const char *db_path) {
    // ic();
    // ic_str(db_path);
    sqlite3 *db = sqlite_prim_open_database(db_path);
    return db;
}

void sqlite_dpi_close_database(sqlite3 *db) {
    // ic();
    sqlite_prim_close_database(db);
}

int sqlite_dpi_execute_query(sqlite3 *db, const char *query) {
    // ic();
    // ic_str(query);
    int result = sqlite_prim_execute_query(db, query);
    // ic_int(result);
    return result;
}

/************************************************
 * Table Operations
 ************************************************/

int sqlite_dpi_read_schema(sqlite3 *db) {
    // ic();
    int result = sqlite_prim_read_table_schema(db);
    // ic_int(result);
    return result;
}

int sqlite_dpi_write_schema(sqlite3 *db, const char *table_name, const char *columns) {
    // ic();
    // ic_str(table_name, columns);
    int result = sqlite_prim_create_table(db, table_name, columns);
    // ic_int(result);
    return result;
}

int sqlite_dpi_table_exists(sqlite3 *db, const char *table_name) {
    // ic();
    // ic_str(table_name);
    int result = sqlite_prim_table_exists(db, table_name);
    // ic_int(result);
    return result;
}

int sqlite_dpi_insert_row(sqlite3 *db, const char *table_name, const char *columns_str, const char *values_str) {
    // ic();
    // ic_str(table_name, columns_str, values_str);

    // Parse comma-separated columns string
    char **columns = NULL;
    int col_count = 0;
    char *columns_copy = strdup(columns_str);
    char *token = strtok(columns_copy, ",");

    while (token != NULL) {
        columns = realloc(columns, sizeof(char*) * (col_count + 1));
        columns[col_count] = strdup(token);
        col_count++;
        token = strtok(NULL, ",");
    }
    free(columns_copy);

    // Parse comma-separated values string
    char **values = NULL;
    char *values_copy = strdup(values_str);
    token = strtok(values_copy, ",");
    int val_count = 0;

    while (token != NULL) {
        values = realloc(values, sizeof(char*) * (val_count + 1));
        values[val_count] = strdup(token);
        val_count++;
        token = strtok(NULL, ",");
    }
    free(values_copy);

    // Verify counts match
    if (col_count != val_count) {
        // ic_error("Column count (%d) and value count (%d) don't match", col_count, val_count);
        // Clean up
        for (int i = 0; i < col_count; i++) {
            free(columns[i]);
        }
        free(columns);

        for (int i = 0; i < val_count; i++) {
            free(values[i]);
        }
        free(values);

        return -1;
    }

    int result = sqlite_prim_insert_row(db, table_name, (const char **)columns, (const char **)values, col_count);
    // ic_int(result);

    // Clean up
    for (int i = 0; i < col_count; i++) {
        free(columns[i]);
    }
    free(columns);

    for (int i = 0; i < val_count; i++) {
        free(values[i]);
    }
    free(values);

    return result;
}

int sqlite_dpi_delete_row(sqlite3 *db, const char *table_name, int row_id) {
    // ic();
    // ic_str(table_name);
    // ic_int(row_id);
    int result = sqlite_prim_delete_row(db, table_name, row_id);
    // ic_int(result);
    return result;
}

int sqlite_dpi_get_row(sqlite3 *db, const char *table_name, int row_id) {
    // ic();
    // ic_str(table_name);
    // ic_int(row_id);

    char **columns = NULL;
    char **values = NULL;
    int col_count = 0;

    int result = sqlite_prim_get_row(db, table_name, row_id, &columns, &values, &col_count);
    // ic_int(result);

    // Here we would need to handle returning the data to SystemVerilog
    // For now, just print the values and free memory
    if (result == 0) {
        for (int i = 0; i < col_count; i++) {
            // ic_msg("Column %s = %s", columns[i], values[i]);
            free(columns[i]);
            free(values[i]);
        }
        free(columns);
        free(values);
    }

    return result;
}

int sqlite_dpi_begin_transaction(sqlite3 *db) {
    // ic();
    int result = sqlite_prim_begin_transaction(db);
    // ic_int(result);
    return result;
}

int sqlite_dpi_commit_transaction(sqlite3 *db) {
    // ic();
    int result = sqlite_prim_commit_transaction(db);
    // ic_int(result);
    return result;
}

int sqlite_dpi_rollback_transaction(sqlite3 *db) {
    // ic();
    int result = sqlite_prim_rollback_transaction(db);
    // ic_int(result);
    return result;
}

int sqlite_dpi_vacuum_database(sqlite3 *db) {
    // ic();
    int result = sqlite_prim_vacuum_database(db);
    // ic_int(result);
    return result;
}