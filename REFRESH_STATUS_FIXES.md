# Refresh Status Progress Bar Fixes

## Issues Found and Fixed

### 1. Phase Name Mismatches (Frontend ↔ Backend)
**Problem**: The backend and frontend used different phase names, causing the status mapping to fail.

- Backend: `scraping_details` → Frontend expected: `scraping_grants`
- Backend: `saving_to_db` → Frontend expected: `saving`

**Fix**: Updated frontend status mapping to handle both old and new phase names for backwards compatibility.

**File**: `frontend/components/refresh-status.tsx`
- Added mappings for `scraping_details → scraping_grants` and `saving_to_db → saving`

---

### 2. No Per-Grant Progress Updates
**Problem**: The scraper processed all grants in bulk without sending progress updates for individual grants, so `current_grant` was never updated and the progress bar stayed static.

**Fix**: Updated the scraping pipeline to send progress updates after processing each grant.

**Files Modified**:

#### `backend/app/services/scraper.py`
1. **`get_grant_details()`**: 
   - Added `job_id` parameter
   - Added progress update after each grant is scraped
   - Sends `current_grant` counter (1, 2, 3, ...) and `total_found`

2. **`get_grant_details_as_models()`**:
   - Added `job_id` parameter
   - Passes `job_id` to `get_grant_details()`

3. **`save_grants_to_db()`**:
   - Added `job_id` parameter
   - Passes `job_id` to `get_grant_details_as_models()`
   - Added progress updates before and after database save

4. **`scrape_and_refresh_grants()`**:
   - Updated call to `save_grants_to_db()` to pass `job_id`

---

### 3. Status Update Overwrites
**Problem**: The `update_refresh_status()` function was overwriting all fields (including those set to `None`), which could lose existing progress data.

**Fix**: Modified to only update fields that are explicitly provided (not `None`), preserving existing values.

**File**: `backend/app/services/refresh_status.py`
- Changed `update_refresh_status()` to conditionally update only non-None fields

---

## How Progress Updates Now Work

### Flow:
1. **Starting**: Browser initialization
2. **Navigating**: Navigate to grants portal
3. **Extracting Links**: Find open grants
4. **Scraping Details**: 
   - For each grant (1 to N):
     - Update status with `current_grant=i, total_found=N`
     - Scrape grant details
5. **Saving to DB**:
   - Update status with `grants_saved=0`
   - Save all grants to database
   - Update status with final `grants_saved` count
6. **Completed**: Job finished

### Progress Bar Calculation:
The frontend calculates progress as:
- If `total_found` and `current_grant` are set: `(current_grant / total_found) * 100`
- Otherwise, estimates based on phase (starting=5%, navigating=15%, etc.)

---

## Testing Checklist

- [ ] Start a grant refresh
- [ ] Verify progress bar updates during scraping (should increment with each grant)
- [ ] Verify status text changes correctly through all phases
- [ ] Verify "Currently scraping: Grant X" counter updates
- [ ] Verify final completion shows correct counts
- [ ] Check SSE stream in browser DevTools Network tab
