# Grant Scraper API

A FastAPI-based backend service for scraping, filtering, and analyzing grants from the Singapore Government Grants portal.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [API Routes](#api-routes)
  - [Pipeline Routes](#pipeline-routes)
  - [Grants Routes](#grants-routes)
  - [Results Routes](#results-routes)
  - [Health Check](#health-check)
- [Setup](#setup)
- [Configuration](#configuration)
- [Logging](#logging)

## Overview

This API provides a complete pipeline for:
1. **Scraping** open grants from the Singapore Government Grants portal
2. **Filtering** grants based on initiative criteria
3. **Analyzing** grants using AI (Google Gemini) for match quality
4. **Storing** and retrieving analysis results

## Architecture

```
app/
├── routers/           # API route handlers
│   ├── pipeline.py    # Pipeline operations
│   ├── grants.py      # Grant scraping/management
│   └── results.py     # Results retrieval
├── services/          # Business logic
│   ├── pipeline_service.py  # Pipeline orchestration
│   ├── scraper.py           # Web scraping
│   ├── gemini_service.py    # AI analysis
│   └── file_service.py      # File downloads
├── access/            # Database operations
├── models/            # SQLAlchemy models
└── core/              # Configuration
```

## API Routes

Base URL: `http://localhost:8000`

### Pipeline Routes

Routes for running and monitoring the grant filtering pipeline.

**Prefix:** `/pipeline`

---

#### 1. Start Pipeline

Trigger the grant filtering pipeline for an initiative.

```http
POST /pipeline/filter-grants/{initiative_id}
```

**Parameters:**
- `initiative_id` (path, required): ID of the initiative to filter grants for
- `threshold` (query, optional): Minimum preliminary rating (0-100) to include in deep analysis. Default: 50

**Response:**
```json
{
  "message": "Pipeline started",
  "initiative_id": 123,
  "threshold": 50,
  "status_endpoint": "/pipeline/get-status?initiative_id=123"
}
```

**Process:**
1. Load initiative and organization from database
2. Calculate preliminary ratings for all grants (Phase 1)
3. Filter grants above threshold
4. Deep scrape filtered grants (Phase 2)
5. Analyze with Gemini AI and save results

---

#### 2. Get Pipeline Status

Check the current status of a running pipeline.

```http
GET /pipeline/get-status?initiative_id={id}
```

**Parameters:**
- `initiative_id` (query, required): ID of the initiative

**Response (Calculating Phase):**
```json
{
  "status": "calculating",
  "remaining_calls": 15
}
```

**Response (Deep Scraping Phase):**
```json
{
  "status": "deep_scraping",
  "total_grants": 8,
  "remaining_calls": 8
}
```

**Response (Analyzing Phase):**
```json
{
  "status": "analyzing",
  "total_grants": 8,
  "current_grant": 3,
  "remaining_calls": 5
}
```

**Response (Completed):**
```json
{
  "status": "completed",
  "message": "Pipeline completed successfully",
  "total_grants": 25
}
```

**Response (Error):**
```json
{
  "status": "error",
  "error": "Error message here"
}
```

**Response (Idle):**
```json
{
  "status": "idle",
  "message": "No pipeline running for this initiative"
}
```

**Status Values:**
- `idle`: No pipeline running
- `calculating`: Phase 1 - Computing preliminary ratings
- `deep_scraping`: Phase 2 - Scraping additional grant information
- `analyzing`: Phase 2 - Analyzing with Gemini AI
- `completed`: Pipeline finished successfully
- `error`: Pipeline encountered an error

---

#### 3. Stream Pipeline Status (SSE)

Real-time status updates via Server-Sent Events.

```http
GET /pipeline/get-status-stream/{initiative_id}
```

**Parameters:**
- `initiative_id` (path, required): ID of the initiative

**Response Type:** `text/event-stream`

**Event Format:**
```
data: {"status": "calculating", "remaining_calls": 15}

data: {"status": "analyzing", "total_grants": 8, "current_grant": 2, "remaining_calls": 6}

data: {"status": "completed", "message": "Pipeline completed successfully"}
```

The stream automatically closes when the pipeline completes or encounters an error.

**Frontend Example:**
```javascript
const eventSource = new EventSource('/pipeline/get-status-stream/123');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Status:', data.status);
  if (data.status === 'completed' || data.status === 'error') {
    eventSource.close();
  }
};
```

---

### Grants Routes

Routes for scraping and managing grant data.

**Prefix:** `/grants`

---

#### 4. Start Grant Refresh

Start a background job to scrape the latest open grants from the government portal.

```http
POST /grants/refresh
```

**Parameters:**
- `headless` (query, optional): Run browser in headless mode. Default: `true`
- `take_screenshots` (query, optional): Save debug screenshots. Default: `false`

**Request Example:**
```http
POST /grants/refresh?headless=true&take_screenshots=false
```

**Response (Job Started):**
```json
{
  "job_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "message": "Grant refresh job started",
  "status_endpoint": "/grants/refresh-status/a1b2c3d4-5678-90ab-cdef-1234567890ab"
}
```

**Process:**
1. Returns immediately with a unique `job_id`
2. Scraping runs in background (~1 minute)
3. Use the `job_id` to check status

**Note:** This endpoint returns immediately. The actual scraping happens asynchronously. Use the refresh status endpoint to monitor progress.

---

#### 5. Get Grant Refresh Status

Check the status of a grant refresh job.

```http
GET /grants/refresh-status/{job_id}
```

**Parameters:**
- `job_id` (path, required): The job ID returned from `/grants/refresh`

**Response (In Progress):**
```json
{
  "job_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "phase": "scraping_details",
  "total_found": 15,
  "message": "Found 15 grants, starting detailed scraping",
  "updated_at": "2024-01-15T10:23:45.123456"
}
```

**Response (Completed):**
```json
{
  "job_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "phase": "completed",
  "total_found": 15,
  "grants_saved": 15,
  "grant_urls": [
    "https://oursggrants.gov.sg/grants/...",
    "..."
  ],
  "errors": [],
  "completed_at": "2024-01-15T10:24:30.123456"
}
```

**Response (Error):**
```json
{
  "job_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "phase": "error",
  "error": "Error message here",
  "updated_at": "2024-01-15T10:23:50.123456"
}
```

**Phase Values:**
- `starting`: Initializing browser
- `navigating`: Loading grants page
- `extracting_links`: Finding open grants
- `scraping_details`: Extracting grant details
- `saving_to_db`: Saving to database
- `completed`: Job finished successfully
- `error`: Job failed

**Scraping Process:**
1. Navigate to grants listing page
2. Apply "Organisation" filter
3. Extract links for open grants (automatically filters out closed grants)
4. Visit each grant page and extract details
5. Save/update grants in database (matched by URL)

**Note:** Closed grants are automatically filtered out based on:
- "Closed" status indicators on the website
- "Applications closed" text

---

### Results Routes

Routes for retrieving grant analysis results.

**Prefix:** `/results`

---

#### 5. Get Results

Retrieve all grant analysis results for an initiative.

```http
GET /results/{initiative_id}
```

**Parameters:**
- `initiative_id` (path, required): ID of the initiative

**Response:**
```json
{
  "initiative_id": 123,
  "count": 25,
  "results": [
    {
      "grant_id": 1,
      "initiative_id": 123,
      "prelim_rating": 75,
      "grant_description": "Grant for social initiatives...",
      "criteria": [
        "Must be a registered charity",
        "Serve beneficiaries in Singapore"
      ],
      "grant_amount": "$50,000 - $200,000",
      "match_rating": 85,
      "uncertainty_rating": 15,
      "deadline": "2024-12-31T23:59:59",
      "sources": ["https://..."],
      "sponsor_name": "Ministry of XYZ",
      "sponsor_description": "Government ministry...",
      "explanations": {
        "match_rating": "High alignment with initiative goals...",
        "uncertainty_rating": "Some eligibility criteria unclear..."
      }
    },
    ...
  ]
}
```

**Field Descriptions:**
- `prelim_rating`: Initial rating (0-100) from Phase 1
- `match_rating`: Final match quality (0-100) from Phase 2 analysis
- `uncertainty_rating`: Confidence level (0-100), lower is better
- `grant_amount`: Funding amount range (string for flexibility)
- `deadline`: Application deadline (ISO 8601 format)
- `criteria`: List of eligibility requirements
- `explanations`: Detailed reasoning for ratings

---

### Health Check

Simple health check endpoint.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

---

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL database
- Google Gemini API key

### Installation

1. **Clone the repository and navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Set up environment variables:**
   
   Create a `.env` file in the backend directory:
   ```env
   # Database
   DB_URL=postgresql://user:password@localhost:5432/grantscraper
   
   # Gemini API
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Logging (optional)
   LOG_LEVEL=INFO
   LOG_FILE=/path/to/logfile.log  # Optional file logging
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start the server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_URL` | ✅ Yes | - | PostgreSQL connection string |
| `GEMINI_API_KEY` | ✅ Yes | - | Google Gemini API key |
| `LOG_LEVEL` | ❌ No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE` | ❌ No | - | Optional log file path |

### Rating Threshold

The pipeline filtering threshold can be adjusted per request:
- Default: 50 (out of 100)
- Configurable via `threshold` parameter in `/pipeline/filter-grants`

---

## Logging

The API includes comprehensive logging at all levels:

### Log Levels

- **DEBUG**: Detailed step-by-step operations (grant processing, API calls)
- **INFO**: Major operations (pipeline start/completion, route calls)
- **WARNING**: Non-fatal issues (partial failures, deprecated warnings)
- **ERROR**: Failures (exceptions, missing data, pipeline errors)

### Log Format

```
2024-01-15 10:23:45 - app.routers.pipeline - INFO - Starting pipeline for initiative 123
2024-01-15 10:23:46 - app.services.scraper - INFO - Found 15 open grants
2024-01-15 10:24:12 - app.services.gemini_service - DEBUG - Analyzing grant 42
```

### Configuration

Set the log level in your `.env` file:
```env
LOG_LEVEL=DEBUG  # For development
LOG_LEVEL=INFO   # For production
```

Enable file logging:
```env
LOG_FILE=/var/log/grantscraper/api.log
```

### Log Locations

- **Console**: All logs output to stdout by default
- **File**: Optional file logging when `LOG_FILE` is set
- **Third-party libraries**: Set to WARNING level to reduce noise

---

## Typical Workflow

1. **Refresh grants** (do this first or periodically):
   ```bash
   curl -X POST "http://localhost:8000/grants/refresh"
   ```

2. **Create organizations and initiatives** (via database or separate endpoints)

3. **Run pipeline for an initiative**:
   ```bash
   curl -X POST "http://localhost:8000/pipeline/filter-grants/123?threshold=60"
   ```

4. **Monitor progress**:
   ```bash
   curl "http://localhost:8000/pipeline/get-status?initiative_id=123"
   ```

5. **Get results**:
   ```bash
   curl "http://localhost:8000/results/123"
   ```

---

## API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `404`: Resource not found (initiative, grant)
- `500`: Internal server error

Error responses include detailed messages:
```json
{
  "detail": "Initiative not found"
}
```

---

## Development

### Project Structure

```
backend/
├── app/
│   ├── access/              # Database CRUD operations
│   ├── core/                # Configuration and setup
│   ├── models/              # SQLAlchemy models
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic
│   └── main.py              # FastAPI application
├── alembic/                 # Database migrations
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Adding New Routes

1. Create a new router file in `app/routers/`
2. Add logging using `logger = logging.getLogger(__name__)`
3. Export router in `app/routers/__init__.py`
4. Include router in `app/main.py`

---

## License

[Your License Here]

---

## Support

For issues or questions, please contact the development team.

