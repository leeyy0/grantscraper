"use client"

import { useEffect } from "react"
import { useSSE } from "react-eventsource"
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

  // Determine if we should connect to SSE
  const shouldConnect =
    pipelineStatus.initiative_id &&
    pipelineStatus.status !== "idle" &&
    pipelineStatus.status !== "completed" &&
    pipelineStatus.status !== "error"

  // Build SSE URL dynamically (empty string disables connection)
  const sseUrl: string = shouldConnect
    ? `${BACKEND_API_URL}/pipeline/get-status-stream/${pipelineStatus.initiative_id}`
    : ""

  // Use react-eventsource hook
  const { readyState, close } = useSSE({
    url: sseUrl,
    onMessage: (message) => {
      try {
        const parsedData = JSON.parse(message.data)
        updatePipelineStatus(parsedData)

        // Show toast on completion
        if (parsedData.status === "completed") {
          toast.success("Pipeline completed!", {
            description:
              parsedData.message || "All grants have been analyzed",
          })
        } else if (parsedData.status === "error") {
          toast.error("Pipeline failed", {
            description:
              parsedData.error || "An error occurred during processing",
          })
        }
      } catch (error) {
        console.error("Failed to parse SSE message:", error)
      }
    },
    onError: (error) => {
      console.error("SSE connection error:", error)
      updatePipelineStatus({
        status: "error",
        error: "Connection to pipeline status stream failed",
      })
    },
  })

  // Close connection when pipeline completes or errors
  useEffect(() => {
    if (
      pipelineStatus.status === "completed" ||
      pipelineStatus.status === "error"
    ) {
      close()
    }
  }, [pipelineStatus.status, close])

  if (pipelineStatus.status === "idle" || !pipelineStatus.initiative_id) {
    return null
  }

  const getStatusIcon = () => {
    switch (pipelineStatus.status) {
      case "calculating_phase1":
        return <Search className="h-5 w-5" />
      case "filtering":
        return <FileSearch className="h-5 w-5" />
      case "scraping_phase2":
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
      case "calculating_phase1":
        return "Calculating preliminary ratings..."
      case "filtering":
        return "Filtering grants..."
      case "scraping_phase2":
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
      return (pipelineStatus.processed_grants / pipelineStatus.total_grants) * 100
    }
    // Estimate progress based on status
    switch (pipelineStatus.status) {
      case "calculating_phase1":
        return 10
      case "filtering":
        return 30
      case "scraping_phase2":
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
            className="h-6 w-6 -mt-1 -mr-1"
            onClick={clearPipeline}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <p className="text-sm font-medium mb-1">
            {pipelineStatus.initiative_title}
          </p>
          <Badge variant={getStatusColor()} className="text-xs">
            {getStatusText()}
          </Badge>
        </div>

        <Progress value={getProgress()} className="h-2" />

        <div className="space-y-1 text-xs text-muted-foreground">
          {pipelineStatus.total_grants && (
            <div className="flex justify-between">
              <span>Total grants:</span>
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
              <span>API calls remaining:</span>
              <span className="font-medium">
                {pipelineStatus.remaining_calls}
              </span>
            </div>
          )}
        </div>

        {pipelineStatus.message && (
          <p className="text-xs text-muted-foreground pt-2 border-t">
            {pipelineStatus.message}
          </p>
        )}

        {pipelineStatus.error && (
          <p className="text-xs text-red-500 pt-2 border-t">
            Error: {pipelineStatus.error}
          </p>
        )}
      </CardContent>
    </Card>
  )
}
