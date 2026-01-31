"use client"

import { Button } from "@/components/ui/button"
import Initiatives from "@/components/initiatives"
import { Settings } from "lucide-react"
import Link from "next/link"
import { useEffect } from "react"
import { usePipeline, getStoredPipeline } from "@/lib/pipeline-context"
import { getPipelineStatus } from "@/lib/backend"
import { Card } from "@/components/ui/card"

export default function Home() {
  const { resumePipeline, clearPipeline } = usePipeline()

  // Check for running pipeline on mount
  useEffect(() => {
    const checkRunningPipeline = async () => {
      const storedPipeline = getStoredPipeline()

      if (storedPipeline) {
        try {
          // Check if pipeline is still running in backend
          const status = await getPipelineStatus(storedPipeline.initiative_id)

          // If pipeline is still active, resume tracking
          if (status.status !== "completed" && status.status !== "error") {
            console.log(
              "Resuming pipeline tracking for initiative:",
              storedPipeline.initiative_id,
            )
            resumePipeline(
              storedPipeline.initiative_id,
              storedPipeline.initiative_title,
            )
          } else {
            // Pipeline already completed, clear storage
            clearPipeline()
          }
        } catch (error) {
          console.error("Failed to check pipeline status:", error)
          // If we can't check status, clear the stored pipeline
          clearPipeline()
        }
      }
    }

    checkRunningPipeline()
  }, [resumePipeline, clearPipeline])

  return (
    <main className="bg-background min-h-screen px-6 py-7">
      <Link href="/configure">
        <Card className="py-0">
          <Button
            variant="ghost"
            size="icon"
            className="h-17 w-full items-center! justify-start border px-4 py-7 text-left"
          >
            <Settings className="h-6! w-6!" />
            <span className="text-xl text-wrap">
              Configure your organisation&apos;s information here!
            </span>
          </Button>
        </Card>
      </Link>
      <Initiatives />
      {/* <div className="my-3 flex flex-col gap-2 py-3">
        <h1 className="text-3xl font-semibold">Recommended to apply</h1>
      </div> */}
      <div className="flex pb-3">
        <h1 className="text-3xl font-semibold">Grant Deadlines</h1>
      </div>
      <iframe
        src="https://calendar.google.com/calendar/embed?height=700&wkst=1&ctz=Asia%2FSingapore&showPrint=0&title=Grant%20Deadlines&src=N2M4YTZhNmRmYTY3YTdjNjQ5NzJlY2U4NTJlYWE3MzNkNjdkMjliZThiMWVlNDhhM2UwNDMyNGUwZmI4YjkxYUBncm91cC5jYWxlbmRhci5nb29nbGUuY29t&color=%239e69af"
        className="min-h-[700px] w-full border shadow"
      ></iframe>
    </main>
  )
}
