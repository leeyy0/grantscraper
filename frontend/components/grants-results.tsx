"use client"

import Link from "next/link"
import { Card, CardContent } from "@/components/ui/card"
import { getRatingColor } from "@/lib/utils"

export interface GrantResult {
  id: string
  match_rating: number
  uncertainty_rating: number
  name: string
  amount: string
  sponsors: string
  deadline: string
}

interface GrantResultsProps {
  grants: GrantResult[]
}

export function GrantResults({ grants }: GrantResultsProps) {
  return (
    <div className="border-border mt-8 border-t pt-6">
      <h2 className="mb-4 text-xl font-semibold">Grant Results</h2>
      <div className="space-y-4">
        {grants.map((grant) => (
          <Link key={grant.id} href={`/grant/${grant.id}`}>
            <Card className="border-border hover:border-primary/50 cursor-pointer border transition-all hover:shadow-md">
              <CardContent className="p-4">
                {/* Match and Uncertainty ratings - side by side, larger text */}
                <div className="mb-4 flex gap-6">
                  <div className="flex flex-col">
                    <span className="text-muted-foreground text-sm">
                      Match Rating
                    </span>
                    <span
                      className={`text-3xl font-bold ${getRatingColor(grant.match_rating)}`}
                    >
                      {grant.match_rating}%
                    </span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-muted-foreground text-sm">
                      Uncertainty Rating
                    </span>
                    <span
                      className={`text-3xl font-bold ${getRatingColor(grant.uncertainty_rating, true)}`}
                    >
                      {grant.uncertainty_rating}%
                    </span>
                  </div>
                </div>
                {/* Grant details in two columns */}
                <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
                  <div className="flex flex-col">
                    <span className="text-muted-foreground">Name</span>
                    <span className="font-medium">{grant.name}</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-muted-foreground">Amount</span>
                    <span className="font-medium">{grant.amount}</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-muted-foreground">Sponsors</span>
                    <span className="font-medium">{grant.sponsors}</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-muted-foreground">Deadline</span>
                    <span className="font-medium">{grant.deadline}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
