import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function GrantNotFound() {
  return (
    <main className="bg-background min-h-screen px-4 py-12">
      <div className="mx-auto max-w-2xl">
        <Card className="border-border border">
          <CardHeader>
            <CardTitle className="text-2xl">Grant Not Found</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              The grant you&apos;re looking for doesn&apos;t exist or may have
              been removed.
            </p>
            <Link href="/">
              <Button>Back to Results</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}
