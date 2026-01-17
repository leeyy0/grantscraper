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
    <div className="mt-8 pt-6 border-t border-border">
      <h2 className="text-xl font-semibold mb-4">Grant Results</h2>
      <div className="space-y-4">
        {grants.map((grant) => (
          <Link key={grant.id} href={`/grant/${grant.id}`}>
            <Card className="border border-border hover:border-primary/50 hover:shadow-md transition-all cursor-pointer">
              <CardContent className="p-4">
                {/* Match and Uncertainty ratings - side by side, larger text */}
                <div className="flex gap-6 mb-4">
                  <div className="flex flex-col">
                    <span className="text-sm text-muted-foreground">Match Rating</span>
                    <span className={`text-3xl font-bold ${getRatingColor(grant.match_rating)}`}>
                      {grant.match_rating}%
                    </span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-sm text-muted-foreground">Uncertainty Rating</span>
                    <span className={`text-3xl font-bold ${getRatingColor(grant.uncertainty_rating, true)}`}>
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
