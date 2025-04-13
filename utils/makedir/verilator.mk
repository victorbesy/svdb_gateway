VERILATOR = verilator
SRCS = ../dpi/sqlite_dpi.sv
CFLAGS = -I../c/include -L../c/src -lsqlite_dpi

.PHONY: all clean

all:
	$(VERILATOR) --cc $(SRCS) --exe ../dpi/testbench.sv -CFLAGS "$(CFLAGS)"

clean:
    rm -rf ../dpi/obj_dir