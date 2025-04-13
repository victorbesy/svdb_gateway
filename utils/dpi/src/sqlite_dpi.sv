import "DPI-C" function int open_database(input string db_path);
import "DPI-C" function int execute_query(input string query);
import "DPI-C" function void close_database();

module sqlite_dpi_test;
    initial begin
        int db_handle;
        string db_path = "test.db";
        string query = "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);";

        // Open database
        db_handle = open_database(db_path);
        if (db_handle != 0) begin
            $display("Failed to open database");
            $finish;
        end

        // Execute query
        if (execute_query(query) != 0) begin
            $display("Failed to execute query");
        end

        // Close database
        close_database();
        $display("Database operations completed successfully");
    end
endmodule