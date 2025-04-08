#!/bin/bash

# Set up directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXAMPLE_DIR="/media/sf_workspace/svdb_gateway/examples/ip_xact/1685-2014/examples"
TEMP_DIR="/home/v/TEMP"

# Help function
show_help() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -i, --input     Input XML file name (required)"
    echo "  -d, --database  Output database file name (required)"
    echo "  -o, --output    Output XML file name (required)"
    echo "  -h, --help      Show this help message"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--input)
            INPUT_XML="$2"
            shift 2
            ;;
        -d|--database)
            OUTPUT_DB="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_XML="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

# Check if required arguments are provided
if [ -z "${INPUT_XML}" ] || [ -z "${OUTPUT_DB}" ] || [ -z "${OUTPUT_XML}" ]; then
    echo "Error: Missing required arguments"
    show_help
fi

# Create TEMP directory if it doesn't exist
mkdir -p "${TEMP_DIR}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ...existing code for print_status function...

# Display script start
echo "Starting IP-XACT conversion process..."
echo "Input XML:  ${INPUT_XML}"
echo "Database:   ${OUTPUT_DB}"
echo "Output XML: ${OUTPUT_XML}"

# Step 1: XML to SQLite
echo -e "\n1. Converting XML to SQLite..."
python3 "${SCRIPT_DIR}/xml2sql.py" \
    -i "${EXAMPLE_DIR}/${INPUT_XML}" \
    -d "${TEMP_DIR}"
print_status $? "XML to SQLite conversion"

# Step 2: SQLite to XML
echo -e "\n2. Converting SQLite back to XML..."
python3 "${SCRIPT_DIR}/sql2xml.py" \
    -i "${TEMP_DIR}/${OUTPUT_DB}" \
    -o "${TEMP_DIR}/${OUTPUT_XML}"
print_status $? "SQLite to XML conversion"

# ...existing code for file comparison...

# Display file locations
echo -e "\nFile locations:"
echo "Original XML: ${EXAMPLE_DIR}/${INPUT_XML}"
echo "SQLite DB:   ${TEMP_DIR}/${OUTPUT_DB}"
echo "New XML:     ${TEMP_DIR}/${OUTPUT_XML}"