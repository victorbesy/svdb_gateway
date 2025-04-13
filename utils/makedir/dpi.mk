VERILATOR = verilator
SRCS = ../dpi/src/sqlite_dpi.sv
CFLAGS = -I../dpi/include -L../../bin -lsqlite_dpi

.PHONY: all clean

all:
	$(VERILATOR) --cc $(SRCS) --exe ../dpi/testbench.sv -CFLAGS "$(CFLAGS)"

clean:
	rm -rf ../dpi/obj_dir