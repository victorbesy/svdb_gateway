#!/bin/bash

# Set up directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
XML_DIR="/media/sf_workspace/svdb_gateway/examples/Leon2_1685-2022/Leon2/spiritconsortium.org/Leon2RTL/ahbstat/1.2"
OUTPUT_DIR="/home/v/TEMP"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create output directory if it doesn't exist
mkdir -p "${OUTPUT_DIR}"

# Process each XML file
echo "Starting IP-XACT batch conversion process..."
echo "Source directory: ${XML_DIR}"
echo "Output directory: ${OUTPUT_DIR}"
echo -e "----------------------------------------\n"

for xml_file in "${XML_DIR}"/*.xml; do
    if [ -f "$xml_file" ]; then
        # Extract filename without path and extension
        filename=$(basename "$xml_file" .xml)
        echo -e "\nProcessing: ${filename}.xml"
        
        # Run the conversion script
        "${SCRIPT_DIR}/run.sh" \
            -i "${filename}.xml" \
            -d "${filename}.db" \
            -o "${filename}_restored.xml"
        
        # Check if run.sh succeeded
        if [ $? -ne 0 ]; then
            echo -e "${RED}[ERROR]${NC} Failed to process ${filename}.xml"
            echo "Stopping batch process due to error."
            exit 1
        else
            echo -e "${GREEN}[SUCCESS]${NC} Processed ${filename}.xml"
        fi
    fi
done

echo -e "\n----------------------------------------"
echo "Batch processing completed successfully."
exit 0