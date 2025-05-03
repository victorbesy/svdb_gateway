# Makefile
VERILATOR = verilator
VERILATOR_FLAGS = -Wall --trace
SIM_MAIN = sim_main.cpp
TOP_MODULE = Vcs_common
OUTPUT_DIR = .

# Set default SVDB_HOME if not already set
ifeq (${SVDB_HOME},)
    SVDB_HOME := $(shell cd ../../.. && pwd)
endif

COMPILATION_LOG_FILE = verilator_comp.log
TEST_LOG_FILE = verilator_test.log
LIBDBDPI_PATH = ${SVDB_HOME}/bin/libdbdpi.so
SVDB_VERILATOR_FLAG = -CFLAGS "-I${SVDB_HOME}/utils/dpi/include" \
                      -CFLAGS "-I${SVDB_HOME}/utils/c/include" \
                      -cc \
                      ${SVDB_HOME}/utils/dpi/src/sqlite_dpi_pkg.sv \
                      -LDFLAGS "${SVDB_HOME}/bin/libdbdpi.so"
MAKE_SVDB = ../../makedir


ifeq (${VERILATOR},)
export VERILATOR = verilator
endif

.PHONY: all clean run svdb_compile compile_verilator_sv help

# Default target
all:
	@echo "Starting all target..."
	$(MAKE) clean && \
	$(MAKE) svdb_compile && \
	$(MAKE) compile_verilator_sv && \
	$(MAKE) run && \
	echo "Completed all target."

# Display help information
help:
	@echo "SVDB Gateway Makefile Help"
	@echo "=========================="
	@echo "Available targets:"
	@echo "  all                 : Default target. Cleans, compiles SVDB libraries, compiles Verilator code, and runs simulation"
	@echo "  svdb_compile        : Compiles the SVDB C libraries"
	@echo "  compile_verilator_sv: Compiles SystemVerilog code with Verilator"
	@echo "  run                 : Runs the simulation"
	@echo "  clean               : Removes all generated files and directories"
	@echo "  help                : Displays this help message"

	@echo ""
	@echo "Configuration variables:"
	@echo "  OUTPUT_DIR         : Directory for output files (default: .)"
	@echo "  VERILATOR          : Path to Verilator executable (default: verilator)"
	@echo "  MAKE_SVDB          : Path to SVDB makedir (default: ../../makedir)"
	@echo "  LIBDBDPI_PATH      : Path to libdbdpi.so library (default: \${SVDB_HOME}/bin/libdbdpi.so)"
	@echo "  SVDB_HOME          : Path to svdb_gateway root directory (default: automatically detected)"
	@echo ""
	@echo "Example usage:"
	@echo "  make               : Run all targets"
	@echo "  make OUTPUT_DIR=./output : Run all targets with custom output directory"
	@echo "  make help          : Show this help"

svdb_compile:
	@echo "Starting svdb_compile target..."
	@echo "Compiling SVDB C libraries..." > $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE)
	$(MAKE) -C $(MAKE_SVDB) -f c.mk all >> $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE) 2>&1 || { cat $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE); exit 1; }
	@echo "SVDB C libraries compilation complete." >> $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE)
	@cat $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE)
	@echo "Completed svdb_compile target."

compile_verilator_sv:
	@echo "Starting compile_verilator_sv target..."
	@mkdir -p $(OUTPUT_DIR)
	@echo "Compiling with Verilator..." > $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE)
	${VERILATOR} $(VERILATOR_FLAGS) cs_common.svh $(SVDB_VERILATOR_FLAG) test_sqlite.sv --exe $(SIM_MAIN) --Mdir $(OUTPUT_DIR)/obj_dir --trace >> $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE) 2>&1 || { cat $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE); exit 1; }
	@echo "Command: make -C $(OUTPUT_DIR)/obj_dir -j -f Vcs_common.mk Vcs_common" >> $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE)
	@if [ -d "$(OUTPUT_DIR)/obj_dir" ]; then \
		make -C $(OUTPUT_DIR)/obj_dir -j -f Vcs_common.mk Vcs_common >> $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE) 2>&1 || { cat $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE); exit 1; }; \
	else \
		echo "Error: obj_dir not created, Verilator compilation failed" >> $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE); \
		cat $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE); \
		exit 1; \
	fi
	@echo "Compilation complete. Compilation log file generated: $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE)" >> $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE)
	@cat $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE)
	@echo "Completed compile_verilator_sv target."

run:
	@echo "Starting run target..."
	@echo "Running simulation..." > $(OUTPUT_DIR)/$(TEST_LOG_FILE)
	@echo "Command: $(OUTPUT_DIR)/obj_dir/$(TOP_MODULE)" >> $(OUTPUT_DIR)/$(TEST_LOG_FILE)
	@if [ -x "$(OUTPUT_DIR)/obj_dir/$(TOP_MODULE)" ]; then \
		$(OUTPUT_DIR)/obj_dir/$(TOP_MODULE) >> $(OUTPUT_DIR)/$(TEST_LOG_FILE) 2>&1 || { cat $(OUTPUT_DIR)/$(TEST_LOG_FILE); exit 1; }; \
	else \
		echo "Error: Executable $(OUTPUT_DIR)/obj_dir/$(TOP_MODULE) not found or not executable" >> $(OUTPUT_DIR)/$(TEST_LOG_FILE); \
		cat $(OUTPUT_DIR)/$(TEST_LOG_FILE); \
		exit 1; \
	fi
	@echo "Simulation complete. Test log file generated: $(OUTPUT_DIR)/$(TEST_LOG_FILE)" >> $(OUTPUT_DIR)/$(TEST_LOG_FILE)
	@cat $(OUTPUT_DIR)/$(TEST_LOG_FILE)
	@echo "Completed run target."

clean:
	@echo "Starting clean target..."
	rm -rf $(OUTPUT_DIR)/obj_dir
	rm -f $(OUTPUT_DIR)/$(COMPILATION_LOG_FILE) $(OUTPUT_DIR)/$(TEST_LOG_FILE)
	$(MAKE) -C $(MAKE_SVDB) -f c.mk clean
	@echo "Completed clean target."
 
