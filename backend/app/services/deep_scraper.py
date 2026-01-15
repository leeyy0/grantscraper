from typing import Any
from urllib.parse import urljoin, urlparse

from playwright.sync_api import Page


def extract_page_content_and_links(page: Page, url: str) -> dict[str, Any]:
    """Extract content and links from a page.

    Args:
        page: Playwright page object
        url: URL of the page to visit

    Returns:
        Dictionary with:
        - 'url': The URL visited
        - 'content': Text content from the page (preferring .card-body if available)
        - 'links': List of absolute URLs found on the page
        - 'error': Error message if extraction failed
    """
    result = {
        "url": url,
        "content": None,
        "links": [],
        "error": None,
    }

    print(f"Extracting content from: {url}")
    try:
        print("  Navigating to page...")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=10000)
        print("  Page loaded successfully")

        # Try to extract from .card-body first (common for grant pages)
        card_body = page.locator(".card-body").first
        if card_body.count() > 0:
            print("  Found .card-body element, extracting from card-body")
            result["content"] = card_body.inner_text()
            # Extract links from card-body
            link_elements = card_body.locator("a[href]")
        else:
            # Fallback to body content if no card-body
            print("  No .card-body found, falling back to body content")
            body = page.locator("body")
            result["content"] = body.inner_text()
            # Extract links from body
            link_elements = body.locator("a[href]")

        # Extract all links
        link_count = link_elements.count()
        print(f"  Found {link_count} link element(s)")
        for i in range(link_count):
            href = link_elements.nth(i).get_attribute("href")
            if href:
                # Convert relative URLs to absolute
                if href.startswith("http"):
                    result["links"].append(href)
                else:
                    absolute_url = urljoin(url, href)
                    result["links"].append(absolute_url)

        # Remove duplicates while preserving order
        seen = set()
        result["links"] = [
            link for link in result["links"] if link not in seen and not seen.add(link)
        ]
        print(f"  Extracted {len(result['links'])} unique link(s)")

        content_length = len(result["content"]) if result["content"] else 0
        print(f"  Extracted {content_length} characters of content")
        print(f"  Successfully extracted content from {url}")

    except Exception as e:
        result["error"] = str(e)
        print(f"  Error extracting content from {url}: {e}")

    return result


def scrape_url_recursive(
    page: Page,
    url: str,
    current_depth: int = 0,
    max_depth: int = 4,
    visited_urls: set[str] | None = None,
    base_domain: str | None = None,
) -> dict[str, Any]:
    """Recursively scrape a URL and its linked pages up to a maximum depth.

    Args:
        page: Playwright page object
        url: URL to scrape
        current_depth: Current recursion depth (0 = initial page)
        max_depth: Maximum depth to recurse (default: 4)
        visited_urls: Set of URLs already visited to avoid cycles
        base_domain: Base domain to restrict links to (optional)

    Returns:
        Dictionary with:
        - 'url': The URL
        - 'content': Text content from the page
        - 'links': List of URLs found on the page
        - 'nested_content': List of dictionaries with nested scraped content
        - 'error': Error message if extraction failed
    """
    if visited_urls is None:
        visited_urls = set()

    if base_domain is None:
        parsed = urlparse(url)
        base_domain = f"{parsed.scheme}://{parsed.netloc}"

    # Avoid cycles and already visited URLs
    if url in visited_urls:
        return {
            "url": url,
            "content": None,
            "links": [],
            "nested_content": [],
            "error": "Already visited (cycle prevention)",
        }

    visited_urls.add(url)

    # Extract content and links from current page
    page_data = extract_page_content_and_links(page, url)
    result = {
        "url": url,
        "content": page_data["content"],
        "links": page_data["links"],
        "nested_content": [],
        "error": page_data["error"],
    }

    # If we've reached max depth, don't recurse further
    if current_depth >= max_depth:
        return result

    # Recursively scrape linked pages
    for link_url in page_data["links"]:
        # Optionally filter by base domain to stay within the same site
        if base_domain:
            parsed_link = urlparse(link_url)
            link_domain = f"{parsed_link.scheme}://{parsed_link.netloc}"
            # Only follow links from the same domain
            if link_domain != base_domain:
                continue

        # Skip non-HTTP(S) links
        if not link_url.startswith(("http://", "https://")):
            continue

        print(
            f"  {'  ' * current_depth}→ Following link (depth {current_depth + 1}): {link_url}"
        )
        nested_result = scrape_url_recursive(
            page=page,
            url=link_url,
            current_depth=current_depth + 1,
            max_depth=max_depth,
            visited_urls=visited_urls,
            base_domain=base_domain,
        )
        result["nested_content"].append(nested_result)

    return result


def deep_scrape_grants(
    page: Page,
    grant_details: list[dict[str, Any]],
    max_depth: int = 4,
) -> list[dict[str, Any]]:
    """Perform deep scraping on grant details, following links recursively.

    This function takes grant details from get_grant_details() and recursively
    follows links found in the card-body up to a specified depth.

    Args:
        page: Playwright page object
        grant_details: List of grant detail dictionaries from get_grant_details()
        max_depth: Maximum depth to recurse when following links (default: 4)

    Returns:
        List of dictionaries with the same structure as input, but with added
        'deep_content' field containing recursively scraped content from linked pages.
        Each grant will have:
        - All original fields (url, button_text, card_body_text, links, etc.)
        - 'deep_content': List of dictionaries with nested content from followed links
    """
    results = []

    for grant in grant_details:
        grant_url = grant.get("url")
        button_text = grant.get("button_text", "Unknown")

        print(f"\nDeep scraping grant: {button_text}")
        print(f"  URL: {grant_url}")

        # Get links from the grant details (extracted from card-body)
        links = grant.get("links", [])

        if not links:
            print("  No links found in grant card-body")
            results.append(
                {
                    **grant,
                    "deep_content": [],
                }
            )
            continue

        print(f"  Found {len(links)} link(s) in card-body")

        # Follow each link from the card-body and scrape recursively
        deep_content = []
        visited_urls = set()

        # Determine base domain from grant URL
        parsed = urlparse(grant_url)
        base_domain = f"{parsed.scheme}://{parsed.netloc}"

        for link_url in links:
            # Skip non-HTTP(S) links
            if not link_url.startswith(("http://", "https://")):
                continue

            print(f"  → Following link from card-body: {link_url}")
            nested_result = scrape_url_recursive(
                page=page,
                url=link_url,
                current_depth=0,
                max_depth=max_depth,
                visited_urls=visited_urls,
                base_domain=base_domain,
            )
            deep_content.append(nested_result)

        results.append(
            {
                **grant,
                "deep_content": deep_content,
            }
        )

    return results
