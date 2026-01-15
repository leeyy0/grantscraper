"""Tests for the deep scraper service."""

import pytest
from playwright.sync_api import sync_playwright
from services.deep_scraper import (
    deep_scrape_grants,
    extract_page_content_and_links,
    scrape_url_recursive,
)
from services.scraper import get_grant_details

# Test URL provided by user
TEST_GRANT_URL = "https://oursggrants.gov.sg/grants/aicccmda/instruction"


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


def test_extract_page_content_and_links(page):
    """Test that extract_page_content_and_links extracts content and links from a page."""
    result = extract_page_content_and_links(page, TEST_GRANT_URL)

    # Check structure
    assert "url" in result
    assert "content" in result
    assert "links" in result
    assert result["url"] == TEST_GRANT_URL

    # Check that content was extracted
    assert result["content"] is not None
    assert len(result["content"]) > 0
    assert len(result["content"].strip()) > 100

    # Check that links is a list
    assert isinstance(result["links"], list)

    print(f"\nExtracted {len(result['links'])} link(s) from {TEST_GRANT_URL}")
    if result["links"]:
        print("Sample links:")
        for link in result["links"][:5]:  # Show first 5 links
            print(f"  - {link}")


def test_scrape_url_recursive_shallow(page):
    """Test scrape_url_recursive with max_depth=0 (no recursion)."""
    result = scrape_url_recursive(page, TEST_GRANT_URL, max_depth=0)

    # Check structure
    assert "url" in result
    assert "content" in result
    assert "links" in result
    assert "nested_content" in result
    assert result["url"] == TEST_GRANT_URL

    # Check that content was extracted
    assert result["content"] is not None
    assert len(result["content"]) > 0

    # With max_depth=0, there should be no nested content
    assert isinstance(result["nested_content"], list)
    assert len(result["nested_content"]) == 0

    print(f"\nExtracted {len(result['links'])} link(s) from {TEST_GRANT_URL}")


def test_scrape_url_recursive_deep(page):
    """Test scrape_url_recursive with max_depth=2 (limited recursion for testing)."""
    result = scrape_url_recursive(page, TEST_GRANT_URL, max_depth=2)

    # Check structure
    assert "url" in result
    assert "content" in result
    assert "links" in result
    assert "nested_content" in result
    assert result["url"] == TEST_GRANT_URL

    # Check that content was extracted
    assert result["content"] is not None
    assert len(result["content"]) > 0

    # Check nested content structure
    assert isinstance(result["nested_content"], list)

    print(f"\nExtracted {len(result['links'])} link(s) from {TEST_GRANT_URL}")
    print(f"Found {len(result['nested_content'])} nested page(s)")

    # If there are nested pages, verify their structure
    for nested in result["nested_content"]:
        assert "url" in nested
        assert "content" in nested
        assert "nested_content" in nested


def test_deep_scrape_grants(page):
    """Test deep_scrape_grants with the test grant URL."""
    # First, get grant details using the scraper
    test_grant_links = [
        {
            "url": TEST_GRANT_URL,
            "button_text": "View Details",
        }
    ]

    # Get grant details (this will extract links from card-body)
    grant_details = get_grant_details(page, test_grant_links, use_text=True)

    # Verify grant details were extracted
    assert len(grant_details) == 1
    assert "links" in grant_details[0]
    assert grant_details[0]["url"] == TEST_GRANT_URL

    print(f"\nFound {len(grant_details[0]['links'])} link(s) in grant card-body")

    # Now perform deep scraping
    deep_scraped = deep_scrape_grants(page, grant_details, max_depth=2)

    # Check structure
    assert len(deep_scraped) == 1
    assert "deep_content" in deep_scraped[0]
    assert deep_scraped[0]["url"] == TEST_GRANT_URL

    # Check that original grant details are preserved
    assert "card_body_text" in deep_scraped[0]
    assert "links" in deep_scraped[0]

    # Check deep_content structure
    deep_content = deep_scraped[0]["deep_content"]
    assert isinstance(deep_content, list)

    print(f"\nDeep scraped {len(deep_content)} linked page(s)")

    # If there are deep content pages, verify their structure
    for content in deep_content:
        assert "url" in content
        assert "content" in content
        assert "nested_content" in content
        print(f"  - {content['url']}: {len(content.get('links', []))} links found")


def test_deep_scrape_grants_no_links(page):
    """Test deep_scrape_grants when grant has no links."""
    # Create a grant detail with no links
    grant_details = [
        {
            "url": TEST_GRANT_URL,
            "button_text": "View Details",
            "card_body_text": "Some content",
            "links": [],  # No links
        }
    ]

    deep_scraped = deep_scrape_grants(page, grant_details, max_depth=2)

    # Check structure
    assert len(deep_scraped) == 1
    assert "deep_content" in deep_scraped[0]
    assert deep_scraped[0]["deep_content"] == []


def test_deep_scrape_grants_with_max_depth(page):
    """Test deep_scrape_grants with different max_depth values."""
    test_grant_links = [
        {
            "url": TEST_GRANT_URL,
            "button_text": "View Details",
        }
    ]

    # Get grant details
    grant_details = get_grant_details(page, test_grant_links, use_text=True)

    # Test with max_depth=1 (shallow)
    shallow_result = deep_scrape_grants(page, grant_details, max_depth=1)
    assert len(shallow_result) == 1
    assert "deep_content" in shallow_result[0]

    # Test with max_depth=3 (deeper)
    deep_result = deep_scrape_grants(page, grant_details, max_depth=3)
    assert len(deep_result) == 1
    assert "deep_content" in deep_result[0]

    print(f"\nShallow (depth=1): {len(shallow_result[0]['deep_content'])} pages")
    print(f"Deep (depth=3): {len(deep_result[0]['deep_content'])} pages")
