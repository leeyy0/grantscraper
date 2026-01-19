"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams, usePathname } from "next/navigation"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ChevronLeft } from "lucide-react"
import * as initiativesDb from "@/lib/supabase/db/initiatives"
import type { Initiative } from "@/lib/supabase/db/types"

export default function RootLayout({
    children,
  }: Readonly<{
    children: React.ReactNode
  }>) {
    const router = useRouter()
    const params = useParams()
    const pathname = usePathname()
    const initiativeId = params.id as string
  
    const [initiative, setInitiative] = useState<Initiative | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
  
    // Determine back navigation path based on current route
    const isOnGrantPage = pathname?.includes('/grants/')
    const backPath = isOnGrantPage ? `/initiatives/${initiativeId}` : '/initiatives'
  
    useEffect(() => {
      async function loadInitiative() {
        try {
          setLoading(true)
  
          // Fetch initiative details
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
        } catch (err) {
          setError(err instanceof Error ? err.message : "Unknown error")
        } finally {
          setLoading(false)
        }
      }
  
      if (initiativeId) {
        loadInitiative()
      }
    }, [initiativeId])
  
    if (loading) {
      return (
        <main className="bg-background min-h-screen px-6 py-7 max-w-4xl mx-auto">
          <div className="mx-auto max-w-7xl">
            <Card>
              <CardHeader>
                <CardTitle>Loading...</CardTitle>
                <CardDescription>Fetching initiative...</CardDescription>
              </CardHeader>
            </Card>
          </div>
        </main>
      )
    }
  
    if (error) {
      return (
        <main className="bg-background min-h-screen px-6 py-7 max-w-4xl mx-auto">
          <div className="mx-auto max-w-7xl">
            <Card>
              <CardHeader>
                <CardTitle>Error</CardTitle>
                <CardDescription>{error}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={() => router.push("/initiatives")}>
                  Back to Initiatives
                </Button>
              </CardContent>
            </Card>
          </div>
        </main>
      )
    }
  
    return (
        
      <main className="bg-background min-h-screen px-6 py-7 max-w-4xl mx-auto">
        <div className="mx-auto max-w-7xl">
          <div className="mb-6 flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => router.push(backPath)}
              className="h-8 w-8"
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-3xl font-semibold">
                {initiative?.title || "Initiative"}
              </h1>
              <p className="text-muted-foreground">Grant Records</p>
            </div>
          </div>
          {children}
        </div>
      </main>
    )
}