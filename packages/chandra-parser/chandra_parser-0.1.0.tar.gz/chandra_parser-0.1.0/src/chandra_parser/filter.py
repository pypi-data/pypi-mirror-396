"""Filter non-essential figures from markdown using OpenAI."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from openai import AsyncOpenAI

SYSTEM_PROMPT = """You are a document cleaner. Your task is to return the provided markdown text VERBATIM, but with all references to non-essential images removed.

REMOVE these (both the image embed AND any caption/description text):
- Company logos
- Brand marks
- Decorative page borders/headers/footers
- Watermarks
- Author/speaker photos (unless specifically discussed in narrative)
- Decorative separators or icons
- Background patterns

KEEP these (preserve exactly as-is):
- Charts, graphs, plots showing data
- Tables with information
- Diagrams explaining concepts
- Figures referenced in the text narrative
- Mathematical visualizations
- Flowcharts and process diagrams
- Screenshots demonstrating functionality
- Maps or geographic visualizations
- Any image that conveys substantive information

CRITICAL RULES:
1. Return the text EXACTLY as provided, only removing non-essential image references
2. Do NOT summarize, paraphrase, or modify any other content
3. Do NOT add any commentary or explanation
4. Preserve all formatting, headings, lists, and structure
5. If an image embed like ![alt text](filename) is non-essential, remove BOTH the embed AND any standalone caption text that describes the same thing
6. If unsure, KEEP the image reference
7. Where there is a figure embed there is also often a detailed description of the figure in the text. Strictly enclose the figure description text in markdown code blocks."""


def get_openai_client() -> AsyncOpenAI:
    """Get an async OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return AsyncOpenAI(api_key=api_key)


async def filter_page_content(
    markdown: str,
    client: AsyncOpenAI | None = None,
    model: str = "gpt-5-mini",
) -> str:
    """Filter non-essential figures from a single page of markdown.

    Args:
        markdown: The markdown content to filter.
        client: Optional AsyncOpenAI client (created if not provided).
        model: The OpenAI model to use.

    Returns:
        Filtered markdown with non-essential figures removed.
    """
    if not markdown.strip():
        return markdown

    if client is None:
        client = get_openai_client()

    user_input = f"""Return this markdown verbatim, removing only non-essential image references (logos, decorations, author photos) and their captions:

{markdown}"""

    response = await client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=user_input,
    )

    return response.output_text.strip()


async def _process_page_file(
    page_file: Path,
    output_dir: Path,
    client: AsyncOpenAI,
    model: str,
    verbose: bool,
) -> str:
    """Process a single page file."""
    markdown = page_file.read_text()
    filtered = await filter_page_content(markdown, client=client, model=model)
    output_file = output_dir / page_file.name
    output_file.write_text(filtered)
    if verbose:
        print(f"  Processed: {page_file.name}")
    return page_file.name


async def filter_pages(
    input_dir: str | Path,
    output_dir: str | Path,
    batch_size: int = 10,
    model: str = "gpt-5-mini",
    verbose: bool = True,
) -> int:
    """Filter non-essential figures from all markdown pages in a directory.

    Processes pages in parallel batches for efficiency.

    Args:
        input_dir: Directory containing page_*.md files.
        output_dir: Directory for filtered output files.
        batch_size: Number of pages to process in parallel.
        model: OpenAI model to use for filtering.
        verbose: Print progress messages.

    Returns:
        Number of pages processed.
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    client = get_openai_client()
    page_files = sorted(input_dir.glob("page_*.md"))
    total_pages = len(page_files)

    if verbose:
        print(f"Processing {total_pages} pages in batches of {batch_size}...")

    for i in range(0, len(page_files), batch_size):
        batch = page_files[i : i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(page_files) + batch_size - 1) // batch_size

        if verbose:
            print(f"\nBatch {batch_num}/{total_batches}:")

        tasks = [
            _process_page_file(pf, output_dir, client, model, verbose) for pf in batch
        ]
        await asyncio.gather(*tasks)

    if verbose:
        print(f"\n{'='*50}")
        print(f"Summary:")
        print(f"  Pages processed: {total_pages}")
        print(f"  Output saved to: {output_dir}")

    return total_pages
