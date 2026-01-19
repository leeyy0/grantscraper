import { notFound } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { getGrantById } from "@/lib/grant-data"
import { getRatingColor } from "@/lib/utils"

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

interface GrantDetailPageProps {
  params: Promise<{ id: string }>
}

export default async function GrantDetailPage({
  params,
}: GrantDetailPageProps) {
  const { id } = await params
  const grant = getGrantById(id)

  if (!grant) {
    notFound()
  }

  return (
    <main className="bg-background min-h-screen px-4 py-12">
      <div className="mx-auto max-w-4xl">
        <div className="mb-6">
          <Link href="/">
            <Button variant="outline" className="mb-4">
              ← Back to Results
            </Button>
          </Link>
        </div>

        <Card className="border-border border">
          <CardHeader>
            <div className="mb-4 flex items-start justify-between">
              <div>
                <CardTitle className="mb-2 text-3xl">
                  {grant.grant_name}
                </CardTitle>
                <CardDescription className="text-lg">
                  {grant.grant_description}
                </CardDescription>
              </div>
            </div>

            {/* Match and Uncertainty ratings */}
            <div className="mt-4 flex gap-8">
              <div className="flex flex-col">
                <span className="text-muted-foreground text-sm">
                  Match Rating
                </span>
                <span
                  className={`text-4xl font-bold ${getRatingColor(grant.match_rating)}`}
                >
                  {grant.match_rating}%
                </span>
              </div>
              <div className="flex flex-col">
                <span className="text-muted-foreground text-sm">
                  Uncertainty Rating
                </span>
                <span
                  className={`text-4xl font-bold ${getRatingColor(grant.uncertainty_rating, true)}`}
                >
                  {grant.uncertainty_rating}%
                </span>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Grant Information */}
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <div className="space-y-1">
                <span className="text-muted-foreground text-sm font-medium">
                  Grant Amount
                </span>
                <p className="text-lg font-semibold">{grant.grant_amount}</p>
              </div>
              <div className="space-y-1">
                <span className="text-muted-foreground text-sm font-medium">
                  Sponsors
                </span>
                <p className="text-lg font-semibold">{grant.grant_sponsors}</p>
              </div>
              <div className="space-y-1">
                <span className="text-muted-foreground text-sm font-medium">
                  Deadline
                </span>
                <p className="text-lg font-semibold">
                  {formatDeadline(grant.deadline)}
                </p>
              </div>
            </div>

            {/* Explanations */}
            <div className="border-border space-y-4 border-t pt-4">
              <div>
                <h3 className="mb-2 text-lg font-semibold">
                  Match Rating Explanation
                </h3>
                <p className="text-muted-foreground">
                  {grant.explanations.match_rating}
                </p>
              </div>
              <div>
                <h3 className="mb-2 text-lg font-semibold">
                  Uncertainty Rating Explanation
                </h3>
                <p className="text-muted-foreground">
                  {grant.explanations.uncertainty_rating}
                </p>
              </div>
            </div>

            {/* Eligibility Criteria */}
            <div className="border-border border-t pt-4">
              <h3 className="mb-4 text-lg font-semibold">
                Eligibility Criteria
              </h3>
              <ul className="space-y-2">
                {grant.criteria.map((criterion, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span className="text-muted-foreground">{criterion}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Sources */}
            {grant.sources.length > 0 && (
              <div className="border-border border-t pt-4">
                <h3 className="mb-4 text-lg font-semibold">Sources & Links</h3>
                <ul className="space-y-2">
                  {grant.sources.map((source, index) => (
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
    </main>
  )
}
