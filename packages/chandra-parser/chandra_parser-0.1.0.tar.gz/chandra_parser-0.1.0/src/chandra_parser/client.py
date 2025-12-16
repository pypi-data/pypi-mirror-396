"""Core client for Datalab's Marker OCR API."""

from __future__ import annotations

import base64
import json
import os
import re
import time
from pathlib import Path
from typing import TYPE_CHECKING

import fitz  # pymupdf
import httpx

if TYPE_CHECKING:
    from typing import Any

API_BASE = "https://www.datalab.to/api/v1"


def get_api_key() -> str:
    """Get the Datalab API key from environment."""
    key = os.getenv("DATALAB_API_KEY") or os.getenv("CHANDRA_API_KEY")
    if not key:
        raise ValueError(
            "API key not found. Set DATALAB_API_KEY or CHANDRA_API_KEY environment variable."
        )
    return key


def submit_document(
    file_path: str | Path,
    output_format: str = "markdown",
    mode: str = "accurate",
    extras: str | None = None,
) -> dict[str, Any]:
    """Submit a document for OCR processing.

    Args:
        file_path: Path to the PDF or image file.
        output_format: Output format ('markdown', 'html', 'json', 'text').
        mode: Processing mode ('fast' or 'accurate').
        extras: Comma-separated extra features (e.g., 'chart_understanding').

    Returns:
        API response with request_id and request_check_url.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    api_key = get_api_key()
    mime_type = "application/pdf" if path.suffix.lower() == ".pdf" else "image/png"

    with open(path, "rb") as f:
        files = {"file": (path.name, f, mime_type)}
        data = {
            "output_format": output_format,
            "mode": mode,
            "force_ocr": "true",
            "paginate": "true",
        }
        if extras:
            data["extras"] = extras

        response = httpx.post(
            f"{API_BASE}/marker",
            files=files,
            data=data,
            headers={"X-Api-Key": api_key},
            timeout=60.0,
        )
        response.raise_for_status()

    return response.json()


def poll_result(
    check_url: str,
    max_wait: int = 300,
    poll_interval: int = 2,
    verbose: bool = True,
) -> dict[str, Any]:
    """Poll for OCR results until complete or timeout.

    Args:
        check_url: URL to poll for results.
        max_wait: Maximum wait time in seconds.
        poll_interval: Seconds between polls.
        verbose: Print status updates.

    Returns:
        Complete API response with OCR results.
    """
    api_key = get_api_key()
    start = time.time()

    while time.time() - start < max_wait:
        response = httpx.get(
            check_url,
            headers={"X-Api-Key": api_key},
            timeout=30.0,
        )
        response.raise_for_status()
        result = response.json()

        status = result.get("status")
        if status == "complete":
            return result
        elif status == "failed":
            raise RuntimeError(f"Processing failed: {result.get('error', 'Unknown error')}")

        if verbose:
            print(f"  Status: {status}... waiting")
        time.sleep(poll_interval)

    raise TimeoutError(f"Processing did not complete within {max_wait} seconds")


def split_pages(markdown: str) -> list[tuple[int, str]]:
    """Split paginated markdown into (page_num, content) tuples.

    The Datalab API uses markers like {0}------------------------------------------------
    to separate pages when paginate=true.
    """
    pattern = r"\n*\{(\d+)\}-{48}\n*"
    parts = re.split(pattern, markdown)

    pages = []
    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            page_num = int(parts[i])
            content = parts[i + 1].strip()
            if content:
                pages.append((page_num, content))

    return pages


def extract_page_images(
    pdf_path: str | Path,
    output_dir: str | Path,
    width: int = 712,
) -> int:
    """Extract each page of a PDF as a PNG image.

    Args:
        pdf_path: Path to the PDF file.
        output_dir: Directory to save page images.
        width: Target width in pixels (height scales proportionally).

    Returns:
        Number of pages extracted.
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        zoom = width / page.rect.width
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        output_file = output_dir / f"page_{page_num:03d}.png"
        pix.save(output_file)

    num_pages = len(doc)
    doc.close()
    return num_pages


def bind_pages(pages_dir: str | Path, output_file: str | Path) -> int:
    """Combine page markdown files into a single document.

    Args:
        pages_dir: Directory containing page_*.md files.
        output_file: Output file path.

    Returns:
        Number of pages bound.
    """
    pages_dir = Path(pages_dir)
    output_file = Path(output_file)

    page_files = sorted(pages_dir.glob("page_*.md"))
    contents = []

    for page_file in page_files:
        content = page_file.read_text().strip()
        if content:
            contents.append(content)

    combined = "\n\n---\n\n".join(contents)
    output_file.write_text(combined)
    return len(contents)


def save_result(result: dict[str, Any], output_dir: str | Path, verbose: bool = True) -> None:
    """Save OCR results to disk.

    Creates:
        - output.md: Full markdown output
        - pages/: Individual page markdown files
        - response.json: Complete API response
        - images/: Extracted figure images

    Args:
        result: API response dictionary.
        output_dir: Output directory path.
        verbose: Print progress messages.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save full markdown
    markdown = result.get("markdown", "")
    if markdown:
        (output_dir / "output.md").write_text(markdown)
        if verbose:
            print(f"  Saved: {output_dir}/output.md")

        # Split into pages
        pages = split_pages(markdown)
        if len(pages) > 1:
            pages_dir = output_dir / "pages"
            pages_dir.mkdir(exist_ok=True)
            for page_num, content in pages:
                (pages_dir / f"page_{page_num:03d}.md").write_text(content)
            if verbose:
                print(f"  Saved: {output_dir}/pages/ ({len(pages)} pages)")

    # Save JSON response
    (output_dir / "response.json").write_text(json.dumps(result, indent=2))
    if verbose:
        print(f"  Saved: {output_dir}/response.json")

    # Save images
    images = result.get("images", {})
    if images:
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)
        for filename, b64_data in images.items():
            image_bytes = base64.b64decode(b64_data)
            (images_dir / filename).write_bytes(image_bytes)
        if verbose:
            print(f"  Saved: {output_dir}/images/ ({len(images)} images)")

    if verbose:
        print(f"\nSummary:")
        print(f"  Pages: {result.get('page_count', 'unknown')}")
        print(f"  Images: {len(images)}")


def parse_pdf(
    file_path: str | Path,
    output_dir: str | Path,
    filter_figures: bool = True,
    extract_images: bool = True,
    image_width: int = 712,
    verbose: bool = True,
) -> Path:
    """Parse a PDF document with OCR and optional post-processing.

    This is the main entry point for parsing PDFs. It:
    1. Submits the PDF to Datalab's Marker OCR API
    2. Saves markdown, images, and page files
    3. Optionally extracts page images at specified width
    4. Optionally filters non-essential figures using GPT
    5. Binds pages into a final markdown document

    Args:
        file_path: Path to the PDF file.
        output_dir: Directory for output files.
        filter_figures: Use GPT to remove logos/decorations (requires OPENAI_API_KEY).
        extract_images: Extract PDF pages as PNG images.
        image_width: Width for extracted page images.
        verbose: Print progress messages.

    Returns:
        Path to the final.md output file.
    """
    import asyncio
    from .filter import filter_pages

    file_path = Path(file_path)
    output_dir = Path(output_dir)

    if verbose:
        print(f"Processing: {file_path}")
        print("-" * 40)
        print("  Submitting to Datalab API...")

    # Submit and poll for results
    submit_result = submit_document(file_path, output_format="markdown")
    check_url = submit_result.get("request_check_url")

    if verbose:
        print(f"  Request ID: {submit_result.get('request_id')}")
        print("  Polling for results...")

    result = poll_result(check_url, verbose=verbose)

    # Save results
    save_result(result, output_dir, verbose=verbose)

    # Extract page images
    if extract_images and file_path.suffix.lower() == ".pdf":
        page_images_dir = output_dir / "page_images"
        num_images = extract_page_images(file_path, page_images_dir, width=image_width)
        if verbose:
            print(f"  Saved: {page_images_dir}/ ({num_images} page images @ {image_width}px)")

    # Filter and bind pages
    pages_dir = output_dir / "pages"
    final_doc = output_dir / "final.md"

    if filter_figures and os.getenv("OPENAI_API_KEY") and pages_dir.exists():
        if verbose:
            print(f"\n{'='*40}")
            print("Post-processing: Filtering non-essential figures...")
            print("=" * 40)

        filtered_dir = output_dir / "pages_filtered"
        asyncio.run(filter_pages(pages_dir, filtered_dir, verbose=verbose))
        num_pages = bind_pages(filtered_dir, final_doc)
    elif pages_dir.exists():
        if filter_figures and not os.getenv("OPENAI_API_KEY"):
            if verbose:
                print("\n  Note: Set OPENAI_API_KEY to enable figure filtering")
        num_pages = bind_pages(pages_dir, final_doc)
    else:
        # Single page or no pages - use output.md as final
        final_doc = output_dir / "output.md"
        num_pages = 1

    if verbose and pages_dir.exists():
        print(f"\n  Bound {num_pages} pages into: {final_doc}")

    return final_doc
