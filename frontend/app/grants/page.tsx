"use client"

import { useState, useEffect } from "react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ExternalLink, Loader2 } from "lucide-react"
import type { Grant } from "@/lib/supabase/db/types"
import * as grantsDb from "@/lib/supabase/db/grants"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { triggerRefreshGrants } from "@/lib/backend"
import { useRefresh, getStoredRefresh } from "@/lib/refresh-context"
import { RefreshStatus } from "@/components/refresh-status"

interface GrantCardProps {
  grant: Grant
}

function GrantCard({ grant }: GrantCardProps) {

  return (
    <Card className="flex h-full flex-col">
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0 flex-1">
            <CardTitle className="text-lg text-wrap">
              {grant.name || "Untitled Grant"}
            </CardTitle>
            <CardDescription className="mt-1">
              {grant.url && (
                <a
                  href={grant.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-blue-600 hover:underline dark:text-blue-400"
                >
                  View Source
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-3">
        <div className="space-y-2 text-sm">
          {grant.card_body_text && (
            <p className="line-clamp-4 text-muted-foreground">
              {grant.card_body_text}
            </p>
          )}
          
          
          
          {grant.links && grant.links.length > 0 && (
            <div className="mt-2">
              <span className="text-xs font-semibold">Related Links:</span>
              <div className="mt-1 flex flex-wrap gap-1">
                {grant.links.slice(0, 3).map((link, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    Link {index + 1}
                  </Badge>
                ))}
                {grant.links.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{grant.links.length - 3} more
                  </Badge>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="mt-auto pt-3">
          <a
            href={grant.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex h-9 w-full items-center justify-center gap-2 rounded-md border border-input bg-background px-3 font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
          >
            View Full Details
            <ExternalLink className="h-5 w-5" />
          </a>
        </div>
      </CardContent>
    </Card>
  )
}

export default function GrantsPage() {
  const [grants, setGrants] = useState<Grant[]>([])
  const [loading, setLoading] = useState(true)
  const { refreshStatus, startRefresh } = useRefresh()

  const fetchGrants = async () => {
    try {
      const { data, error } = await grantsDb.getAll()

      if (error) {
        toast.error("Failed to load grants", {
          description: error.message,
        })
        return
      }

      setGrants(data || [])
    } catch (err) {
      toast.error("An unexpected error occurred", {
        description: err instanceof Error ? err.message : "Unknown error",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchGrants()
  }, [])

  // Check for existing refresh process on mount
  useEffect(() => {
    const storedRefresh = getStoredRefresh()
    if (storedRefresh && storedRefresh.job_id) {
      console.log(
        `Found existing refresh job: ${storedRefresh.job_id}, resuming...`
      )
      // Restore the refresh status - this will trigger SSE reconnection
      startRefresh(storedRefresh.job_id)
    }
  }, [startRefresh])

  // Reload grants when refresh completes
  useEffect(() => {
    if (refreshStatus.status === "completed") {
      fetchGrants()
    }
  }, [refreshStatus.status])

  const handleRefreshGrants = async () => {
    try {
      toast.info("Initiating scraper...")
      
      const response = await triggerRefreshGrants()
      startRefresh(response.job_id)
      
      toast.success("Scraper started!", {
        description: "Check the status card for progress",
      })
    } catch (error) {
      toast.error("Failed to start scraper", {
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
      })
    }
  }
  

  if (loading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
        <div className="flex flex-col items-center gap-2">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Loading grants...</p>
        </div>
      </div>
    )
  }

  const isRefreshing = 
    refreshStatus.status !== "idle" && 
    refreshStatus.status !== "completed" && 
    refreshStatus.status !== "error"

  return (
    <div className="container mx-auto px-4 py-8">
      <RefreshStatus />
      <div className="mb-6">
        <div className="flex flex-row justify-between">
          <div>
            <h1 className="text-3xl font-bold">All Grants</h1>
            <p className="mt-2 text-muted-foreground">
              Browse through all available grants in our database
            </p>
            <div className="mt-2">
              <Badge variant="secondary">
                {grants.length} {grants.length === 1 ? "Grant" : "Grants"} Found
              </Badge>
            </div>

          </div>
          <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="default"
                    className=""
                    onClick={handleRefreshGrants}
                    disabled={isRefreshing}
                  >
                    Refresh Grants
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="bottom">
                  <p>
                    Triggers the scraper to check for updates at the OurSG Grants Portal
                  </p>
                </TooltipContent>
              </Tooltip>
        </div>
      </div>

      {grants.length === 0 ? (
        <Card className="p-12 text-center">
          <CardContent>
            <p className="text-muted-foreground">
              No grants found. Check back later for updates.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {grants.map((grant) => (
            <GrantCard key={grant.id} grant={grant} />
          ))}
        </div>
      )}
    </div>
  )
}
