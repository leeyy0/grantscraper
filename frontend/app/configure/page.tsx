"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import {
  OrganisationForm,
  OrganisationFormInput,
  OrganisationFormErrors,
} from "@/components/organisation-form"
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
import * as organisationsDb from "@/lib/supabase/db/organisations"
import type { Organisation } from "@/lib/supabase/db/types"
import { toast } from "sonner"
import { ChevronLeft } from "lucide-react"

export default function Page() {
  const router = useRouter()
  const [organisation, setOrganisation] = useState<Organisation | null>(null)
  const [initialFormData, setInitialFormData] = useState<OrganisationFormInput>(
    {
      name: "",
      mission_and_focus: "",
      about_us: "",
      remarks: "",
    },
  )
  const [formData, setFormData] = useState<OrganisationFormInput>({
    name: "",
    mission_and_focus: "",
    about_us: "",
    remarks: "",
  })
  const [errors, setErrors] = useState<OrganisationFormErrors>({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [showUnsavedDialog, setShowUnsavedDialog] = useState(false)

  // Load organisation data on mount
  useEffect(() => {
    async function loadOrganisation() {
      try {
        setLoading(true)
        const { data, error } = await organisationsDb.getAll()

        if (error) {
          toast.error("Failed to load organisation data", {
            description: error.message,
          })
          return
        }

        // Get the first organisation or create a new one
        if (data && data.length > 0) {
          const org = data[0]
          setOrganisation(org)
          const orgData = {
            name: org.name || "",
            mission_and_focus: org.mission_and_focus || "",
            about_us: org.about_us || "",
            remarks: org.remarks || "",
          }
          setFormData(orgData)
          setInitialFormData(orgData)
        }
      } catch (error) {
        toast.error("An unexpected error occurred", {
          description: error instanceof Error ? error.message : "Unknown error",
        })
      } finally {
        setLoading(false)
      }
    }

    loadOrganisation()
  }, [])

  // Check if there are unsaved changes
  const hasUnsavedChanges = () => {
    return (
      formData.name !== initialFormData.name ||
      formData.mission_and_focus !== initialFormData.mission_and_focus ||
      formData.about_us !== initialFormData.about_us ||
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
    const newErrors: OrganisationFormErrors = {}

    if (!formData.name.trim()) {
      newErrors.name = "Organisation name is required"
    }

    if (!formData.mission_and_focus.trim()) {
      newErrors.mission_and_focus = "Mission and focus is required"
    }

    if (!formData.about_us.trim()) {
      newErrors.about_us = "About us is required"
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

    try {
      setSaving(true)

      if (organisation?.id) {
        // Update existing organisation
        const { data, error } = await organisationsDb.update(organisation.id, {
          name: formData.name,
          mission_and_focus: formData.mission_and_focus,
          about_us: formData.about_us,
          remarks: formData.remarks,
        })

        if (error) {
          toast.error("Failed to update organisation", {
            description: error.message,
          })
          return
        }

        if (data) {
          setOrganisation(data)
          const updatedData = {
            name: data.name || "",
            mission_and_focus: data.mission_and_focus || "",
            about_us: data.about_us || "",
            remarks: data.remarks || "",
          }
          setInitialFormData(updatedData)
          toast.success("Organisation updated successfully")
        }
      } else {
        // Create new organisation
        const { data, error } = await organisationsDb.create({
          name: formData.name,
          mission_and_focus: formData.mission_and_focus,
          about_us: formData.about_us,
          remarks: formData.remarks,
        })

        if (error) {
          toast.error("Failed to create organisation", {
            description: error.message,
          })
          return
        }

        if (data) {
          setOrganisation(data)
          const createdData = {
            name: data.name || "",
            mission_and_focus: data.mission_and_focus || "",
            about_us: data.about_us || "",
            remarks: data.remarks || "",
          }
          setInitialFormData(createdData)
          toast.success("Organisation created successfully")
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
            <CardTitle>Organisation Configuration</CardTitle>
            <CardDescription>Loading organisation data...</CardDescription>
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
                  <CardTitle>Organisation Configuration</CardTitle>
                  <CardDescription>
                    {organisation
                      ? "Update your organisation information"
                      : "Create your organisation profile"}
                  </CardDescription>
                </div>
              </div>
              <Button
                onClick={handleSave}
                disabled={saving || !hasUnsavedChanges()}
              >
                {saving ? "Saving..." : organisation ? "Update" : "Create"}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <OrganisationForm
              formData={formData}
              onChange={setFormData}
              errors={errors}
            />
            <div className="my-4 flex justify-end">
              <Button
                onClick={handleSave}
                disabled={saving || !hasUnsavedChanges()}
              >
                {saving ? "Saving..." : organisation ? "Update" : "Create"}
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
