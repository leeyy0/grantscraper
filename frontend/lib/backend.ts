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
    | "calculating_phase1"
    | "filtering"
    | "scraping_phase2"
    | "analyzing"
    | "completed"
    | "error"
  initiative_id: number
  total_grants?: number
  processed_grants?: number
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
