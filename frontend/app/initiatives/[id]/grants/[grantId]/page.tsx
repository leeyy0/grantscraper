"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Loader2 } from "lucide-react"
import { getRatingColor } from "@/lib/utils"
import supabase from "@/lib/supabase/client"
import type { Result, Grant } from "@/lib/supabase/db/types"
import { toast } from "sonner"

interface ResultWithGrant extends Result {
  grants: Grant
}

interface Explanations {
  match_rating?: string
  uncertainty_rating?: string
}

function formatDeadline(deadline: string | null): string {
  if (!deadline) return "No deadline specified"
  try {
    const date = new Date(deadline)
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  } catch {
    return deadline
  }
}

export default function GrantDetailPage() {
  const router = useRouter()
  const params = useParams()
  const initiativeId = params.id as string
  const grantId = params.grantId as string

  const [result, setResult] = useState<ResultWithGrant | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchGrantDetails() {
      try {
        setLoading(true)
        
        const { data, error: fetchError } = await supabase
          .from("results")
          .select("*, grants(*)")
          .eq("initiative_id", Number(initiativeId))
          .eq("grant_id", Number(grantId))
          .single()

        if (fetchError) {
          setError(fetchError.message)
          toast.error("Failed to load grant details", {
            description: fetchError.message,
          })
          return
        }

        if (!data) {
          setError("Grant not found")
          toast.error("Grant not found")
          return
        }

        setResult(data as ResultWithGrant)
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : "Unknown error"
        setError(errorMsg)
        toast.error("An unexpected error occurred", {
          description: errorMsg,
        })
      } finally {
        setLoading(false)
      }
    }

    if (initiativeId && grantId) {
      fetchGrantDetails()
    }
  }, [initiativeId, grantId])

  if (loading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
        <div className="flex flex-col items-center gap-2">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            Loading grant details...
          </p>
        </div>
      </div>
    )
  }

  if (error || !result) {
    return (
      <main className="bg-background min-h-screen px-4 py-12">
        <div className="mx-auto max-w-4xl">
          <Card>
            <CardHeader>
              <CardTitle>Error</CardTitle>
              <CardDescription>{error || "Grant not found"}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => router.push(`/initiatives/${initiativeId}`)}>
                Back to Initiative
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    )
  }

  return (<div className="mx-auto">
        

        <Card className="border-border border">
          <CardHeader>
            <div className="mb-4 flex items-start justify-between">
              <div>
                <CardTitle className="mb-2 text-3xl">
                  {result.grants.name || "Untitled Grant"}
                </CardTitle>
                {result.grant_description && (
                  <CardDescription className="text-lg">
                    {result.grant_description}
                  </CardDescription>
                )}
              </div>
            </div>

            {/* Ratings */}
            <div className="mt-4 flex flex-wrap gap-8">
              <div className="flex flex-col">
                <span className="text-muted-foreground text-sm">
                  Preliminary Rating
                </span>
                <span
                  className={`text-4xl font-bold ${getRatingColor(result.prelim_rating)}`}
                >
                  {result.prelim_rating}%
                </span>
              </div>
              {result.match_rating !== null && (
                <div className="flex flex-col">
                  <span className="text-muted-foreground text-sm">
                    Match Rating
                  </span>
                  <span
                    className={`text-4xl font-bold ${getRatingColor(result.match_rating)}`}
                  >
                    {result.match_rating}%
                  </span>
                </div>
              )}
              {result.uncertainty_rating !== null && (
                <div className="flex flex-col">
                  <span className="text-muted-foreground text-sm">
                    Uncertainty Rating
                  </span>
                  <span
                    className={`text-4xl font-bold ${getRatingColor(result.uncertainty_rating, true)}`}
                  >
                    {result.uncertainty_rating}%
                  </span>
                </div>
              )}
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Grant Information */}
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              {result.grant_amount && (
                <div className="space-y-1">
                  <span className="text-muted-foreground text-sm font-medium">
                    Grant Amount
                  </span>
                  <p className="text-lg font-semibold">{result.grant_amount}</p>
                </div>
              )}
              {result.sponsor_name && (
                <div className="space-y-1">
                  <span className="text-muted-foreground text-sm font-medium">
                    Sponsor
                  </span>
                  <p className="text-lg font-semibold">{result.sponsor_name}</p>
                </div>
              )}
              {result.deadline && (
                <div className="space-y-1">
                  <span className="text-muted-foreground text-sm font-medium">
                    Deadline
                  </span>
                  <p className="text-lg font-semibold">
                    {formatDeadline(result.deadline)}
                  </p>
                </div>
              )}
              {result.grants.url && (
                <div className="space-y-1">
                  <span className="text-muted-foreground text-sm font-medium">
                    Source URL
                  </span>
                  <a
                    href={result.grants.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline block text-lg"
                  >
                    {result.grants.url}
                  </a>
                </div>
              )}
            </div>

            {/* Sponsor Description */}
            {result.sponsor_description && (
              <div className="border-border border-t pt-4">
                <h3 className="mb-2 text-lg font-semibold">
                  About the Sponsor
                </h3>
                <p className="text-muted-foreground">
                  {result.sponsor_description}
                </p>
              </div>
            )}

            {/* Explanations */}
            {result.explanations &&
              typeof result.explanations === "object" &&
              result.explanations !== null && (
                <div className="border-border space-y-4 border-t pt-4">
                  {(result.explanations as Explanations).match_rating && (
                    <div>
                      <h3 className="mb-2 text-lg font-semibold">
                        Match Rating Explanation
                      </h3>
                      <p className="text-muted-foreground">
                        {(result.explanations as Explanations).match_rating}
                      </p>
                    </div>
                  )}
                  {(result.explanations as Explanations).uncertainty_rating && (
                    <div>
                      <h3 className="mb-2 text-lg font-semibold">
                        Uncertainty Rating Explanation
                      </h3>
                      <p className="text-muted-foreground">
                        {(result.explanations as Explanations).uncertainty_rating}
                      </p>
                    </div>
                  )}
                </div>
              )}

            {/* Eligibility Criteria */}
            {result.criteria && result.criteria.length > 0 && (
              <div className="border-border border-t pt-4">
                <h3 className="mb-4 text-lg font-semibold">
                  Eligibility Criteria
                </h3>
                <ul className="space-y-2">
                  {result.criteria.map((criterion, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span className="text-muted-foreground">{criterion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Sources */}
            {result.sources && result.sources.length > 0 && (
              <div className="border-border border-t pt-4">
                <h3 className="mb-4 text-lg font-semibold">Sources & Links</h3>
                <ul className="space-y-2">
                  {result.sources.map((source, index) => (
                    <li key={index}>
                      <a
                        href={source}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline"
                      >
                        {source}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
  )
}
