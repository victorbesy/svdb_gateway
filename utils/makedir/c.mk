CC = gcc
CFLAGS = -fPIC -shared -I../c/include
BIN_DIR = ../../bin
TARGET = $(BIN_DIR)/libsqlite_dpi.so

.PHONY: all clean

all: $(BIN_DIR) $(TARGET)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(TARGET): ../c/src/sqlite_dpi.c
	$(CC) $(CFLAGS) -o $@ $^

clean:
	rm -f $(TARGET)