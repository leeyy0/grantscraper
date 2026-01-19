"use client"

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
} from "react"

const REFRESH_STORAGE_KEY = "running_refresh"

export interface RefreshStatus {
  status:
    | "starting"
    | "navigating"
    | "extracting_links"
    | "scraping_grants"
    | "saving"
    | "completed"
    | "error"
    | "idle"
  job_id: string | null
  phase?: string
  total_found?: number
  current_grant?: number
  grants_saved?: number
  message?: string
  error?: string
}

interface RefreshContextType {
  refreshStatus: RefreshStatus
  startRefresh: (jobId: string) => void
  updateRefreshStatus: (status: Partial<RefreshStatus>) => void
  clearRefresh: () => void
}

const RefreshContext = createContext<RefreshContextType | undefined>(undefined)

export function RefreshProvider({ children }: { children: React.ReactNode }) {
  const [refreshStatus, setRefreshStatus] = useState<RefreshStatus>({
    status: "idle",
    job_id: null,
  })

  // Save refresh state to localStorage when it changes
  useEffect(() => {
    if (
      refreshStatus.job_id &&
      refreshStatus.status !== "idle" &&
      refreshStatus.status !== "completed"
    ) {
      localStorage.setItem(
        REFRESH_STORAGE_KEY,
        JSON.stringify({
          job_id: refreshStatus.job_id,
          status: refreshStatus.status,
        }),
      )
    } else {
      // Clear localStorage when refresh completes or is idle
      localStorage.removeItem(REFRESH_STORAGE_KEY)
    }
  }, [refreshStatus.job_id, refreshStatus.status])

  const startRefresh = useCallback((jobId: string) => {
    setRefreshStatus({
      status: "starting",
      job_id: jobId,
    })
  }, [])

  const updateRefreshStatus = useCallback((status: Partial<RefreshStatus>) => {
    setRefreshStatus((prev) => ({ ...prev, ...status }))
  }, [])

  const clearRefresh = useCallback(() => {
    setRefreshStatus({
      status: "idle",
      job_id: null,
    })
    localStorage.removeItem(REFRESH_STORAGE_KEY)
  }, [])

  return (
    <RefreshContext.Provider
      value={{
        refreshStatus,
        startRefresh,
        updateRefreshStatus,
        clearRefresh,
      }}
    >
      {children}
    </RefreshContext.Provider>
  )
}

/**
 * Get stored refresh info from localStorage
 */
export function getStoredRefresh(): {
  job_id: string
  status: string
} | null {
  if (typeof window === "undefined") return null

  try {
    const stored = localStorage.getItem(REFRESH_STORAGE_KEY)
    return stored ? JSON.parse(stored) : null
  } catch (error) {
    console.error("Failed to parse stored refresh:", error)
    return null
  }
}

export function useRefresh() {
  const context = useContext(RefreshContext)
  if (context === undefined) {
    throw new Error("useRefresh must be used within a RefreshProvider")
  }
  return context
}
