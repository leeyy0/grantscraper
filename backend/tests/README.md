# Testing Guide

## Prerequisites

1. **Install dependencies** (including pytest):
   ```bash
   cd /home/yy/nus/grantscraper/backend
   uv sync --group dev
   ```

2. **Install Playwright browsers** (if not already installed):
   ```bash
   playwright install chromium
   ```

## Running Tests

### Run all tests
```bash
pytest tests/test_scraper.py -v
```

### Run a specific test
```bash
# Run the comprehensive test with all links and screenshots
pytest tests/test_scraper.py::test_get_grant_details_all_test_links -v -s

# Run a quick test (only 2 links, faster)
pytest tests/test_scraper.py::test_get_grant_details_returns_correct_structure -v -s

# Run the screenshot test
pytest tests/test_scraper.py::test_get_grant_details_with_screenshots -v -s
```

### Run with output (see print statements)
```bash
pytest tests/test_scraper.py -v -s
```

### Run in headless mode (faster, no browser window)
To run tests in headless mode, modify the `browser` fixture in `test_scraper.py`:
```python
browser = p.chromium.launch(headless=True)  # Change False to True
```

## Test Descriptions

1. **`test_get_grant_details_returns_correct_structure`**
   - Quick test (2 links)
   - Validates return structure

2. **`test_get_grant_details_extracts_content`**
   - Quick test (2 links)
   - Verifies content extraction

3. **`test_get_grant_details_with_screenshots`**
   - Medium test (3 links)
   - Takes screenshots for each grant

4. **`test_get_grant_details_handles_errors_gracefully`**
   - Tests error handling with invalid URL

5. **`test_get_grant_details_all_test_links`**
   - Comprehensive test (5 links)
   - Processes all test links and saves screenshots

## Screenshots

Screenshots are saved to: `.private/screenshots/`

Format: `grant_YYYYMMDD_HHMMSS_<index>_<grant_id>.png`

Example: `grant_20260115_011500_1_ssgacg.png`

## Troubleshooting

### "pytest: command not found"
```bash
uv sync --group dev
# Or activate your virtual environment first
```

### "Browser not found"
```bash
playwright install chromium
```

### Tests fail with timeout
- The website might be slow or down
- Try running tests one at a time
- Increase timeout in test file if needed

### Screenshots not saving
- Check that `.private/screenshots/` directory exists
- Check file permissions
- The directory is in `.gitignore` so screenshots won't be committed

