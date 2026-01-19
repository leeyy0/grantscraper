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
  Download,
  X,
  Globe,
  Link2,
  FileText,
  Database,
} from "lucide-react"
import { useRefresh, type RefreshStatus } from "@/lib/refresh-context"
import { toast } from "sonner"
import { getRefreshStreamUrl } from "@/lib/backend"

export function RefreshStatus() {
  const { refreshStatus, updateRefreshStatus, clearRefresh } = useRefresh()
  const eventSourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    // Only connect when we have a job and refresh is running
    const shouldConnect =
      refreshStatus.job_id &&
      refreshStatus.status !== "idle" &&
      refreshStatus.status !== "completed" &&
      refreshStatus.status !== "error"

    if (!shouldConnect) {
      // Clean up existing connection if status changed
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
      return
    }

    // Create SSE connection
    const streamUrl = getRefreshStreamUrl(refreshStatus.job_id!)
    const eventSource = new EventSource(streamUrl)

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        // Map the backend phase to our status
        const statusMap: Record<string, RefreshStatus["status"]> = {
          starting: "starting",
          navigating: "navigating",
          extracting_links: "extracting_links",
          scraping_details: "scraping_grants",
          scraping_grants: "scraping_grants", // Keep for backwards compatibility
          saving_to_db: "saving",
          saving: "saving", // Keep for backwards compatibility
          completed: "completed",
          error: "error",
        }

        updateRefreshStatus({
          status: statusMap[data.phase] || "starting",
          phase: data.phase,
          total_found: data.total_found,
          current_grant: data.current_grant,
          grants_saved: data.grants_saved,
          message: data.message,
          error: data.error,
        })

        // Show toast on completion
        if (data.phase === "completed") {
          toast.success("Grants refreshed!", {
            description: data.message || `${data.grants_saved} grants updated`,
          })
          eventSource.close()
        } else if (data.phase === "error") {
          toast.error("Refresh failed", {
            description: data.error || "An error occurred during scraping",
          })
          eventSource.close()
        }
      } catch (error) {
        console.error("Failed to parse SSE message:", error)
      }
    }

    eventSource.onerror = (error) => {
      console.error("SSE connection error:", error)
      updateRefreshStatus({
        status: "error",
        error: "Lost connection to server",
      })
      eventSource.close()
    }

    eventSourceRef.current = eventSource

    // Cleanup function
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
    }
  }, [refreshStatus.job_id, refreshStatus.status, updateRefreshStatus])

  if (refreshStatus.status === "idle" || !refreshStatus.job_id) {
    return null
  }

  const getStatusIcon = () => {
    switch (refreshStatus.status) {
      case "starting":
        return <Download className="h-5 w-5" />
      case "navigating":
        return <Globe className="h-5 w-5" />
      case "extracting_links":
        return <Link2 className="h-5 w-5" />
      case "scraping_grants":
        return <Loader2 className="h-5 w-5 animate-spin" />
      case "saving":
        return <Database className="h-5 w-5" />
      case "completed":
        return <CheckCircle2 className="h-5 w-5 text-green-500" />
      case "error":
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return <FileText className="h-5 w-5" />
    }
  }

  const getStatusText = () => {
    switch (refreshStatus.status) {
      case "starting":
        return "Starting browser..."
      case "navigating":
        return "Navigating to grants portal..."
      case "extracting_links":
        return "Finding open grants..."
      case "scraping_grants":
        return "Scraping grant details..."
      case "saving":
        return "Saving to database..."
      case "completed":
        return "Refresh complete!"
      case "error":
        return "Refresh failed"
      default:
        return "Processing..."
    }
  }

  const getStatusColor = () => {
    switch (refreshStatus.status) {
      case "completed":
        return "default"
      case "error":
        return "destructive"
      default:
        return "secondary"
    }
  }

  const getProgress = () => {
    if (refreshStatus.total_found && refreshStatus.current_grant) {
      return (refreshStatus.current_grant / refreshStatus.total_found) * 100
    }
    // Estimate progress based on status
    switch (refreshStatus.status) {
      case "starting":
        return 5
      case "navigating":
        return 15
      case "extracting_links":
        return 30
      case "scraping_grants":
        return 60
      case "saving":
        return 90
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
            <CardTitle className="text-base">Grant Refresh Status</CardTitle>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="-mt-1 -mr-1 h-6 w-6"
            onClick={clearRefresh}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <Badge variant={getStatusColor()} className="text-xs">
            {getStatusText()}
          </Badge>
        </div>

        <Progress value={getProgress()} className="h-2" />

        <div className="text-muted-foreground space-y-1 text-xs">
          {refreshStatus.status === "extracting_links" && (
            <div className="mb-2 rounded bg-blue-50 p-2 text-blue-700 dark:bg-blue-950 dark:text-blue-300">
              <p className="text-xs">Scanning OurSG portal for open grants</p>
            </div>
          )}
          {refreshStatus.status === "scraping_grants" && (
            <div className="mb-2 rounded bg-purple-50 p-2 text-purple-700 dark:bg-purple-950 dark:text-purple-300">
              <p className="text-xs">Extracting detailed grant information</p>
            </div>
          )}
          {refreshStatus.total_found !== undefined && (
            <div className="flex justify-between">
              <span>Total grants found:</span>
              <span className="font-medium">{refreshStatus.total_found}</span>
            </div>
          )}
          {refreshStatus.current_grant !== undefined && (
            <div className="flex justify-between">
              <span>Currently scraping:</span>
              <span className="font-medium">
                Grant {refreshStatus.current_grant}
              </span>
            </div>
          )}
          {refreshStatus.grants_saved !== undefined && (
            <div className="flex justify-between">
              <span>Grants saved:</span>
              <span className="font-medium">{refreshStatus.grants_saved}</span>
            </div>
          )}
        </div>

        {refreshStatus.message && (
          <p className="text-muted-foreground border-t pt-2 text-xs">
            {refreshStatus.message}
          </p>
        )}

        {refreshStatus.error && (
          <p className="border-t pt-2 text-xs text-red-500">
            Error: {refreshStatus.error}
          </p>
        )}
      </CardContent>
    </Card>
  )
}
