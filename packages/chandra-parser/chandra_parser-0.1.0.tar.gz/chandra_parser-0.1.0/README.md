# Chandra Parser

PDF to Markdown parser using [Datalab's Marker OCR API](https://www.datalab.to) with optional GPT-based figure filtering.

Built by [ReSolve Asset Management](https://investresolve.com) to make financial research more accessible.

## Why We Built This

At ReSolve, we produce extensive research on asset allocation, alternatives, and portfolio construction. We wanted a better way to:

- Convert our PDF research papers into searchable, web-friendly markdown
- Extract clean text for AI/LLM processing and RAG pipelines
- Make our educational content more accessible across devices

We open-sourced this tool so others in the investment community can benefit too.

**Try it on our research:** Download any paper from [Return Stacked ETFs](https://www.returnstackedetfs.com) or [ReSolve Asset Management](https://investresolve.com/research) and parse it with Chandra.

## Features

- **High-quality OCR**: Uses Datalab's Marker API for accurate PDF text extraction
- **Paginated output**: Splits documents into individual page files
- **Page images**: Extracts PDF pages as PNG images at configurable resolution
- **Figure filtering**: Optionally removes logos, decorations, and non-essential images using GPT
- **CLI & library**: Use from command line or import as a Python package

## Installation

```bash
# Using uv (recommended)
uv add chandra-parser

# Using pip
pip install chandra-parser
```

## Quick Start

### Command Line

```bash
# Parse a PDF
chandra parse document.pdf ./output

# Parse without figure filtering
chandra parse document.pdf ./output --no-filter

# Extract just the page images
chandra images document.pdf ./page_images --width 1024
```

### Python API

```python
from chandra_parser import parse_pdf

# Full pipeline
result = parse_pdf(
    "document.pdf",
    "./output",
    filter_figures=True,  # Requires OPENAI_API_KEY
    extract_images=True,
    image_width=712,
)

# Individual functions
from chandra_parser import extract_page_images, filter_pages

extract_page_images("document.pdf", "./images", width=712)
```

## Configuration

Create a `.env` file or set environment variables:

```bash
# Required: Datalab API key
DATALAB_API_KEY=your_key_here

# Optional: For GPT-based figure filtering
OPENAI_API_KEY=your_key_here
```

Get your Datalab API key at [datalab.to](https://www.datalab.to).

## Output Structure

```
output/
├── final.md              # Cleaned, bound markdown (filtered if enabled)
├── output.md             # Raw OCR output
├── response.json         # Full API response
├── images/               # Extracted figures from OCR
├── page_images/          # PDF page renders as PNG
├── pages/                # Individual page markdown files
└── pages_filtered/       # Filtered page markdown (if filtering enabled)
```

## macOS Quick Action (Right-Click to Parse)

Want to parse PDFs with a simple right-click? We have a step-by-step guide to set up a Finder Quick Action — no coding experience required.

**[View the Quick Action Setup Guide →](scripts/README.md)**

Once set up, just right-click any PDF and select "Parse PDF with Chandra". The output folder opens automatically when complete.

## API Reference

### `parse_pdf(file_path, output_dir, **options)`

Main entry point for parsing PDFs.

**Arguments:**
- `file_path`: Path to the PDF file
- `output_dir`: Directory for output files
- `filter_figures`: Use GPT to remove non-essential figures (default: `True`)
- `extract_images`: Extract PDF pages as PNG (default: `True`)
- `image_width`: Width for page images in pixels (default: `712`)
- `verbose`: Print progress messages (default: `True`)

**Returns:** Path to the final markdown file

### `extract_page_images(pdf_path, output_dir, width=712)`

Extract each page of a PDF as a PNG image.

### `filter_pages(input_dir, output_dir, batch_size=10, model="gpt-5-mini")`

Filter non-essential figures from markdown pages using GPT.

## About

Chandra Parser is developed and maintained by [ReSolve Asset Management](https://investresolve.com), a systematic asset manager specializing in risk parity, managed futures, and alternative investment strategies.

**Learn more about our work:**
- [Return Stacked ETFs](https://www.returnstackedetfs.com) - Capital-efficient ETFs that stack return sources
- [ReSolve Research](https://investresolve.com/research) - Free research on portfolio construction and alternatives
- [Gestalt University](https://www.youtube.com/@GestsaltU) - Educational content on YouTube

## License

MIT License - see [LICENSE](LICENSE) for details.
