# GrantScraper

> **Problem Statement for Tsao Foundation**
>
> "How might non-profit organisations **'pull' information about grants from OurSG grants portal** that are relevant to them according to key criteria including issue area, scope of grant, KPIs, funding quantum, application due date, etcs. so that they can strengthen their financial sustainability?"

---

## 📋 Comprehensive Description

GrantScraper is an intelligent, automated solution designed to address the challenge faced by non-profit organisations in discovering relevant funding opportunities. Instead of manually navigating the OurSG Grants Portal and reviewing hundreds of grants, organisations can use GrantScraper to:

1.  **Automatically "Pull" Data**: The system uses a sophisticated web scraper to retrieve all open grants specifically available for organisations from the OurSG portal.
2.  **Intelligent Matching**: By leveraging Google Gemini AI, the platform analyzes the "pull" data against an organisation's specific profile (issue area, KPIs, etc.) to identify high-potential matches.
3.  **Strengthen Sustainability**: By reducing the administrative burden of search and increasing the precision of grant targeting, NPOs can focus their resources on delivery and sustainability.

This project implements a full-stack solution with a data ingestion pipeline, an AI matching engine, and a user-friendly dashboard for managing grant opportunities.

## 📚 Component Documentation
For specific details on setup, architecture, and API usage, please refer to the inner documentation:
*   [**Frontend Documentation**](./frontend/README.md) - UI components, routing, and client setup.
*   [**Backend Documentation**](./backend/README.md) - API endpoints, database schema, and deeper scraper logic.

---

## 🛠️ Tech Stack Requirement

### Frontend
*   **Framework**: Next.js 16 (React 19)
*   **Styling**: TailwindCSS 4
*   **UI Components**: shadcn/ui (Radix UI)
*   **Language**: TypeScript

### Backend
*   **Framework**: Python / FastAPI
*   **Package Manager**: uv
*   **Scraping**: Playwright
*   **AI Service**: Google Gemini API
*   **ORM**: SQLAlchemy

### Database & Services
*   **Database**: PostgreSQL (via Supabase)
*   **Migrations**: Alembic

---

## 🌟 Main Features

### 1. Automated Grant Scraping from OurSG Portal
The core "pull" mechanism is built on a robust Playwright-based scraper that ensures up-to-date information:
*   **Targeted Navigation**: Navigates directly to `oursggrants.gov.sg`.
*   **Smart Filtering**: automatically applies the "Organisation" filter to exclude individual grants.
*   **Status Detection**: Parses grant cards to identify and exclude "Closed" or "Applications closed" grants.
*   **Deep Extraction**: Visits each grant page to capture the full `card-body` text, including issuer details, funding quantum, and deadlines, preserving structure for AI analysis.

### 2. AI-Powered Relevance Analysis
*   **Preliminary Scoring**: Rapidly categorizes grants based on high-level fit.
*   **Deep Analysis**: Uses Gemini 1.5 Pro to evaluate specific criteria like "Funding Quantum" and "KPI alignment".

### 3. Organisation Dashboard
*   **Profile Management**: configure organisation details, mission, and KPIs.
*   **Real-time Updates**: Monitor the scraping job status live via Server-Sent Events (SSE).

---

## ⚙️ Configuration & Getting Started

### Prerequisites
*   Node.js 18+ (Frontend)
*   Python 3.12+ (Backend)
*   Supabase Account (Database)
*   Google Gemini API Key

### Backend Configuration
1.  Navigate to `backend/`.
2.  Create a `.env` file based on `.env.example`:
    ```env
    DB_URL=postgresql://user:password@host:5432/db
    GEMINI_API_KEY=your_gemini_key
    ```
3.  Install dependencies: `uv sync`
4.  Run migrations: `alembic upgrade head`
5.  Start server: `uvicorn app.main:app --reload`

### Frontend Configuration
1.  Navigate to `frontend/`.
2.  Create a `.env.local` file:
    ```env
    NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
    NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key
    NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
    ```
3.  Install dependencies: `pnpm install`
4.  Start dev server: `pnpm dev`
