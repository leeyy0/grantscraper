from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urljoin

from playwright.sync_api import Page, sync_playwright

if TYPE_CHECKING:
    from models.models import Grant


def get_links(page: Page) -> list[dict[str, str]]:
    """Extract links for open grants from the grants listing page.

    Args:
        page: Playwright page object on the grants listing page

    Returns:
        List of dictionaries with 'url' and 'button_text' keys
    """
    grant_links = []
    grant_cards = page.locator('[class*="itemsContainer"]')

    for i in range(grant_cards.count()):
        card = grant_cards.nth(i)

        # Check if the grant is closed
        # Grants are closed if they have either:
        # 1. A "Closed" div with class containing "closedGrant"
        # 2. Text "Applications closed" in the status section
        is_closed = False

        # Check for "Closed" div
        closed_div = card.locator('[class*="closedGrant"]')
        if closed_div.count() > 0:
            is_closed = True

        # Check for "Applications closed" text with red styling
        if not is_closed:
            status_text = card.locator("#closingDates span").text_content()
            if status_text and "Applications closed" in status_text:
                is_closed = True

        # If grant is not closed, extract the link
        if not is_closed:
            link_element = card.locator("a[href]")
            if link_element.count() > 0:
                href = link_element.get_attribute("href")
                button_text = card.locator(
                    '[class*="viewDetailsButton"]'
                ).text_content()
                if href:
                    # Construct full URL if relative
                    full_url = (
                        href
                        if href.startswith("http")
                        else f"https://oursggrants.gov.sg{href}"
                    )
                    grant_links.append(
                        {
                            "url": full_url,
                            "button_text": button_text.strip() if button_text else None,
                        }
                    )

    return grant_links


def extract_card_body_content(page: Page, url: str) -> str:
    """Extract the content from the card-body div on a grant detail page.

    Args:
        page: Playwright page object
        url: URL of the grant detail page to visit

    Returns:
        HTML content of the card-body div as a string
    """
    page.goto(url)
    page.wait_for_selector(".card-body", state="visible")

    # Extract the HTML content of the card-body div
    card_body = page.locator(".card-body").first
    html_content = card_body.inner_html()

    return html_content


def extract_card_body_text(page: Page, url: str) -> str:
    """Extract clean text content from the card-body div (alternative to HTML extraction).

    This is recommended for LLM processing as it:
    - Removes HTML markup noise
    - Preserves logical structure (headings, lists, sections)
    - Is token-efficient
    - Is easy for LLMs to parse and extract information

    Args:
        page: Playwright page object
        url: URL of the grant detail page to visit

    Returns:
        Clean plain text with structure preserved
    """
    page.goto(url)
    page.wait_for_selector(".card-body", state="visible")

    # Extract clean text content (automatically handles HTML conversion)
    card_body = page.locator(".card-body").first
    text_content = card_body.inner_text()

    return text_content


def extract_card_body_text_and_links(page: Page, url: str) -> tuple[str, list[str]]:
    """Extract both text content and links from the card-body div in a single page visit.

    This is more efficient than calling extract_card_body_text and extract_links_from_card_body
    separately, as it only visits the page once.

    Args:
        page: Playwright page object
        url: URL of the grant detail page to visit

    Returns:
        Tuple of (text_content, links) where:
        - text_content: Clean plain text with structure preserved
        - links: List of absolute URLs found in the card-body
    """
    page.goto(url)
    page.wait_for_selector(".card-body", state="visible")

    card_body = page.locator(".card-body").first

    # Extract clean text content
    text_content = card_body.inner_text()

    # Extract all links from the card-body
    links = []
    link_elements = card_body.locator("a[href]")

    for i in range(link_elements.count()):
        href = link_elements.nth(i).get_attribute("href")
        if href:
            # Convert relative URLs to absolute
            if href.startswith("http"):
                links.append(href)
            else:
                # Use urljoin to properly handle relative URLs
                absolute_url = urljoin(url, href)
                links.append(absolute_url)

    # Remove duplicates while preserving order
    seen = set()
    unique_links = [link for link in links if link not in seen and not seen.add(link)]

    return text_content, unique_links


def extract_links_from_card_body(page: Page, url: str) -> list[str]:
    """Extract all links (href attributes) from the card-body div.

    Args:
        page: Playwright page object
        url: URL of the grant detail page to visit

    Returns:
        List of absolute URLs found in the card-body
    """
    page.goto(url)
    page.wait_for_selector(".card-body", state="visible")

    # Extract all links from the card-body
    card_body = page.locator(".card-body").first
    links = []
    link_elements = card_body.locator("a[href]")

    for i in range(link_elements.count()):
        href = link_elements.nth(i).get_attribute("href")
        if href:
            # Convert relative URLs to absolute
            if href.startswith("http"):
                links.append(href)
            else:
                # Use urljoin to properly handle relative URLs
                absolute_url = urljoin(url, href)
                links.append(absolute_url)

    return links


def get_grant_details(
    page: Page, grant_links: list[dict[str, str]], use_text: bool = True
) -> list[dict[str, str]]:
    """Visit all grant links and extract card-body content.

    This function is designed to extract grant content for LLM processing.
    By default, it returns clean text (recommended for LLMs), but can also
    return HTML if needed. Also extracts links from the card-body for deep scraping.

    Args:
        page: Playwright page object
        grant_links: List of grant link dictionaries with 'url' and 'button_text'
        use_text: If True, extract clean text (recommended for LLM). If False, extract HTML.

    Returns:
        List of dictionaries with:
        - 'url': Grant URL
        - 'button_text': Button text from listing page
        - 'card_body_text' or 'card_body_html': Extracted content (depending on use_text)
        - 'links': List of URLs found in the card-body
    """
    grant_details = []

    for grant in grant_links:
        print(f"Extracting content from: {grant['button_text']}")
        try:
            if use_text:
                # Extract both text and links in a single page visit (more efficient)
                card_body_content, links = extract_card_body_text_and_links(
                    page, grant["url"]
                )
                grant_details.append(
                    {
                        "url": grant["url"],
                        "button_text": grant["button_text"],
                        "card_body_text": card_body_content,
                        "links": links,
                    }
                )
            else:
                # Extract HTML - for other use cases
                card_body_content = extract_card_body_content(page, grant["url"])
                # Still need to extract links separately when using HTML
                links = extract_links_from_card_body(page, grant["url"])
                grant_details.append(
                    {
                        "url": grant["url"],
                        "button_text": grant["button_text"],
                        "card_body_html": card_body_content,
                        "links": links,
                    }
                )
        except Exception as e:
            print(f"Error extracting content from {grant['url']}: {e}")
            key = "card_body_text" if use_text else "card_body_html"
            grant_details.append(
                {
                    "url": grant["url"],
                    "button_text": grant["button_text"],
                    key: None,
                    "links": [],
                    "error": str(e),
                }
            )

    return grant_details


def get_grant_details_as_models(
    page: Page, grant_links: list[dict[str, str]], use_text: bool = True
) -> list["Grant"]:
    """Get grant details and return as Grant SQLAlchemy model instances.

    This is a convenience wrapper around get_grant_details() that converts
    the dictionaries to Grant model instances.

    Args:
        page: Playwright page object
        grant_links: List of grant link dictionaries with 'url' and 'button_text'
        use_text: If True, extract clean text (recommended for LLM). If False, extract HTML.

    Returns:
        List of Grant SQLAlchemy model instances (not yet persisted to database)
    """
    from models.models import Grant

    grant_dicts = get_grant_details(page, grant_links, use_text=use_text)
    return [Grant.from_scraper_dict(grant_dict) for grant_dict in grant_dicts]


# Screenshot directory - ensure screenshots go to backend/.private/screenshots
SCREENSHOT_DIR = Path(__file__).parent.parent / ".private" / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Generate timestamp for unique screenshot filenames
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://oursggrants.gov.sg/grants/new")
    print(page.title())
    page.screenshot(
        path=str(SCREENSHOT_DIR / f"screenshot_{timestamp}_01_initial_load.png"),
        full_page=True,
    )

    # Wait for the filter section to load
    print("waiting for selector")
    page.wait_for_selector("#applyAs-1", state="visible")

    # Click on the "Organisation" checkbox
    # Try clicking the label first (more reliable), fallback to JS click if needed
    print("trying to click the label first")
    checkbox = page.locator("#applyAs-1")
    try:
        # Try clicking the label associated with the checkbox
        print("trying to click the label associated with checkbox")
        page.locator('label[for="applyAs-1"]').click(timeout=5000)
    except Exception:
        # If label click fails, use JavaScript to click the checkbox directly
        # This bypasses viewport issues
        print("using javascript to click\n\n")
        checkbox.evaluate("element => element.click()")

    # Wait a moment for the filter to apply
    page.wait_for_timeout(1000)
    page.screenshot(
        path=str(
            SCREENSHOT_DIR / f"screenshot_{timestamp}_02_after_checkbox_click.png"
        ),
        full_page=True,
    )

    # Wait for grant cards to be visible
    page.wait_for_selector('[class*="itemsContainer"]', state="visible")
    page.screenshot(
        path=str(SCREENSHOT_DIR / f"screenshot_{timestamp}_03_grant_cards_visible.png"),
        full_page=True,
    )

    # Extract links for grants that are not closed
    grant_links = get_links(page)

    # Print the extracted links
    print(f"\nFound {len(grant_links)} open grant(s):")
    for grant in grant_links:
        print(f"  - {grant['button_text']}: {grant['url']}")

    page.screenshot(
        path=str(SCREENSHOT_DIR / f"screenshot_{timestamp}_04_final_state.png"),
        full_page=True,
    )
    browser.close()
