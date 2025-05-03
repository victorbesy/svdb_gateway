/* verilator lint_off UNUSED */
/* verilator lint_off UNDRIVEN */
/* verilator lint_off VARHIDDEN */

module test_sqlite (input reg clk_i);

   //logic clk_i;
   import sqlite_dpi_pkg::*;

   bit Pass;
   chandle SqliteDB;
   int PassCount;
   int FailCount;


   initial begin
      string Status;
      string Test_name;

      Pass = 1'b1; // Start with Pass = 1 (all tests passing)
      PassCount = 0;
      FailCount = 0;

      $display("SQLite Tests: START");

      // Execute basic sqlite test
      Test_name = "Basic_sqlite_test";
      Pass = basic_sqlite_test(Test_name);

      // Test opening SQLite database
      Test_name = "Open SQLite DB test";
      Pass = open_sqlite_test(Test_name);

      // Test table operations
      Test_name = "Table Schema Operations test";
      Pass = table_schema_test(Test_name);

      Test_name = "Table Row Operations test";
      Pass = table_row_operations_test(Test_name);

      // Test closing SQLite database
      Test_name = "Close SQLite DB test";
      Pass = close_sqlite_test(Test_name);

      // Final test result
      if (Pass) begin
         $display("OVERALL TEST RESULT: PASS @%0t", $time);
      end else begin
         $display("OVERALL TEST RESULT: FAIL @%0t", $time);
      end
      $display("Tests Passed: %0d, Tests Failed: %0d, Total: %0d", PassCount, FailCount, PassCount + FailCount);

      $finish;
   end

   //Test functions
   // Basic SQLite test function
   function automatic bit basic_sqlite_test(input string test_name);
      bit success = 1'b1;
      string db_name = "test.db";  // Changed to local file
      SqliteDB = sqlite_dpi_open_database(db_name);
      if (SqliteDB != null) begin
         $display("PASS: Opened SQLite database '%s' for basic test", db_name);
         sqlite_dpi_close_database(SqliteDB);
         $display("PASS: Closed SQLite database '%s' after basic test", db_name);
      end else begin
         $display("ERROR: Could not open SQLite database '%s' for basic test", db_name);
         success = 1'b0;
      end
      end_of_test(success, test_name);
      return Pass;
   endfunction

   // Open SQLite database test function
   function automatic bit open_sqlite_test(input string test_name);
      bit success = 1'b1;
      string db_name = "test.db";

      // Try to open the SQLite database
      SqliteDB = sqlite_dpi_open_database(db_name);

      if (SqliteDB != null) begin
         $display("PASS: Opened SQLite database '%s' with handle %0d", db_name, SqliteDB);
      end else begin
         $display("ERROR: Could not open SQLite database '%s'", db_name);
         success = 1'b0;
      end

      end_of_test(success, test_name);
      return Pass;
   endfunction

   // Close SQLite database test function
   function automatic bit close_sqlite_test(input string test_name);
      bit success = 1'b0;

      // Try to close the SQLite database
      if (SqliteDB != null) begin
         sqlite_dpi_close_database(SqliteDB);
         success = 1'b1;
         $display("PASS: Closed SQLite database with handle %0d", SqliteDB);
         SqliteDB = null;
      end else begin
         $display("ERROR: Cannot close SQLite database - handle is null");
      end

      end_of_test(success, test_name);
      return Pass;
   endfunction

   // Table schema test function
   function automatic bit table_schema_test(input string test_name);
      bit success = 1'b1;
      string table_name = "test_table";
      string columns = "id INTEGER PRIMARY KEY, name TEXT, value INTEGER";

      // Create table
      if (sqlite_dpi_write_schema(SqliteDB, table_name, columns) == 0) begin
         $display("PASS: Created table '%s' with columns: %s", table_name, columns);
      end else begin
         $display("ERROR: Could not create table '%s'", table_name);
         success = 1'b0;
      end

      // Check if table exists
      if (sqlite_dpi_table_exists(SqliteDB, table_name) > 0) begin
         $display("PASS: Verified table '%s' exists", table_name);
      end else begin
         $display("ERROR: Table '%s' does not exist", table_name);
         success = 1'b0;
      end

      // Read schema
      $display("\nReading database schema:");
      if (sqlite_dpi_read_schema(SqliteDB) == 0) begin
         $display("PASS: Successfully read schema for table '%s'", table_name);
         // Print table details
         $display("\nTable Details:");
         $display("  Table Name: %s", table_name);
         $display("  Columns:");
         $display("    - id INTEGER PRIMARY KEY");
         $display("    - name TEXT");
         $display("    - value INTEGER");
      end else begin
         $display("ERROR: Could not read schema for table '%s'", table_name);
         success = 1'b0;
      end

      end_of_test(success, test_name);
      return Pass;
   endfunction

   // Table row operations test function
   function automatic bit table_row_operations_test(input string test_name);
      bit success = 1'b1;
      string table_name = "test_table";
      string columns = "name, value";
      string values = "'test_name', 42";
      int row_id;

      // Begin transaction
      if (sqlite_dpi_begin_transaction(SqliteDB) != 0) begin
         $display("ERROR: Could not begin transaction");
         success = 1'b0;
         return success;
      end

      // Print initial table contents
      $display("Initial table contents:");
      if (sqlite_dpi_execute_query(SqliteDB, {"SELECT * FROM ", table_name}) == 0) begin
         $display("PASS: Retrieved initial table contents");
      end else begin
         $display("ERROR: Could not retrieve initial table contents");
         success = 1'b0;
      end

      // Insert row
      row_id = sqlite_dpi_insert_row(SqliteDB, table_name, columns, values);
      if (row_id > 0) begin
         $display("PASS: Inserted row with ID %0d into table '%s'", row_id, table_name);
         $display("  Columns: %s", columns);
         $display("  Values: %s", values);
      end else begin
         $display("ERROR: Could not insert row into table '%s'", table_name);
         success = 1'b0;
      end

      // Print table contents after insert
      $display("\nTable contents after insert:");
      if (sqlite_dpi_execute_query(SqliteDB, {"SELECT * FROM ", table_name}) == 0) begin
         $display("PASS: Retrieved table contents after insert");
      end else begin
         $display("ERROR: Could not retrieve table contents after insert");
         success = 1'b0;
      end

      // Get row
      if (sqlite_dpi_get_row(SqliteDB, table_name, row_id) == 0) begin
         $display("PASS: Retrieved row %0d from table '%s'", row_id, table_name);
      end else begin
         $display("ERROR: Could not retrieve row %0d from table '%s'", row_id, table_name);
         success = 1'b0;
      end

      // Delete row
      if (sqlite_dpi_delete_row(SqliteDB, table_name, row_id) == 0) begin
         $display("PASS: Deleted row %0d from table '%s'", row_id, table_name);
      end else begin
         $display("ERROR: Could not delete row %0d from table '%s'", row_id, table_name);
         $display("  Attempting to rollback transaction...");
         if (sqlite_dpi_rollback_transaction(SqliteDB) == 0) begin
            $display("  PASS: Successfully rolled back transaction");
         end else begin
            $display("  ERROR: Failed to rollback transaction");
         end
         success = 1'b0;
         return success;
      end

      // Commit transaction
      if (sqlite_dpi_commit_transaction(SqliteDB) == 0) begin
         $display("PASS: Successfully committed transaction");
      end else begin
         $display("ERROR: Failed to commit transaction");
         success = 1'b0;
      end

      end_of_test(success, test_name);
      return Pass;
   endfunction

   // End of test function
   function automatic void end_of_test(input bit success, input string test_name);
      if (success) begin
         $display("PASS: %s @%0t", test_name, $time);
         PassCount++;
      end else begin
         $display("FAIL: %s @%0t", test_name, $time);
         FailCount++;
         Pass = 1'b0;
      end
   endfunction

endmodule
/* verilator lint_on UNUSED */
/* verilator lint_on UNDRIVEN */
/* verilator lint_on VARHIDDEN */
