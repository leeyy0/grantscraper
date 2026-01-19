# GrantScraper Frontend

This is the frontend application for **GrantScraper**, built to help non-profit organisations "pull" relevant grant information from the OurSG portal. It interacts with the FastAPI backend to visualize real-time scraping status and AI-matched grant results.

## 🛠️ Frontend Tech Stack

*   **Framework**: [Next.js 16](https://nextjs.org/) (App Router)
*   **Language**: TypeScript
*   **Styling**: [TailwindCSS 4](https://tailwindcss.com/)
*   **UI Library**: [shadcn/ui](https://ui.shadcn.com/) (based on Radix UI)
*   **Icons**: Lucide React
*   **Data Visualization**: Recharts
*   **State/Data Fetching**: React Server Components & Client Hooks

## 🚀 Getting Started

### 1. Prerequisites
*   Node.js 18.17 or later
*   pnpm (recommended)

### 2. Installation
```bash
cd frontend
pnpm install
```

### 3. Configuration
Create a `.env.local` file in the `frontend` directory with the following variables. 
> **Note**: These connect the frontend to your Supabase instance and the local Backend API.

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Backend API URL
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
```

### 4. Running Locally
Start the development server:
```bash
pnpm dev
```
Open [http://localhost:3000](http://localhost:3000) to view the application.

## 📂 Project Structure

*   `app/`: Next.js App Router pages and layouts.
    *   `configure/`: Organisation profile settings.
    *   `grants/`: View all scraped grants and trigger refreshing.
    *   `initiatives/`: Create and manage grant-seeking initiatives.
    *   `results/`: View AI-matched results for initiatives.
*   `components/`: Reusable React components.
    *   `ui/`: Base UI components (buttons, inputs, etc.).
*   `lib/`: Utilities and API clients (`backend.ts` for API calls).

## 🔑 Key Features
*   **Dashboard**: Overview of current initiatives and grant matches.
*   **Grant Refresh**: UI to trigger the backend scraper and view progress via real-time stream.
*   **Relevance Matching**: Detailed view of why a grant was matched, including "Funding Quantum" and "KPIs".
