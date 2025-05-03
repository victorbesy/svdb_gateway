# SVDB Gateway

SQLite Database Gateway for SystemVerilog

## Overview

SVDB Gateway provides a bridge between SystemVerilog and SQLite databases, allowing SystemVerilog code to interact with SQLite databases through a Direct Programming Interface (DPI).

## Project Structure

```
svdb_gateway/
├── bin/                  # Compiled binaries
├── utils/
│   ├── c/                # C utilities
│   │   ├── include/      # C header files
│   │   │   └── icecream-c/   # C debugging library
│   │   └── src/          # C source files
│   ├── dpi/              # DPI interface
│   │   ├── include/      # DPI header files
│   │   │   └── icecream_sv/  # SystemVerilog debugging library
│   │   └── src/          # DPI source files
│   ├── makedir/          # Build system
│   ├── py/               # Python utilities
│   └── tests/            # Test cases
│       └── systemverilog/   # SystemVerilog tests
└── README.md             # This file
```

## Features

- SQLite database operations from SystemVerilog
- Complete DPI bridge for database operations
- Enhanced debugging with icecream libraries

## Requirements

- C/C++ compiler (GCC recommended)
- SQLite development libraries
- For testing SystemVerilog code:
  - Verilator (see [installation instructions](utils/tests/systemverilog/INSTALL_VERILATOR.md))
  - Make

## Building

To build the project:

```bash
cd utils/makedir
make
```

## Running Tests

To run the SystemVerilog tests with Verilator:

```bash
cd utils/tests/systemverilog
./run_verilator_test.sh  # On Linux/Unix
run_verilator_test.bat   # On Windows
```

## Debugging

The project integrates two powerful debugging libraries:

### IceCream for SystemVerilog

[icecream_sv](https://github.com/xver/icecream_sv) provides easy debugging for SystemVerilog:

```systemverilog
import icecream_pkg::*;

// Simple debug print with location information
`IC;

// Print variables with values
`IC_STR(my_string);
`IC_DEC(my_int);
`IC_HEX(my_hex);
`IC_ARR(my_array);
```

### IceCream for C

[icecream-c](https://github.com/chunqian/icecream-c) provides intuitive debugging for C code:

```c
#include "icecream.h"

// Simple debug print with location information
ic();

// Print variables with types
ic_str(my_string, another_string);
ic_int(my_int, another_int);
ic_ptr(my_pointer);
```

## License

Released under the MIT License. See LICENSE file for details.
