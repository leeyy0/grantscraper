import { notFound } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { getGrantById, type GrantDetail } from "@/lib/grant-data"
import { getRatingColor } from "@/lib/utils"

function formatDeadline(deadline: string | null): string {
  if (!deadline) return "No deadline specified"
  try {
    const date = new Date(deadline)
    return date.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })
  } catch {
    return deadline
  }
}

interface GrantDetailPageProps {
  params: Promise<{ id: string }>
}

export default async function GrantDetailPage({ params }: GrantDetailPageProps) {
  const { id } = await params
  const grant = getGrantById(id)

  if (!grant) {
    notFound()
  }

  return (
    <main className="min-h-screen bg-background py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <Link href="/">
            <Button variant="outline" className="mb-4">
              ← Back to Results
            </Button>
          </Link>
        </div>

        <Card className="border border-border">
          <CardHeader>
            <div className="flex justify-between items-start mb-4">
              <div>
                <CardTitle className="text-3xl mb-2">{grant.grant_name}</CardTitle>
                <CardDescription className="text-lg">{grant.grant_description}</CardDescription>
              </div>
            </div>

            {/* Match and Uncertainty ratings */}
            <div className="flex gap-8 mt-4">
              <div className="flex flex-col">
                <span className="text-sm text-muted-foreground">Match Rating</span>
                <span className={`text-4xl font-bold ${getRatingColor(grant.match_rating)}`}>
                  {grant.match_rating}%
                </span>
              </div>
              <div className="flex flex-col">
                <span className="text-sm text-muted-foreground">Uncertainty Rating</span>
                <span className={`text-4xl font-bold ${getRatingColor(grant.uncertainty_rating, true)}`}>
                  {grant.uncertainty_rating}%
                </span>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Grant Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-1">
                <span className="text-sm font-medium text-muted-foreground">Grant Amount</span>
                <p className="text-lg font-semibold">{grant.grant_amount}</p>
              </div>
              <div className="space-y-1">
                <span className="text-sm font-medium text-muted-foreground">Sponsors</span>
                <p className="text-lg font-semibold">{grant.grant_sponsors}</p>
              </div>
              <div className="space-y-1">
                <span className="text-sm font-medium text-muted-foreground">Deadline</span>
                <p className="text-lg font-semibold">{formatDeadline(grant.deadline)}</p>
              </div>
            </div>

            {/* Explanations */}
            <div className="space-y-4 pt-4 border-t border-border">
              <div>
                <h3 className="text-lg font-semibold mb-2">Match Rating Explanation</h3>
                <p className="text-muted-foreground">{grant.explanations.match_rating}</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">Uncertainty Rating Explanation</h3>
                <p className="text-muted-foreground">{grant.explanations.uncertainty_rating}</p>
              </div>
            </div>

            {/* Eligibility Criteria */}
            <div className="pt-4 border-t border-border">
              <h3 className="text-lg font-semibold mb-4">Eligibility Criteria</h3>
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
              <div className="pt-4 border-t border-border">
                <h3 className="text-lg font-semibold mb-4">Sources & Links</h3>
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
