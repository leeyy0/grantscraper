import { SubmissionForms } from "@/components/submission-forms"

export default function Home() {
  return (
    <main className="bg-background min-h-screen px-4 py-12">
      <div className="mx-auto max-w-2xl">
        <h1 className="text-foreground mb-2 text-center text-3xl font-bold">
          Edit Organisation and Initiative Details
        </h1>
        <p className="text-muted-foreground mb-8 text-center">
          Edit your organisation&apos;s information to filter grants accurately.
        </p>
        <SubmissionForms />
      </div>
    </main>
  )
}
