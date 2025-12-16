"""Command-line interface for Chandra Parser."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from . import __version__


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """Chandra Parser - PDF to Markdown using Datalab's Marker OCR API."""
    pass


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option(
    "--no-filter",
    is_flag=True,
    help="Skip GPT-based figure filtering (doesn't require OPENAI_API_KEY).",
)
@click.option(
    "--no-images",
    is_flag=True,
    help="Skip extracting page images from PDF.",
)
@click.option(
    "--image-width",
    default=712,
    type=int,
    help="Width in pixels for extracted page images.",
)
@click.option(
    "--quiet", "-q",
    is_flag=True,
    help="Suppress progress output.",
)
def parse(
    pdf_path: Path,
    output_dir: Path,
    no_filter: bool,
    no_images: bool,
    image_width: int,
    quiet: bool,
) -> None:
    """Parse a PDF document with OCR.

    PDF_PATH is the path to the PDF file to process.
    OUTPUT_DIR is the directory where output files will be saved.

    Output includes:
    - final.md: Cleaned, bound markdown document
    - output.md: Raw OCR output
    - pages/: Individual page markdown files
    - page_images/: PNG renders of each page (optional)
    - images/: Extracted figure images from OCR
    """
    from .client import parse_pdf

    try:
        parse_pdf(
            file_path=pdf_path,
            output_dir=output_dir,
            filter_figures=not no_filter,
            extract_images=not no_images,
            image_width=image_width,
            verbose=not quiet,
        )
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option(
    "--batch-size",
    default=10,
    type=int,
    help="Number of pages to process in parallel.",
)
@click.option(
    "--model",
    default="gpt-5-mini",
    help="OpenAI model to use for filtering.",
)
@click.option(
    "--quiet", "-q",
    is_flag=True,
    help="Suppress progress output.",
)
def filter(
    input_dir: Path,
    output_dir: Path,
    batch_size: int,
    model: str,
    quiet: bool,
) -> None:
    """Filter non-essential figures from markdown pages.

    INPUT_DIR is a directory containing page_*.md files.
    OUTPUT_DIR is where filtered files will be saved.

    Requires OPENAI_API_KEY environment variable.
    """
    import asyncio
    from .filter import filter_pages

    try:
        asyncio.run(
            filter_pages(
                input_dir=input_dir,
                output_dir=output_dir,
                batch_size=batch_size,
                model=model,
                verbose=not quiet,
            )
        )
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option(
    "--width",
    default=712,
    type=int,
    help="Width in pixels (height scales proportionally).",
)
def images(
    pdf_path: Path,
    output_dir: Path,
    width: int,
) -> None:
    """Extract page images from a PDF.

    PDF_PATH is the path to the PDF file.
    OUTPUT_DIR is where page images will be saved.
    """
    from .client import extract_page_images

    try:
        num_pages = extract_page_images(pdf_path, output_dir, width=width)
        click.echo(f"Extracted {num_pages} page images to {output_dir}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
