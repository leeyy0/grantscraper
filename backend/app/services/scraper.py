import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urljoin

from playwright.sync_api import Page, sync_playwright

if TYPE_CHECKING:
    from models.models import Grant

logger = logging.getLogger(__name__)


def get_links(page: Page) -> list[dict[str, str]]:
    """Extract links for open grants from the grants listing page.

    Args:
        page: Playwright page object on the grants listing page

    Returns:
        List of dictionaries with 'url' and 'button_text' keys
    """
    grant_links = []
    grant_cards = page.locator('[class*="itemsContainer"]')
    total_cards = grant_cards.count()

    logger.debug(f"Found {total_cards} grant cards on page")

    for i in range(total_cards):
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
                    logger.debug(f"Found open grant: {button_text}")
        else:
            logger.debug(f"Skipping closed grant (card {i + 1})")

    logger.info(
        f"Extracted {len(grant_links)} open grants from {total_cards} total cards"
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
    page.goto(url, wait_until="domcontentloaded")
    # Wait for the card-body to be attached to DOM (not necessarily visible)
    page.wait_for_selector(".card-body", state="attached", timeout=60000)
    # Give it a moment to render
    page.wait_for_timeout(1000)

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
    page.goto(url, wait_until="domcontentloaded")
    # Wait for the card-body to be attached to DOM (not necessarily visible)
    page.wait_for_selector(".card-body", state="attached", timeout=60000)
    # Give it a moment to render
    page.wait_for_timeout(1000)

    # Extract clean text content (automatically handles HTML conversion)
    card_body = page.locator(".card-body").first
    text_content = card_body.inner_text()

    return text_content


def extract_card_body_text_and_links(
    page: Page, url: str
) -> tuple[str, list[str], str, str]:
    """Extract grant details including issuer, title, text content and links in a single page visit.

    This is more efficient than calling multiple extraction functions separately,
    as it only visits the page once.

    Args:
        page: Playwright page object
        url: URL of the grant detail page to visit

    Returns:
        Tuple of (text_content, links, issuer, title) where:
        - text_content: Clean plain text with structure preserved (from card-body)
        - links: List of absolute URLs found in the card-body
        - issuer: Grant issuing agency (from .card-title h2)
        - title: Grant title (from #grant-header)
    """
    page.goto(url, wait_until="domcontentloaded")
    # Wait for the card-body to be attached to DOM (not necessarily visible)
    page.wait_for_selector(".card-body", state="attached", timeout=60000)
    # Give it a moment to render
    page.wait_for_timeout(1000)

    # Extract grant issuer from .card-title h2
    issuer = ""
    try:
        issuer_element = page.locator(".card-title h2").first
        if issuer_element.count() > 0:
            issuer = issuer_element.inner_text().strip()
            logger.debug(f"Extracted issuer: {issuer}")
        else:
            logger.warning(f"No .card-title h2 element found at {url}")
    except Exception as e:
        logger.warning(f"Could not extract grant issuer from {url}: {e}")

    # Extract grant title from #grant-header
    title = ""
    try:
        title_element = page.locator("#grant-header").first
        if title_element.count() > 0:
            title = title_element.inner_text().strip()
            logger.debug(f"Extracted title: {title}")
        else:
            logger.warning(f"No #grant-header element found at {url}")
    except Exception as e:
        logger.warning(f"Could not extract grant title from {url}: {e}")

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

    return text_content, unique_links, issuer, title


def extract_links_from_card_body(page: Page, url: str) -> list[str]:
    """Extract all links (href attributes) from the card-body div.

    Args:
        page: Playwright page object
        url: URL of the grant detail page to visit

    Returns:
        List of absolute URLs found in the card-body
    """
    page.goto(url, wait_until="domcontentloaded")
    # Wait for the card-body to be attached to DOM (not necessarily visible)
    page.wait_for_selector(".card-body", state="attached", timeout=60000)
    # Give it a moment to render
    page.wait_for_timeout(1000)

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
    page: Page,
    grant_links: list[dict[str, str]],
    use_text: bool = True,
    job_id: str | None = None,
) -> list[dict[str, str]]:
    """Visit all grant links and extract card-body content.

    This function is designed to extract grant content for LLM processing.
    By default, it returns clean text (recommended for LLMs), but can also
    return HTML if needed. Also extracts links from the card-body for deep scraping,
    as well as grant issuer and title.

    Args:
        page: Playwright page object
        grant_links: List of grant link dictionaries with 'url' and 'button_text'
        use_text: If True, extract clean text (recommended for LLM). If False, extract HTML.
        job_id: Optional job ID for status tracking

    Returns:
        List of dictionaries with:
        - 'url': Grant URL
        - 'button_text': Button text from listing page
        - 'card_body_text' or 'card_body_html': Extracted content (depending on use_text)
        - 'links': List of URLs found in the card-body
        - 'issuer': Grant issuing agency
        - 'title': Grant title
    """
    grant_details = []
    total_grants = len(grant_links)

    # Import status tracking if job_id provided
    if job_id:
        from app.services.refresh_status import RefreshPhase, update_refresh_status

    for idx, grant in enumerate(grant_links, start=1):
        print(f"Extracting content from: {grant['url']}")
        
        # Update progress if job_id provided
        if job_id:
            update_refresh_status(
                job_id,
                RefreshPhase.SCRAPING_DETAILS,
                total_found=total_grants,
                current_grant=idx,
                message=f"Scraping grant {idx} of {total_grants}",
            )
        
        try:
            if use_text:
                # Extract text, links, issuer, and title in a single page visit (more efficient)
                card_body_content, links, issuer, title = (
                    extract_card_body_text_and_links(page, grant["url"])
                )
                logger.info(
                    f"Extracted grant - Issuer: '{issuer}', Title: '{title}', "
                    f"Links: {len(links)}, Content: {len(card_body_content)} chars"
                )
                grant_details.append(
                    {
                        "url": grant["url"],
                        "button_text": grant["button_text"],
                        "card_body_text": card_body_content,
                        "links": links,
                        "issuer": issuer,
                        "title": title,
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
                        "issuer": "",
                        "title": "",
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
                    "issuer": "",
                    "title": "",
                    "error": str(e),
                }
            )

    return grant_details


def get_grant_details_as_models(
    page: Page,
    grant_links: list[dict[str, str]],
    use_text: bool = True,
    job_id: str | None = None,
) -> list["Grant"]:
    """Get grant details and return as Grant SQLAlchemy model instances.

    This is a convenience wrapper around get_grant_details() that converts
    the dictionaries to Grant model instances.

    Args:
        page: Playwright page object
        grant_links: List of grant link dictionaries with 'url' and 'button_text'
        use_text: If True, extract clean text (recommended for LLM). If False, extract HTML.
        job_id: Optional job ID for status tracking

    Returns:
        List of Grant SQLAlchemy model instances (not yet persisted to database)
    """
    from app.models.models import Grant

    grant_dicts = get_grant_details(page, grant_links, use_text=use_text, job_id=job_id)
    return [Grant.from_scraper_dict(grant_dict) for grant_dict in grant_dicts]


def save_grants_to_db(
    page: Page,
    grant_links: list[dict[str, str]],
    use_text: bool = True,
    job_id: str | None = None,
) -> list["Grant"]:
    """Scrape grant details and save them to the database.

    This function performs Step 2 of the ingestion pipeline:
    - Scrapes grant details from URLs
    - Saves or updates grants in the database (matched by URL)

    Args:
        page: Playwright page object
        grant_links: List of grant link dictionaries with 'url' and 'button_text'
        use_text: If True, extract clean text (recommended for LLM). If False, extract HTML.
        job_id: Optional job ID for status tracking

    Returns:
        List of saved Grant SQLAlchemy model instances
    """
    from app.access import GrantAccess, get_db_session

    logger.info(f"Extracting details for {len(grant_links)} grants...")

    # Get grant details as model instances
    grant_models = get_grant_details_as_models(
        page, grant_links, use_text=use_text, job_id=job_id
    )

    logger.info(f"Saving {len(grant_models)} grants to database...")

    # Update status if job_id provided
    if job_id:
        from app.services.refresh_status import RefreshPhase, update_refresh_status

        update_refresh_status(
            job_id,
            RefreshPhase.SAVING_TO_DB,
            total_found=len(grant_models),
            grants_saved=0,
            message=f"Saving {len(grant_models)} grants to database",
        )

    # Save to database (create or update by URL)
    with get_db_session() as db:
        saved_grants = GrantAccess.create_or_update_many_by_url(db, grant_models)

    # Update final save count
    if job_id:
        update_refresh_status(
            job_id,
            RefreshPhase.SAVING_TO_DB,
            grants_saved=len(saved_grants),
            message=f"Successfully saved {len(saved_grants)} grants",
        )

    logger.info(f"Successfully saved {len(saved_grants)} grants")
    return saved_grants


# Screenshot directory - ensure screenshots go to backend/.private/screenshots
SCREENSHOT_DIR = Path(__file__).parent.parent.parent / ".private" / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def scrape_and_refresh_grants(
    take_screenshots: bool = False,
    headless: bool = True,
    save_to_db: bool = True,
    job_id: str | None = None,
) -> dict:
    """
    Scrape open grants from the website and optionally save to database.

    This function performs the complete grant scraping workflow:
    1. Navigate to the grants listing page
    2. Apply filters (Organisation checkbox)
    3. Extract links for open grants (closed grants are filtered out)
    4. Extract grant details from each page
    5. Optionally save to database

    Args:
        take_screenshots: Whether to save screenshots during scraping
        headless: Whether to run browser in headless mode
        save_to_db: Whether to save grants to database
        job_id: Optional job ID for status tracking

    Returns:
        Dictionary with:
        - 'total_found': Number of open grants found
        - 'grants_saved': Number of grants saved to DB (if save_to_db=True)
        - 'grant_urls': List of grant URLs processed
        - 'errors': List of any errors encountered
    """
    logger.info("Starting grant scraping process...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    errors = []
    grant_urls = []

    # Import status tracking if job_id provided
    if job_id:
        from app.services.refresh_status import RefreshPhase, update_refresh_status

        update_refresh_status(
            job_id, RefreshPhase.STARTING, message="Initializing browser"
        )

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()

            # Navigate to grants page
            logger.info("Navigating to grants listing page...")
            if job_id:
                update_refresh_status(
                    job_id, RefreshPhase.NAVIGATING, message="Navigating to grants page"
                )
            page.goto("https://oursggrants.gov.sg/grants/new")
            logger.info(f"Page loaded: {page.title()}")

            if take_screenshots:
                page.screenshot(
                    path=str(
                        SCREENSHOT_DIR / f"screenshot_{timestamp}_01_initial_load.png"
                    ),
                    full_page=True,
                )

            # Wait for the filter section to load
            logger.info("Waiting for filter section to load...")
            page.wait_for_selector("#applyAs-1", state="visible")

            # Click on the "Organisation" checkbox
            logger.info("Clicking Organisation filter...")
            checkbox = page.locator("#applyAs-1")
            try:
                # Try clicking the label associated with the checkbox
                page.locator('label[for="applyAs-1"]').click(timeout=5000)
            except Exception as e:
                logger.warning(f"Label click failed, using JavaScript fallback: {e}")
                # If label click fails, use JavaScript to click the checkbox directly
                checkbox.evaluate("element => element.click()")

            # Wait a moment for the filter to apply
            page.wait_for_timeout(1000)

            if take_screenshots:
                page.screenshot(
                    path=str(
                        SCREENSHOT_DIR
                        / f"screenshot_{timestamp}_02_after_checkbox_click.png"
                    ),
                    full_page=True,
                )

            # Wait for grant cards to be visible
            logger.info("Waiting for grant cards to load...")
            page.wait_for_selector('[class*="itemsContainer"]', state="visible")

            if take_screenshots:
                page.screenshot(
                    path=str(
                        SCREENSHOT_DIR
                        / f"screenshot_{timestamp}_03_grant_cards_visible.png"
                    ),
                    full_page=True,
                )

            # Extract links for grants that are not closed
            logger.info("Extracting grant links...")
            if job_id:
                update_refresh_status(
                    job_id,
                    RefreshPhase.EXTRACTING_LINKS,
                    message="Extracting grant links",
                )
            grant_links = get_links(page)
            logger.info(f"Found {len(grant_links)} open grant(s)")

            for grant in grant_links:
                logger.info(f"  - {grant['button_text']}: {grant['url']}")
                grant_urls.append(grant["url"])

            if job_id:
                update_refresh_status(
                    job_id,
                    RefreshPhase.SCRAPING_DETAILS,
                    total_found=len(grant_links),
                    message=f"Found {len(grant_links)} grants, starting detailed scraping",
                )

            if take_screenshots:
                page.screenshot(
                    path=str(
                        SCREENSHOT_DIR / f"screenshot_{timestamp}_04_final_state.png"
                    ),
                    full_page=True,
                )

            # Save to database if requested
            grants_saved = 0
            if save_to_db and grant_links:
                logger.info("Saving grants to database...")
                if job_id:
                    update_refresh_status(
                        job_id,
                        RefreshPhase.SAVING_TO_DB,
                        total_found=len(grant_links),
                        message="Saving grants to database",
                    )
                try:
                    saved_grants = save_grants_to_db(
                        page, grant_links, use_text=True, job_id=job_id
                    )
                    grants_saved = len(saved_grants)
                    logger.info(f"Successfully saved {grants_saved} grants to database")
                except Exception as e:
                    error_msg = f"Error saving grants to database: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            browser.close()
            logger.info("Scraping completed successfully")

            result = {
                "total_found": len(grant_links),
                "grants_saved": grants_saved,
                "grant_urls": grant_urls,
                "errors": errors,
            }

            # Update final status
            if job_id:
                from app.services.refresh_status import complete_refresh

                complete_refresh(
                    job_id, len(grant_links), grants_saved, grant_urls, errors
                )

            return result

    except Exception as e:
        error_msg = f"Error during scraping: {e}"
        logger.error(error_msg, exc_info=True)
        errors.append(error_msg)

        # Update error status
        if job_id:
            update_refresh_status(job_id, RefreshPhase.ERROR, error=error_msg)

        return {
            "total_found": 0,
            "grants_saved": 0,
            "grant_urls": grant_urls,
            "errors": errors,
        }
