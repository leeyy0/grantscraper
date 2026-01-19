/**
 * Backend API utility functions
 */

const BACKEND_API_URL =
  process.env.NEXT_PUBLIC_BACKEND_API_URL || "http://localhost:8000"

export interface FilterGrantsResponse {
  message: string
  initiative_id: number
  threshold: number
  status_endpoint: string
}

export interface PipelineStatusResponse {
  status:
    | "calculating"
    | "filtering"
    | "deep_scraping"
    | "analyzing"
    | "completed"
    | "error"
  initiative_id: number
  total_grants?: number
  processed_grants?: number
  message?: string
  error?: string
}

export interface RefreshGrantsResponse {
  job_id: string
  message: string
  status_endpoint: string
}

export interface RefreshStatusResponse {
  job_id: string
  phase: string
  total_found?: number
  current_grant?: number
  grants_saved?: number
  message?: string
  error?: string
}

/**
 * Trigger the grant filtering pipeline for an initiative
 * @param initiativeId - ID of the initiative to filter grants for
 * @param threshold - Minimum preliminary rating (0-100) to include in deep analysis. Default: 61
 */
export async function triggerFilterGrants(
  initiativeId: number,
  threshold: number = 61,
): Promise<FilterGrantsResponse> {
  const url = `${BACKEND_API_URL}/pipeline/filter-grants/${initiativeId}?threshold=${threshold}`

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(
      errorData.detail || `Failed to trigger pipeline: ${response.statusText}`,
    )
  }

  return response.json()
}

/**
 * Check the current status of a running pipeline
 * @param initiativeId - ID of the initiative
 */
export async function getPipelineStatus(
  initiativeId: number,
): Promise<PipelineStatusResponse> {
  const url = `${BACKEND_API_URL}/pipeline/get-status?initiative_id=${initiativeId}`

  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(
      errorData.detail ||
        `Failed to get pipeline status: ${response.statusText}`,
    )
  }

  return response.json()
}

/**
 * Get the SSE URL for streaming pipeline status updates
 * @param initiativeId - ID of the initiative
 * @returns SSE URL for the pipeline status stream
 */
export function getPipelineStreamUrl(initiativeId: number): string {
  return `${BACKEND_API_URL}/pipeline/get-status-stream/${initiativeId}`
}

/**
 * Trigger a grant refresh job to scrape the latest grants
 * @param headless - Run browser in headless mode (default: true)
 * @param takeScreenshots - Save debug screenshots during scraping (default: false)
 * @returns Job information including job_id and status_endpoint
 */
export async function triggerRefreshGrants(
  headless: boolean = true,
  takeScreenshots: boolean = false,
): Promise<RefreshGrantsResponse> {
  const url = `${BACKEND_API_URL}/grants/refresh?headless=${headless}&take_screenshots=${takeScreenshots}`

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(
      errorData.detail ||
        `Failed to trigger grant refresh: ${response.statusText}`,
    )
  }

  return response.json()
}

/**
 * Check the current status of a grant refresh job
 * @param jobId - Job ID returned from triggerRefreshGrants
 * @returns Current status of the refresh job
 */
export async function getRefreshStatus(
  jobId: string,
): Promise<RefreshStatusResponse> {
  const url = `${BACKEND_API_URL}/grants/refresh-status/${jobId}`

  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(
      errorData.detail ||
        `Failed to get refresh status: ${response.statusText}`,
    )
  }

  return response.json()
}

/**
 * Get the SSE URL for streaming refresh status updates
 * @param jobId - Job ID returned from triggerRefreshGrants
 * @returns SSE URL for the refresh status stream
 */
export function getRefreshStreamUrl(jobId: string): string {
  return `${BACKEND_API_URL}/grants/refresh-status-stream/${jobId}`
}
