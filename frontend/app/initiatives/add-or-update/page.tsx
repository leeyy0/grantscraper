"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import {
  InitiativeForm,
  InitiativeFormInput,
  InitiativeFormErrors,
} from "@/components/initiative-form"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import * as initiativesDb from "@/lib/supabase/db/initiatives"
import * as organisationsDb from "@/lib/supabase/db/organisations"
import type { Initiative } from "@/lib/supabase/db/types"
import { toast } from "sonner"
import { ChevronLeft } from "lucide-react"

export default function Page() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const initiativeId = searchParams.get("id")

  const [initiative, setInitiative] = useState<Initiative | null>(null)
  const [organisationId, setOrganisationId] = useState<number | null>(null)
  const [initialFormData, setInitialFormData] = useState<InitiativeFormInput>({
    title: "",
    stage: "",
    audience: "",
    goals: "",
    costs: "",
    demographic: "",
    remarks: "",
    organisation_id: 0,
  })
  const [formData, setFormData] = useState<InitiativeFormInput>({
    title: "",
    stage: "",
    audience: "",
    goals: "",
    costs: "",
    demographic: "",
    remarks: "",
    organisation_id: 0,
  })
  const [errors, setErrors] = useState<InitiativeFormErrors>({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [showUnsavedDialog, setShowUnsavedDialog] = useState(false)

  // Load initiative data on mount
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)

        // First, get the organisation ID
        const { data: orgData, error: orgError } =
          await organisationsDb.getAll()

        if (orgError) {
          toast.error("Failed to load organisation data", {
            description: orgError.message,
          })
          return
        }

        if (!orgData || orgData.length === 0) {
          toast.error("No organisation found", {
            description: "Please configure your organisation first",
          })
          router.push("/configure")
          return
        }

        const orgId = orgData[0].id
        setOrganisationId(orgId)

        // If we have an initiative ID, load it
        if (initiativeId) {
          const { data, error } = await initiativesDb.getById(
            Number(initiativeId),
          )

          if (error) {
            toast.error("Failed to load initiative data", {
              description: error.message,
            })
            return
          }

          if (data) {
            setInitiative(data)
            const initData = {
              title: data.title || "",
              stage: data.stage || "",
              audience: data.audience || "",
              goals: data.goals || "",
              costs: data.costs?.toString() || "",
              demographic: data.demographic || "",
              remarks: data.remarks || "",
              organisation_id: data.organisation_id,
            }
            setFormData(initData)
            setInitialFormData(initData)
          }
        } else {
          // New initiative - set organisation ID
          setFormData((prev) => ({ ...prev, organisation_id: orgId }))
          setInitialFormData((prev) => ({ ...prev, organisation_id: orgId }))
        }
      } catch (error) {
        toast.error("An unexpected error occurred", {
          description: error instanceof Error ? error.message : "Unknown error",
        })
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [initiativeId, router])

  // Check if there are unsaved changes
  const hasUnsavedChanges = () => {
    return (
      formData.title !== initialFormData.title ||
      formData.stage !== initialFormData.stage ||
      formData.audience !== initialFormData.audience ||
      formData.goals !== initialFormData.goals ||
      formData.costs !== initialFormData.costs ||
      formData.demographic !== initialFormData.demographic ||
      formData.remarks !== initialFormData.remarks
    )
  }

  // Handle back navigation
  const handleBack = () => {
    if (hasUnsavedChanges()) {
      setShowUnsavedDialog(true)
    } else {
      router.back()
    }
  }

  // Confirm navigation without saving
  const handleConfirmLeave = () => {
    setShowUnsavedDialog(false)
    router.back()
  }

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: InitiativeFormErrors = {}

    if (!formData.title.trim()) {
      newErrors.title = "Title is required"
    }

    if (!formData.stage.trim()) {
      newErrors.stage = "Stage is required"
    }

    if (!formData.audience.trim()) {
      newErrors.audience = "Audience is required"
    }

    if (!formData.goals.trim()) {
      newErrors.goals = "Goals are required"
    }

    if (formData.costs && isNaN(Number(formData.costs))) {
      newErrors.costs = "Costs must be a valid number"
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  // Handle save
  const handleSave = async () => {
    if (!validateForm()) {
      toast.error("Please fix the errors in the form")
      return
    }

    if (!organisationId && !formData.organisation_id) {
      toast.error("Organisation ID is missing")
      return
    }

    try {
      setSaving(true)

      const initiativeData = {
        title: formData.title,
        stage: formData.stage,
        audience: formData.audience,
        goals: formData.goals,
        costs: formData.costs ? Number(formData.costs) : null,
        demographic: formData.demographic || null,
        remarks: formData.remarks || null,
        organisation_id: formData.organisation_id || organisationId!,
      }

      if (initiative?.id) {
        // Update existing initiative
        const { data, error } = await initiativesDb.update(
          initiative.id,
          initiativeData,
        )

        if (error) {
          toast.error("Failed to update initiative", {
            description: error.message,
          })
          return
        }

        if (data) {
          setInitiative(data)
          const updatedData = {
            title: data.title || "",
            stage: data.stage || "",
            audience: data.audience || "",
            goals: data.goals || "",
            costs: data.costs?.toString() || "",
            demographic: data.demographic || "",
            remarks: data.remarks || "",
            organisation_id: data.organisation_id,
          }
          setInitialFormData(updatedData)
          toast.success("Initiative updated successfully")
          router.back()
        }
      } else {
        // Create new initiative
        const { data, error } = await initiativesDb.create(initiativeData)

        if (error) {
          toast.error("Failed to create initiative", {
            description: error.message,
          })
          return
        }

        if (data) {
          toast.success("Initiative created successfully")
          router.back()
        }
      }
    } catch (error) {
      toast.error("An unexpected error occurred", {
        description: error instanceof Error ? error.message : "Unknown error",
      })
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-9xl mx-4 p-6">
        <Card>
          <CardHeader>
            <CardTitle>
              {initiativeId ? "Edit Initiative" : "Add Initiative"}
            </CardTitle>
            <CardDescription>Loading initiative data...</CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <>
      <div className="max-w-9xl mx-4 p-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleBack}
                  className="h-8 w-8"
                >
                  <ChevronLeft className="h-5 w-5" />
                </Button>
                <div>
                  <CardTitle>
                    {initiative ? "Edit Initiative" : "Add Initiative"}
                  </CardTitle>
                  <CardDescription>
                    {initiative
                      ? "Update your initiative information"
                      : "Create a new initiative"}
                  </CardDescription>
                </div>
              </div>
              <Button
                onClick={handleSave}
                disabled={saving || !hasUnsavedChanges()}
              >
                {saving ? "Saving..." : initiative ? "Update" : "Create"}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <InitiativeForm
              formData={formData}
              onChange={setFormData}
              errors={errors}
            />
            <div className="my-4 flex justify-end">
              <Button
                onClick={handleSave}
                disabled={saving || !hasUnsavedChanges()}
              >
                {saving ? "Saving..." : initiative ? "Update" : "Create"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <AlertDialog open={showUnsavedDialog} onOpenChange={setShowUnsavedDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Unsaved Changes</AlertDialogTitle>
            <AlertDialogDescription>
              You have unsaved changes. Are you sure you want to leave? Your
              changes will be lost.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Stay on page</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmLeave}>
              Leave without saving
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
