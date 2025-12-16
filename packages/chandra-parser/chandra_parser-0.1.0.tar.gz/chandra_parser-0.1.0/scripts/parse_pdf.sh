#!/bin/bash
# Parse PDF using Chandra parser
# Usage: ./parse_pdf.sh /path/to/document.pdf

set -e

# Configuration - default assumes installation in ~/Documents/chandra-parser
# Change this path if you installed Chandra Parser elsewhere
CHANDRA_DIR="${CHANDRA_DIR:-$HOME/Documents/chandra-parser}"

# Load environment variables from .env file
if [ -f "$CHANDRA_DIR/.env" ]; then
    export $(grep -v '^#' "$CHANDRA_DIR/.env" | xargs)
fi

# Get input PDF path
PDF_PATH="$1"

if [ -z "$PDF_PATH" ]; then
    echo "Usage: $0 <pdf_path>"
    exit 1
fi

if [ ! -f "$PDF_PATH" ]; then
    echo "Error: File not found: $PDF_PATH"
    exit 1
fi

# Get PDF filename without extension for output directory
PDF_NAME=$(basename "$PDF_PATH" .pdf)
PDF_DIR=$(dirname "$PDF_PATH")
OUTPUT_DIR="$PDF_DIR/${PDF_NAME}_parsed"

# Show notification on macOS
notify() {
    if command -v osascript &> /dev/null; then
        osascript -e "display notification \"$1\" with title \"Chandra Parser\" sound name \"$2\""
    else
        echo "$1"
    fi
}

notify "Processing: $PDF_NAME" "Submarine"

# Run the parser
cd "$CHANDRA_DIR"

if command -v uv &> /dev/null; then
    uv run chandra parse "$PDF_PATH" "$OUTPUT_DIR"
else
    python -m chandra_parser.cli parse "$PDF_PATH" "$OUTPUT_DIR"
fi

# Check if successful
if [ -f "$OUTPUT_DIR/final.md" ]; then
    notify "Complete! Output: ${PDF_NAME}_parsed/" "Glass"
    # Open the output folder on macOS
    if command -v open &> /dev/null; then
        open "$OUTPUT_DIR"
    fi
else
    notify "Failed - check output" "Basso"
    exit 1
fi
