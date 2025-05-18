# IP-XACT 1685-2014 Example: How to Run

This directory contains a set of IP-XACT 1685-2014 XML files and demonstrates how to process them using the provided Python scripts in `svdb_gateway/utils/py`.

## Prerequisites
- Python 3.x
- The following Python packages (install with `pip install` if needed):
  - argparse
  - sqlite3
  - xml.etree.ElementTree
  - pathlib
  - xml.dom.minidom

## Files
- `xml_file_list.txt`: List of XML files to process (absolute paths).
- XML files: IP-XACT design and component files.

# System Address Map for FutureSystemMap

This document lists the system-level address assignments for each block instance in the IP-XACT design `FutureSystemMap`. This approach is fully compliant with the IEEE 1685-2014 (IP-XACT) standard, which does not encode system addresses directly in the XML files.

| Instance   | Component | System Base Address |
|------------|-----------|--------------------|
| BlockA_1   | BlockA    | 0x0000             |
| BlockB     | BlockB    | 0x2000             |
| BlockC     | BlockC    | 0x3000             |
| BlockD     | BlockD    | 0x6000             |
| BlockA_2   | BlockA    | 0x8000             |

.
## Steps

All commands below should be run from this directory (`svdb_gateway/examples/ip_xact/1685-2014`).

### 1. Convert XML files to SQLite database

```
python3 ../../../../utils/py/xml_to_sqlite.py xml_file_list.txt -o ../../../bin
```
- This will create `ipxact.db` in the `svdb_gateway/bin` directory.

### 2. Convert SQLite database back to XML files

```
python3 ../../../../utils/py/sqlite_to_xml.py ../../../bin/ipxact.db ../../../bin/xml_result/
```
- This will create XML files in the `svdb_gateway/bin/xml_result/` directory.

### 3. Verify equivalence of original and generated XML files (optional)

```
python3 ../../../../utils/py/verify_xml_equivalence.py xml_file_list.txt ../../../bin/xml_result/
```
- This will print `OK: filename.xml` for each file that matches, or `DIFFER`/`MISSING` if there are differences or missing files.

## Notes
- The scripts expect absolute paths in `xml_file_list.txt`.
- The database schema is defined in `../../../../utils/py/schema.txt`.
- You can modify the output directory as needed, but for this example, use `svdb_gateway/bin` and `svdb_gateway/bin/xml_result` as shown above.
- For more details, see the script source code in `../../../../utils/py/`.