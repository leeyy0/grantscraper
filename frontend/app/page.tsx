"use client"

import { Button } from "@/components/ui/button"
import Initiatives from "@/components/initiatives"
import { Settings } from "lucide-react"
import Link from "next/link"
import { useEffect } from "react"
import { usePipeline, getStoredPipeline } from "@/lib/pipeline-context"
import { getPipelineStatus } from "@/lib/backend"

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
        <Button
          variant="ghost"
          size="icon"
          className="h-17 w-full items-center! justify-start border-2 px-4 py-7 text-left"
        >
          <Settings className="h-6! w-6!" />
          <span className="text-xl">
            Configure your organisation&apos;s information here!
          </span>
        </Button>
      </Link>
      <Initiatives />
      <div className="my-3 flex flex-col gap-2 py-3">
        <h1 className="text-3xl font-semibold">Recommended to apply</h1>
      </div>
    </main>
  )
}
