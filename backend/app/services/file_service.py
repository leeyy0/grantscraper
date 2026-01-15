"""Service for downloading and converting files."""

from pathlib import Path
from urllib.parse import urlparse

import requests
from playwright.sync_api import Page


def download_file(url: str, output_path: Path) -> bool:
    """
    Download a file from URL to the specified path.

    Args:
        url: URL of the file to download
        output_path: Path where file should be saved

    Returns:
        True if successful, False otherwise
    """
    try:
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False


def convert_docx_to_pdf(docx_path: Path, pdf_path: Path) -> bool:
    """
    Convert DOCX file to PDF using LibreOffice (headless).

    Args:
        docx_path: Path to DOCX file
        pdf_path: Path where PDF should be saved

    Returns:
        True if successful, False otherwise
    """
    import subprocess

    try:
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        # Use LibreOffice to convert
        result = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(pdf_path.parent),
                str(docx_path),
            ],
            capture_output=True,
            timeout=60,
        )

        if result.returncode == 0:
            # LibreOffice creates PDF with same name but .pdf extension
            expected_pdf = docx_path.with_suffix(".pdf")
            if expected_pdf.exists():
                expected_pdf.rename(pdf_path)
                return True

        return False
    except Exception as e:
        print(f"Error converting DOCX to PDF: {e}")
        return False


def download_and_convert_file(
    url: str, output_dir: Path, grant_id: int, file_index: int
) -> Path | None:
    """
    Download a file from URL and convert to PDF if needed.

    Args:
        url: URL of the file
        output_dir: Directory to save the file
        grant_id: ID of the grant (for naming)
        file_index: Index of the file (for naming)

    Returns:
        Path to the saved file (PDF), or None if failed
    """
    # Determine file extension from URL
    parsed = urlparse(url)
    path = parsed.path
    ext = Path(path).suffix.lower() or ".pdf"

    # Download to temp location first
    temp_path = output_dir / f"temp_{grant_id}_{file_index}{ext}"
    if not download_file(url, temp_path):
        return None

    # Convert to PDF if needed
    if ext in [".docx", ".doc"]:
        pdf_path = output_dir / f"grant_{grant_id}_{file_index}.pdf"
        if convert_docx_to_pdf(temp_path, pdf_path):
            temp_path.unlink()  # Remove original DOCX
            return pdf_path
        else:
            # If conversion fails, keep original
            return temp_path
    elif ext == ".pdf":
        # Rename to standard format
        pdf_path = output_dir / f"grant_{grant_id}_{file_index}.pdf"
        temp_path.rename(pdf_path)
        return pdf_path
    elif ext in [".txt", ".md"]:
        # Keep text files as-is
        txt_path = output_dir / f"grant_{grant_id}_{file_index}.txt"
        temp_path.rename(txt_path)
        return txt_path
    else:
        # For other formats, try to convert via PDF if possible
        # Otherwise keep as-is
        return temp_path


def download_files_from_links(
    page: Page, links: list[str], output_dir: Path, grant_id: int
) -> list[Path]:
    """
    Download files from a list of URLs.

    Args:
        page: Playwright page object (for handling redirects/auth)
        links: List of URLs to download
        output_dir: Directory to save files
        grant_id: ID of the grant

    Returns:
        List of paths to downloaded files
    """
    downloaded_files = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for idx, link in enumerate(links):
        # Check if link is a file (PDF, DOCX, etc.)
        parsed = urlparse(link)
        path = parsed.path.lower()
        ext = Path(path).suffix.lower()

        if ext in [".pdf", ".docx", ".doc", ".txt", ".md"]:
            file_path = download_and_convert_file(link, output_dir, grant_id, idx)
            if file_path:
                downloaded_files.append(file_path)
        else:
            # If not a direct file link, try to scrape the page for downloadable content
            # This is a fallback - you might want to enhance this
            print(f"Skipping non-file link: {link}")

    return downloaded_files
