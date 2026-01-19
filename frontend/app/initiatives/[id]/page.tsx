"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import * as initiativesDb from "@/lib/supabase/db/initiatives"
import * as resultsDb from "@/lib/supabase/db/results"
import type { Initiative, Result } from "@/lib/supabase/db/types"
import { getRatingColor } from "@/lib/utils"

interface ResultWithGrant extends Result {
  grants: {
    id: number
    name: string | null
    url: string
  }
}

export default function Page() {
  const router = useRouter()
  const params = useParams()
  const initiativeId = params.id as string

  const [initiative, setInitiative] = useState<Initiative | null>(null)
  const [results, setResults] = useState<ResultWithGrant[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)

        // Fetch initiative details (for the details card)
        const { data: initData, error: initError } =
          await initiativesDb.getById(Number(initiativeId))

        if (initError) {
          setError(initError.message)
          return
        }

        if (!initData) {
          setError("Initiative not found")
          return
        }

        setInitiative(initData)

        // Fetch results with grant details
        const { data: resultsData, error: resultsError } =
          await resultsDb.getByInitiativeWithDetails(Number(initiativeId))

        if (resultsError) {
          setError(resultsError.message)
          return
        }

        if (resultsData) {
          setResults(resultsData as ResultWithGrant[])
          console.log(resultsData)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error")
      } finally {
        setLoading(false)
      }
    }

    if (initiativeId) {
      loadData()
    }
  }, [initiativeId])

  const shortlistedResults = results.filter((r) => r.prelim_rating > 61)

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading...</CardTitle>
          <CardDescription>Fetching grant records...</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Error</CardTitle>
          <CardDescription>{error}</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={() => router.back()}>Go Back</Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <>
      <Card className="mb-6">
          <CardHeader>
            <CardTitle>Initiative Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div>
              <span className="font-semibold">Stage:</span> {initiative?.stage}
            </div>
            <div>
              <span className="font-semibold">Audience:</span>{" "}
              {initiative?.audience}
            </div>
            <div>
              <span className="font-semibold">Goals:</span> {initiative?.goals}
            </div>
            {initiative?.costs && (
              <div>
                <span className="font-semibold">Estimated Costs:</span> $
                {initiative.costs.toLocaleString()}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-2xl font-semibold">
            Grant Results{" "}
            <Badge variant="secondary" className="ml-2">
              {results.length} total
            </Badge>
            <Badge variant="default" className="ml-2">
              {shortlistedResults.length} shortlisted
            </Badge>
          </h2>
        </div>

        {results.length === 0 ? (
          <Card>
            <CardHeader>
              <CardTitle>No Grant Records</CardTitle>
              <CardDescription>
                No grants have been analysed for this initiative yet.
              </CardDescription>
            </CardHeader>
          </Card>
        ) : (
          <div className="flex flex-col gap-4">
            {results.map((result) => (
              <Link key={result.grant_id} href={`/initiatives/${initiativeId}/grants/${result.grant_id}`}>
                <Card className="border-border hover:border-primary/50 cursor-pointer border transition-all hover:shadow-md">
                  <CardContent className="p-4">
                    <div className="mb-4 flex gap-6">
                      <div className="flex flex-col">
                        <span className="text-muted-foreground text-sm">
                          Preliminary Rating
                        </span>
                        <span
                          className={`text-3xl font-bold ${getRatingColor(result.prelim_rating)}`}
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
                            className={`text-3xl font-bold ${getRatingColor(result.match_rating)}`}
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
                            className={`text-3xl font-bold ${getRatingColor(result.uncertainty_rating, true)}`}
                          >
                            {result.uncertainty_rating}%
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
                      <div className="flex flex-col">
                        <span className="text-muted-foreground">
                          Grant Name
                        </span>
                        <span className="font-medium">
                          {result.grants.name || "Unnamed Grant"}
                        </span>
                      </div>
                      {result.sponsor_name && (
                        <div className="flex flex-col">
                          <span className="text-muted-foreground">Sponsor</span>
                          <span className="font-medium">
                            {result.sponsor_name}
                          </span>
                        </div>
                      )}
                      {result.grant_amount && (
                        <div className="flex flex-col">
                          <span className="text-muted-foreground">Amount</span>
                          <span className="font-medium">
                            {result.grant_amount}
                          </span>
                        </div>
                      )}
                      {result.deadline && (
                        <div className="flex flex-col">
                          <span className="text-muted-foreground">
                            Deadline
                          </span>
                          <span className="font-medium">{result.deadline}</span>
                        </div>
                      )}
                    </div>

                    {result.grant_description && (
                      <div className="mt-3 text-sm">
                        <span className="text-muted-foreground">
                          Description:
                        </span>{" "}
                        <span className="line-clamp-2">
                          {result.grant_description}
                        </span>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
    </>
  )
}
