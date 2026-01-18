import { SubmissionForms } from "@/components/submission-forms"

export default function Home() {
  return (
    <main className="min-h-screen bg-background py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-foreground text-center mb-2">Submission Portal</h1>
        <p className="text-muted-foreground text-center mb-8">Complete both forms below to submit your information</p>
        <SubmissionForms />
      </div>
    </main>
  )
}
