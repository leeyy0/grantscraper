import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function GrantNotFound() {
  return (
    <main className="min-h-screen bg-background py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <Card className="border border-border">
          <CardHeader>
            <CardTitle className="text-2xl">Grant Not Found</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              The grant you're looking for doesn't exist or may have been removed.
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
