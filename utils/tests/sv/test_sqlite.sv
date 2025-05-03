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
         $display("Successfully opened SQLite database: %s", db_name);
         sqlite_dpi_close_database(SqliteDB);
      end else begin
         $display("Failed to open SQLite database: %s", db_name);
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
         $display("Successfully opened SQLite database: %s", db_name);
      end else begin
         $display("Failed to open SQLite database: %s", db_name);
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
         $display("Successfully closed SQLite database");
      end else begin
         $display("No valid SQLite database handle to close");
      end

      end_of_test(success, test_name);
      return Pass;
   endfunction

   //Utils functions
   // Update test counts based on test result
   function automatic bit update_test_counts(input bit success);
      if (success) begin
         PassCount++;
      end else begin
         FailCount++;
      end
      Pass = Pass && success;
      return Pass;
   endfunction

   // Report test results
   function automatic void end_of_test(input bit success, input string test_name);
      bit updated_pass;
      if (success) begin
         $display("PASS: %s @%0t", test_name, $time);
      end else begin
         $display("FAIL: %s @%0t", test_name, $time);
      end

      // Update the test counts
      updated_pass = update_test_counts(success);
      Pass = updated_pass;
   endfunction

endmodule: test_sqlite
/* verilator lint_on UNUSED */
/* verilator lint_on UNDRIVEN */
/* verilator lint_on VARHIDDEN */
