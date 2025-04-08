#!/bin/bash

# Set up directories and variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXAMPLE_DIR="/media/sf_workspace/svdb_gateway/examples/run_dir"
TEMP_DIR="/home/v/TEMP"
INPUT_XML="ahbstatMaster.xml"
OUTPUT_DB="ahbstatMaster.db"
OUTPUT_XML="restored_ahbstatMaster.xml"

# Create TEMP directory if it doesn't exist
mkdir -p "${TEMP_DIR}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}[SUCCESS]${NC} $2"
    else
        echo -e "${RED}[FAILED]${NC} $2"
        exit 1
    fi
}

# Display script start
echo "Starting IP-XACT conversion process..."

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

# Step 3: Compare files
echo -e "\n3. Comparing original and restored XML files (ignoring comments)..."

# Normalize the original XML
xmllint --format --nocdata "${EXAMPLE_DIR}/${INPUT_XML}" > "${TEMP_DIR}/original_normalized.xml"

# Normalize the restored XML
xmllint --format --nocdata "${TEMP_DIR}/${OUTPUT_XML}" > "${TEMP_DIR}/restored_normalized.xml"

# Remove comments from the normalized files
# Remove comments from the normalized files
grep -v '^[[:space:]]*<!--' "${TEMP_DIR}/original_normalized.xml" > "${TEMP_DIR}/original_no_comments.xml"
grep -v '^[[:space:]]*<!--' "${TEMP_DIR}/restored_normalized.xml" > "${TEMP_DIR}/restored_no_comments.xml"

# Compare the files without comments
diff "${TEMP_DIR}/original_no_comments.xml" "${TEMP_DIR}/restored_no_comments.xml"
DIFF_STATUS=$?

if [ $DIFF_STATUS -eq 0 ]; then
    echo -e "${GREEN}[SUCCESS]${NC} Files are identical (ignoring comments)"
else
    echo -e "${RED}[WARNING]${NC} Files have differences (ignoring comments)"
fi

# Display file locations
echo -e "\nFile locations:"
echo "Original XML: ${EXAMPLE_DIR}/${INPUT_XML}"
echo "SQLite DB:   ${TEMP_DIR}/${OUTPUT_DB}"
echo "New XML:     ${TEMP_DIR}/${OUTPUT_XML}"

