"""Tests for the scraper service."""

from datetime import datetime
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from services.scraper import get_grant_details

# Subset of grant links from the terminal output (lines 193-224)
# Using a small subset for testing
TEST_GRANT_LINKS = [
    {
        "url": "https://oursggrants.gov.sg/grants/ssgacg/instruction",
        "button_text": "View Details",
    },
    {
        "url": "https://oursggrants.gov.sg/grants/nycaep/instruction",
        "button_text": "View Details",
    },
    {
        "url": "https://oursggrants.gov.sg/grants/ccf/instruction",
        "button_text": "View Details",
    },
    {
        "url": "https://oursggrants.gov.sg/grants/aicccnlp/instruction",
        "button_text": "View Details",
    },
    {
        "url": "https://oursggrants.gov.sg/grants/yep/instruction",
        "button_text": "View Details",
    },
]

# Screenshot directory
SCREENSHOT_DIR = Path(__file__).parent.parent / ".private" / "screenshots"


@pytest.fixture(scope="module")
def browser():
    """Create a browser instance for testing."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    """Create a new page for each test."""
    page = browser.new_page()
    yield page
    page.close()


def test_get_grant_details_returns_correct_structure(page):
    """Test that get_grant_details returns the expected structure."""
    # Use only first 2 links for faster testing
    test_links = TEST_GRANT_LINKS[:2]

    results = get_grant_details(page, test_links)
    print("these are the results\n\n\n", results, "=" * 50, "\n\n\n")
    # Check that we got results for all links
    assert len(results) == len(test_links)

    # Check structure of each result (default is text extraction)
    for result in results:
        assert "url" in result
        assert "button_text" in result
        assert "card_body_text" in result  # Default is text, not HTML
        assert isinstance(result["url"], str)
        assert isinstance(result["button_text"], str)


def test_get_grant_details_extracts_content(page):
    """Test that get_grant_details successfully extracts content from grant pages."""
    # Use only first 2 links for faster testing
    test_links = TEST_GRANT_LINKS[:2]

    results = get_grant_details(page, test_links)

    # Check that content was extracted (not None) - default is text
    for result in results:
        if "error" not in result:
            assert result["card_body_text"] is not None
            assert len(result["card_body_text"]) > 0
            # Text content should be substantial (not just whitespace)
            assert len(result["card_body_text"].strip()) > 100


def test_get_grant_details_with_screenshots(page):
    """Test get_grant_details and save screenshots for each grant page."""
    # Ensure screenshot directory exists
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Use a subset of links for testing
    test_links = TEST_GRANT_LINKS[:3]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = get_grant_details(page, test_links)

    # Take screenshots for each grant page
    for i, result in enumerate(results):
        if "error" not in result:
            # Navigate to the page
            page.goto(result["url"])
            page.wait_for_selector(".card-body", state="visible")

            # Save screenshot
            screenshot_path = (
                SCREENSHOT_DIR
                / f"test_grant_{timestamp}_{i + 1}_{result['url'].split('/')[-2]}.png"
            )
            page.screenshot(path=str(screenshot_path), full_page=True)

            # Verify screenshot was created
            assert screenshot_path.exists(), (
                f"Screenshot not created: {screenshot_path}"
            )


def test_get_grant_details_handles_errors_gracefully(page):
    """Test that get_grant_details handles errors gracefully."""
    # Use an invalid URL to test error handling
    invalid_links = [
        {
            "url": "https://oursggrants.gov.sg/grants/invalid_grant/instruction",
            "button_text": "View Details",
        }
    ]

    results = get_grant_details(page, invalid_links)

    # Should still return a result, but with error information
    assert len(results) == 1
    assert "error" in results[0] or results[0]["card_body_text"] is None


def test_get_grant_details_all_test_links(page):
    """Test get_grant_details with all test links and save screenshots."""
    # Ensure screenshot directory exists
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = get_grant_details(page, TEST_GRANT_LINKS)

    # Verify all links were processed
    assert len(results) == len(TEST_GRANT_LINKS)

    # Take screenshots and verify content extraction
    successful_extractions = 0
    for i, result in enumerate(results):
        if "error" not in result and result.get("card_body_text"):
            # Navigate to the page for screenshot
            page.goto(result["url"])
            page.wait_for_selector(".card-body", state="visible", timeout=10000)

            # Save screenshot
            grant_id = result["url"].split("/")[-2]
            screenshot_path = (
                SCREENSHOT_DIR / f"grant_{timestamp}_{i + 1}_{grant_id}.png"
            )
            page.screenshot(path=str(screenshot_path), full_page=True)

            successful_extractions += 1

    # At least some grants should be successfully extracted
    assert successful_extractions > 0, "No grants were successfully extracted"

    print(
        f"\nSuccessfully extracted {successful_extractions}/{len(TEST_GRANT_LINKS)} grants"
    )
    print(f"Screenshots saved to: {SCREENSHOT_DIR}")


def test_get_grant_details_html_extraction(page):
    """Test that get_grant_details can extract HTML when use_text=False."""
    # Use only first 2 links for faster testing
    test_links = TEST_GRANT_LINKS[:2]

    results = get_grant_details(page, test_links, use_text=False)

    # Check that HTML was extracted
    for result in results:
        if "error" not in result:
            assert "card_body_html" in result
            assert result["card_body_html"] is not None
            assert len(result["card_body_html"]) > 0
            # HTML should contain tags
            assert "<" in result["card_body_html"]
