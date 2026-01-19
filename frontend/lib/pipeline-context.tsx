"use client"

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
} from "react"

const PIPELINE_STORAGE_KEY = "running_pipeline"

export interface PipelineStatus {
  status:
    | "calculating_phase1"
    | "filtering"
    | "scraping_phase2"
    | "analyzing"
    | "completed"
    | "error"
    | "idle"
  initiative_id: number | null
  initiative_title?: string
  total_grants?: number
  processed_grants?: number
  current_grant?: number
  remaining_calls?: number
  message?: string
  error?: string
}

interface PipelineContextType {
  pipelineStatus: PipelineStatus
  startPipeline: (initiativeId: number, initiativeTitle: string) => void
  updatePipelineStatus: (status: Partial<PipelineStatus>) => void
  clearPipeline: () => void
  resumePipeline: (initiativeId: number, initiativeTitle: string) => void
}

const PipelineContext = createContext<PipelineContextType | undefined>(
  undefined,
)

export function PipelineProvider({ children }: { children: React.ReactNode }) {
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus>({
    status: "idle",
    initiative_id: null,
  })

  // Save pipeline state to localStorage when it changes
  useEffect(() => {
    if (
      pipelineStatus.initiative_id &&
      pipelineStatus.status !== "idle" &&
      pipelineStatus.status !== "completed"
    ) {
      localStorage.setItem(
        PIPELINE_STORAGE_KEY,
        JSON.stringify({
          initiative_id: pipelineStatus.initiative_id,
          initiative_title: pipelineStatus.initiative_title,
          status: pipelineStatus.status,
        }),
      )
    } else {
      // Clear localStorage when pipeline completes or is idle
      localStorage.removeItem(PIPELINE_STORAGE_KEY)
    }
  }, [pipelineStatus.initiative_id, pipelineStatus.status, pipelineStatus.initiative_title])

  const startPipeline = useCallback(
    (initiativeId: number, initiativeTitle: string) => {
      setPipelineStatus({
        status: "calculating_phase1",
        initiative_id: initiativeId,
        initiative_title: initiativeTitle,
      })
    },
    [],
  )

  const resumePipeline = useCallback(
    (initiativeId: number, initiativeTitle: string) => {
      setPipelineStatus({
        status: "calculating_phase1",
        initiative_id: initiativeId,
        initiative_title: initiativeTitle,
      })
    },
    [],
  )

  const updatePipelineStatus = useCallback(
    (status: Partial<PipelineStatus>) => {
      setPipelineStatus((prev) => ({ ...prev, ...status }))
    },
    [],
  )

  const clearPipeline = useCallback(() => {
    setPipelineStatus({
      status: "idle",
      initiative_id: null,
    })
    localStorage.removeItem(PIPELINE_STORAGE_KEY)
  }, [])

  return (
    <PipelineContext.Provider
      value={{
        pipelineStatus,
        startPipeline,
        updatePipelineStatus,
        clearPipeline,
        resumePipeline,
      }}
    >
      {children}
    </PipelineContext.Provider>
  )
}

/**
 * Get stored pipeline info from localStorage
 */
export function getStoredPipeline(): {
  initiative_id: number
  initiative_title: string
  status: string
} | null {
  if (typeof window === "undefined") return null

  try {
    const stored = localStorage.getItem(PIPELINE_STORAGE_KEY)
    return stored ? JSON.parse(stored) : null
  } catch (error) {
    console.error("Failed to parse stored pipeline:", error)
    return null
  }
}

export function usePipeline() {
  const context = useContext(PipelineContext)
  if (context === undefined) {
    throw new Error("usePipeline must be used within a PipelineProvider")
  }
  return context
}
