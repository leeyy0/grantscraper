"use client"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Plus } from "lucide-react"
import Link from "next/link"
import { useState, useEffect, useCallback } from "react"
import * as initiativesDb from "@/lib/supabase/db/initiatives"
import type { Initiative } from "@/lib/supabase/db/types"
import { InitiativeCard } from "@/components/initiative-card"

export default function Page() {
  const [initiatives, setInitiatives] = useState<Initiative[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchInitiatives = useCallback(async () => {
    try {
      setLoading(true)
      const { data, error } = await initiativesDb.getAll()

      if (error) {
        setError(error.message)
        console.error("Error fetching initiatives:", error)
      } else if (data) {
        setInitiatives(data)
      }
    } catch (err) {
      setError("Failed to fetch initiatives")
      console.error("Error:", err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchInitiatives()
  }, [fetchInitiatives])
  return (
    <main className="bg-background min-h-screen px-9">
      <div className="my-3 flex flex-col gap-2 py-3">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-semibold">Your Initiatives</h1>
          <Link href="/initiatives/add-or-update">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Initiative
            </Button>
          </Link>
        </div>
        <div className="grid w-full grid-cols-1 gap-4 py-3 md:grid-cols-2 lg:grid-cols-4">
          {loading ? (
            // Loading state
            Array.from({ length: 4 }).map((_, index) => (
              <Card key={`loading-${index}`}>
                <CardHeader className="w-full">
                  <CardTitle>Loading...</CardTitle>
                  <CardDescription>Fetching initiative data...</CardDescription>
                </CardHeader>
              </Card>
            ))
          ) : error ? (
            // Error state
            <Card>
              <CardHeader className="w-full">
                <CardTitle>Error</CardTitle>
                <CardDescription>{error}</CardDescription>
              </CardHeader>
            </Card>
          ) : initiatives.length === 0 ? (
            // Empty state
            <Card>
              <CardHeader className="w-full">
                <CardTitle>No Initiatives</CardTitle>
                <CardDescription>
                  No initiatives found. Create one to get started!
                </CardDescription>
              </CardHeader>
            </Card>
          ) : (
            // Display initiatives
            initiatives.map((initiative) => (
              <InitiativeCard
                key={initiative.id}
                initiative={initiative}
                onDelete={fetchInitiatives}
              />
            ))
          )}
        </div>
      </div>
    </main>
  )
}
