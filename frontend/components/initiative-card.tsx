"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { Pencil, Trash2, Eye, Sparkles } from "lucide-react"
import type { Initiative } from "@/lib/supabase/db/types"
import * as initiativesDb from "@/lib/supabase/db/initiatives"
import * as resultsDb from "@/lib/supabase/db/results"
import { triggerFilterGrants } from "@/lib/backend"
import { usePipeline } from "@/lib/pipeline-context"
import { toast } from "sonner"

interface InitiativeCardProps {
  initiative: Initiative
  onDelete?: () => void
}

export function InitiativeCard({ initiative, onDelete }: InitiativeCardProps) {
  const router = useRouter()
  const { startPipeline } = usePipeline()
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [shortlistedCount, setShortlistedCount] = useState<number | null>(null)
  const [loadingCount, setLoadingCount] = useState(true)

  // Fetch shortlisted grants count
  useEffect(() => {
    async function fetchShortlistedCount() {
      try {
        const { count, error } = await resultsDb.getShortlistedCount(
          initiative.id,
        )

        if (error) {
          console.error("Error fetching shortlisted count:", error)
        } else {
          setShortlistedCount(count)
        }
      } catch (err) {
        console.error("Error:", err)
      } finally {
        setLoadingCount(false)
      }
    }

    fetchShortlistedCount()
  }, [initiative.id])

  const handleEdit = () => {
    router.push(`/initiatives/add-or-update?id=${initiative.id}`)
  }

  const handleDelete = async () => {
    try {
      setDeleting(true)
      const { error } = await initiativesDb.deleteInitiative(initiative.id)

      if (error) {
        toast.error("Failed to delete initiative", {
          description: error.message,
        })
        return
      }

      toast.success("Initiative deleted successfully")
      setShowDeleteDialog(false)

      // Call onDelete callback to refresh the list
      if (onDelete) {
        onDelete()
      }
    } catch (err) {
      toast.error("An unexpected error occurred", {
        description: err instanceof Error ? err.message : "Unknown error",
      })
    } finally {
      setDeleting(false)
    }
  }

  const handleViewGrants = () => {
    router.push(`/initiatives/${initiative.id}`)
  }

  const handleAnalyseGrants = async () => {
    try {
      setAnalyzing(true)

      toast.info("Starting pipeline...", {
        description: "Analyzing grants for your initiative",
      })

      await triggerFilterGrants(initiative.id, 61)

      // Start pipeline tracking in context
      startPipeline(initiative.id, initiative.title)

      toast.success("Pipeline started successfully", {
        description: `Processing grants for ${initiative.title}. Check the sidebar for live updates.`,
        duration: 5000,
      })
    } catch (error) {
      toast.error("Failed to start pipeline", {
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
      })
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <>
      <Card className="flex h-full flex-col">
        <CardHeader className="w-full">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0 flex-1">
              <CardTitle className="truncate text-lg text-wrap">
                {initiative.title}
              </CardTitle>
              <CardDescription>
                <span className="font-semibold">Stage:</span> {initiative.stage}
              </CardDescription>
            </div>
            <div className="flex shrink-0 gap-1">
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={handleEdit}
              >
                <Pencil className="h-5 w-5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="text-destructive hover:text-destructive h-8 w-8"
                onClick={() => setShowDeleteDialog(true)}
              >
                <Trash2 className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="flex flex-1 flex-col gap-3">
          <div className="space-y-2 text-sm">
            <p>
              <span className="font-semibold">Audience:</span>{" "}
              {initiative.audience}
            </p>
            <p className="line-clamp-3">
              <span className="font-semibold">Goals:</span> {initiative.goals}
            </p>
            {initiative.costs && (
              <p>
                <span className="font-semibold">Costs:</span> $
                {initiative.costs.toLocaleString()}
              </p>
            )}
          </div>

          <div className="border-t pt-2">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm font-semibold">Shortlisted Grants:</span>
              {loadingCount ? (
                <Badge variant="secondary">Loading...</Badge>
              ) : (
                <Badge
                  variant={
                    shortlistedCount && shortlistedCount > 0
                      ? "default"
                      : "secondary"
                  }
                >
                  {shortlistedCount ?? 0}
                </Badge>
              )}
            </div>

            <div className="flex flex-col gap-2">
              <Button
                variant="outline"
                size="sm"
                className="w-full justify-start"
                onClick={handleViewGrants}
              >
                <Eye className="mr-2 h-4 w-4" />
                View Grant Records
              </Button>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                    onClick={handleAnalyseGrants}
                    disabled={analyzing}
                  >
                    <Sparkles className="mr-2 h-4 w-4" />
                    {analyzing ? "Analysing..." : "Analyse Grants"}
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="bottom">
                  <p className="max-w-xs">
                    Triggers the pipeline to analyse grants based on your
                    organisation and initiative details
                  </p>
                </TooltipContent>
              </Tooltip>
            </div>
          </div>
        </CardContent>
      </Card>

      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Initiative</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete &quot;{initiative.title}&quot;?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleting ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
