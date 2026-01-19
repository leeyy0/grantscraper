"use client"

import { useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import {
  Loader2,
  CheckCircle2,
  XCircle,
  Sparkles,
  X,
  Search,
  FileSearch,
  Brain,
} from "lucide-react"
import { usePipeline } from "@/lib/pipeline-context"
import { toast } from "sonner"

const BACKEND_API_URL =
  process.env.NEXT_PUBLIC_BACKEND_API_URL || "http://localhost:8000"

export function PipelineStatus() {
  const { pipelineStatus, updatePipelineStatus, clearPipeline } = usePipeline()
  const eventSourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    // Only connect when we have an initiative and pipeline is running
    const shouldConnect =
      pipelineStatus.initiative_id &&
      pipelineStatus.status !== "idle" &&
      pipelineStatus.status !== "completed" &&
      pipelineStatus.status !== "error"

    if (!shouldConnect) {
      // Clean up existing connection if status changed
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
      return
    }

    // Create SSE connection
    const sseUrl = `${BACKEND_API_URL}/pipeline/get-status-stream/${pipelineStatus.initiative_id}`
    const eventSource = new EventSource(sseUrl)
    eventSourceRef.current = eventSource

    eventSource.onmessage = (event) => {
      try {
        const parsedData = JSON.parse(event.data)
        updatePipelineStatus(parsedData)

        // Show toast on completion
        if (parsedData.status === "completed") {
          toast.success("Pipeline completed!", {
            description: parsedData.message || "All grants have been analyzed",
          })
        } else if (parsedData.status === "error") {
          toast.error("Pipeline failed", {
            description: parsedData.error || "An error occurred during processing",
          })
        }
      } catch (error) {
        console.error("Failed to parse SSE message:", error)
      }
    }

    eventSource.onerror = (error) => {
      console.error("SSE connection error:", error)
      updatePipelineStatus({
        status: "error",
        error: "Connection to pipeline status stream failed",
      })
      eventSource.close()
    }

    // Cleanup function
    return () => {
      eventSource.close()
      eventSourceRef.current = null
    }
  }, [pipelineStatus.initiative_id, pipelineStatus.status, updatePipelineStatus])

  // Rest of your component remains the same...
  if (pipelineStatus.status === "idle" || !pipelineStatus.initiative_id) {
    return null
  }

  const getStatusIcon = () => {
    switch (pipelineStatus.status) {
      case "calculating":
        return <Search className="h-5 w-5" />
      case "filtering":
        return <FileSearch className="h-5 w-5" />
      case "deep_scraping":
        return <Loader2 className="h-5 w-5 animate-spin" />
      case "analyzing":
        return <Brain className="h-5 w-5" />
      case "completed":
        return <CheckCircle2 className="h-5 w-5 text-green-500" />
      case "error":
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return <Sparkles className="h-5 w-5" />
    }
  }

  const getStatusText = () => {
    switch (pipelineStatus.status) {
      case "calculating":
        return "Calculating preliminary ratings..."
      case "filtering":
        return "Filtering grants..."
      case "deep_scraping":
        return "Deep scraping filtered grants..."
      case "analyzing":
        return "Analyzing with AI..."
      case "completed":
        return "Analysis complete!"
      case "error":
        return "Pipeline failed"
      default:
        return "Processing..."
    }
  }

  const getStatusColor = () => {
    switch (pipelineStatus.status) {
      case "completed":
        return "default"
      case "error":
        return "destructive"
      default:
        return "secondary"
    }
  }

  const getProgress = () => {
    if (pipelineStatus.total_grants && pipelineStatus.processed_grants) {
      return (
        (pipelineStatus.processed_grants / pipelineStatus.total_grants) * 100
      )
    }
    // Estimate progress based on status
    switch (pipelineStatus.status) {
      case "calculating":
        return 10
      case "filtering":
        return 30
      case "deep_scraping":
        return 50
      case "analyzing":
        return 75
      case "completed":
        return 100
      default:
        return 0
    }
  }

  return (
    <Card className="mx-2 mb-4">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <CardTitle className="text-base">Pipeline Status</CardTitle>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="-mt-1 -mr-1 h-6 w-6"
            onClick={clearPipeline}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <p className="mb-1 text-sm font-medium">
            {pipelineStatus.initiative_title}
          </p>
          <Badge variant={getStatusColor()} className="text-xs">
            {getStatusText()}
          </Badge>
        </div>

        <Progress value={getProgress()} className="h-2" />

        <div className="text-muted-foreground space-y-1 text-xs">
          {pipelineStatus.status === "calculating" && (
            <div className="mb-2 rounded bg-blue-50 p-2 text-blue-700 dark:bg-blue-950 dark:text-blue-300">
              <p className="text-xs">
                Phase 1: Quick preliminary screening of all grants
              </p>
            </div>
          )}
          {(pipelineStatus.status === "deep_scraping" ||
            pipelineStatus.status === "analyzing") && (
            <div className="mb-2 rounded bg-purple-50 p-2 text-purple-700 dark:bg-purple-950 dark:text-purple-300">
              <p className="text-xs">
                Phase 2: Deep analysis of filtered grants
              </p>
            </div>
          )}
          {pipelineStatus.total_grants && (
            <div className="flex justify-between">
              <span>
                {pipelineStatus.status === "calculating"
                  ? "Screening:"
                  : "Filtered grants:"}
              </span>
              <span className="font-medium">{pipelineStatus.total_grants}</span>
            </div>
          )}
          {pipelineStatus.processed_grants !== undefined && (
            <div className="flex justify-between">
              <span>Processed:</span>
              <span className="font-medium">
                {pipelineStatus.processed_grants}
              </span>
            </div>
          )}
          {pipelineStatus.current_grant !== undefined && (
            <div className="flex justify-between">
              <span>Current:</span>
              <span className="font-medium">
                Grant {pipelineStatus.current_grant}
              </span>
            </div>
          )}
          {pipelineStatus.remaining_calls !== undefined && (
            <div className="flex justify-between">
              <span>
                {pipelineStatus.status === "calculating"
                  ? "Preliminary scraping calls left:"
                  : "API calls remaining:"}
              </span>
              <span className="font-medium">
                {pipelineStatus.remaining_calls}
              </span>
            </div>
          )}
        </div>

        {pipelineStatus.message && (
          <p className="text-muted-foreground border-t pt-2 text-xs">
            {pipelineStatus.message}
          </p>
        )}

        {pipelineStatus.error && (
          <p className="border-t pt-2 text-xs text-red-500">
            Error: {pipelineStatus.error}
          </p>
        )}
      </CardContent>
    </Card>
  )
}