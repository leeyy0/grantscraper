"use client"

import { useState, useEffect } from "react"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  OrganisationForm,
  type OrganisationFormErrors,
} from "@/components/organisation-form"
import {
  InitiativeForm,
  type InitiativeFormErrors,
} from "@/components/initiative-form"
import { GrantResults, type GrantResult } from "@/components/grants-results"
import { useFormContext } from "@/lib/form-context"
import { grantDetails, type GrantDetail } from "@/lib/grant-data"
import * as organisations from "@/lib/supabase/db/organisations"
import * as initiatives from "@/lib/supabase/db/initiatives"
import { toast } from "sonner"

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

function convertGrantDetailToResult(grant: GrantDetail): GrantResult {
  return {
    id: grant.id,
    match_rating: grant.match_rating,
    uncertainty_rating: grant.uncertainty_rating,
    name: grant.grant_name,
    amount: grant.grant_amount,
    sponsors: grant.grant_sponsors,
    deadline: formatDeadline(grant.deadline),
  }
}

export function SubmissionForms() {
  const {
    organisationForm,
    setOrganisationForm,
    initiativeForm,
    setInitiativeForm,
    showResults,
    setShowResults,
    grantResults,
    setGrantResults,
    accordionValue,
    setAccordionValue,
  } = useFormContext()

  const [errors, setErrors] = useState<{
    organisation: OrganisationFormErrors
    initiative: InitiativeFormErrors
  }>({
    organisation: {},
    initiative: {},
  })

  const [isLoadingOrg, setIsLoadingOrg] = useState(true)
  const [isLoadingInit, setIsLoadingInit] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [orgId, setOrgId] = useState<number | null>(null)
  const [initiativeId, setInitiativeId] = useState<number | null>(null)

  // Fetch and prefill organisation data on mount
  useEffect(() => {
    const fetchOrganisation = async () => {
      try {
        setIsLoadingOrg(true)
        const { data, error } = await organisations.getById(1)

        if (error) {
          console.error("Error fetching organisation:", error)
          toast.error("Failed to load organisation data")
          return
        }

        if (data) {
          setOrgId(data.id)
          setOrganisationForm({
            name: data.name,
            mission_and_focus: data.mission_and_focus,
            about_us: data.about_us,
            remarks: data.remarks || "",
          })
        }
      } catch (error) {
        console.error("Error fetching organisation:", error)
        toast.error("Failed to load organisation data")
      } finally {
        setIsLoadingOrg(false)
      }
    }

    fetchOrganisation()
  }, [setOrganisationForm])

  // Fetch and prefill initiative data on mount
  useEffect(() => {
    const fetchInitiative = async () => {
      try {
        setIsLoadingInit(true)
        // Get the first initiative for organisation id=1
        const { data, error } = await initiatives.getByOrganisation(1)

        if (error) {
          console.error("Error fetching initiative:", error)
          toast.error("Failed to load initiative data")
          return
        }

        // If there's an initiative, use the first one
        if (data && data.length > 0) {
          const initiative = data[0]
          setInitiativeId(initiative.id)
          setInitiativeForm({
            title: initiative.title,
            goals_objective: initiative.goals,
            audience_beneficiaries: initiative.audience,
            estimated_cost: initiative.costs ? initiative.costs.toString() : "",
            stage_of_initiative: initiative.stage,
            demographic: initiative.demographic || "",
            remarks: initiative.remarks || "",
          })
        }
      } catch (error) {
        console.error("Error fetching initiative:", error)
        toast.error("Failed to load initiative data")
      } finally {
        setIsLoadingInit(false)
      }
    }

    fetchInitiative()
  }, [setInitiativeForm])

  const validateForms = () => {
    const newErrors = {
      organisation: {} as OrganisationFormErrors,
      initiative: {} as InitiativeFormErrors,
    }

    // Validate Organisation Form
    if (!organisationForm.name.trim()) {
      newErrors.organisation.name = "Name is required"
    }
    if (!organisationForm.mission_and_focus.trim()) {
      newErrors.organisation.mission_and_focus = "Mission and Focus is required"
    }
    if (!organisationForm.about_us.trim()) {
      newErrors.organisation.about_us = "About Us is required"
    }

    // Validate Initiative Form
    if (!initiativeForm.title.trim()) {
      newErrors.initiative.title = "Title is required"
    }
    if (!initiativeForm.goals_objective.trim()) {
      newErrors.initiative.goals_objective = "Goals/ Objective is required"
    }
    if (!initiativeForm.audience_beneficiaries.trim()) {
      newErrors.initiative.audience_beneficiaries =
        "Audience/ Target Beneficiaries is required"
    }
    if (
      initiativeForm.estimated_cost.trim() &&
      (isNaN(Number.parseInt(initiativeForm.estimated_cost)) ||
        Number.parseInt(initiativeForm.estimated_cost) < 0)
    ) {
      newErrors.initiative.estimated_cost =
        "Estimated Cost must be a valid positive integer"
    }

    setErrors(newErrors)

    return (
      Object.keys(newErrors.organisation).length === 0 &&
      Object.keys(newErrors.initiative).length === 0
    )
  }

  const handleSubmit = async () => {
    if (!validateForms()) {
      return
    }

    try {
      setIsSubmitting(true)

      // Update organisation if orgId exists
      if (orgId) {
        const { error: orgError } = await organisations.update(orgId, {
          name: organisationForm.name,
          mission_and_focus: organisationForm.mission_and_focus,
          about_us: organisationForm.about_us,
          remarks: organisationForm.remarks.trim() || null,
        })

        if (orgError) {
          console.error("Error updating organisation:", orgError)
          toast.error("Failed to update organisation. Please try again.")
          return
        }
      }

      // Update or create initiative
      const initiativeData = {
        title: initiativeForm.title,
        goals: initiativeForm.goals_objective,
        audience: initiativeForm.audience_beneficiaries,
        costs: initiativeForm.estimated_cost.trim()
          ? Number.parseInt(initiativeForm.estimated_cost)
          : null,
        stage: initiativeForm.stage_of_initiative.trim() || "Planning",
        demographic: initiativeForm.demographic.trim() || null,
        remarks: initiativeForm.remarks.trim() || null,
        organisation_id: orgId || 1,
      }

      if (initiativeId) {
        // Update existing initiative
        const { error: initError } = await initiatives.update(
          initiativeId,
          initiativeData,
        )

        if (initError) {
          console.error("Error updating initiative:", initError)
          toast.error("Failed to update initiative. Please try again.")
          return
        }
      } else {
        // Create new initiative
        const { data: newInitiative, error: initError } =
          await initiatives.create(initiativeData)

        if (initError) {
          console.error("Error creating initiative:", initError)
          toast.error("Failed to create initiative. Please try again.")
          return
        }

        if (newInitiative) {
          setInitiativeId(newInitiative.id)
        }
      }

      toast.success("Information saved successfully!")

      // Convert GrantDetail[] to GrantResult[] format
      const results = grantDetails.map(convertGrantDetailToResult)
      setGrantResults(results)
      setShowResults(true)
      setAccordionValue([])
    } catch (error) {
      console.error("Error submitting form:", error)
      toast.error("An unexpected error occurred. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card className="border-border border">
      <CardContent className="px-6">
        <Accordion
          type="multiple"
          value={accordionValue}
          onValueChange={setAccordionValue}
          className="w-full"
        >
          <AccordionItem value="organisation">
            <AccordionTrigger className="text-lg font-semibold">
              Organisation Information
            </AccordionTrigger>
            <AccordionContent>
              {isLoadingOrg ? (
                <div className="text-muted-foreground py-8 text-center">
                  Loading organisation data...
                </div>
              ) : (
                <OrganisationForm
                  formData={organisationForm}
                  onChange={setOrganisationForm}
                  errors={errors.organisation}
                />
              )}
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="initiative">
            <AccordionTrigger className="text-lg font-semibold">
              Initiative Details
            </AccordionTrigger>
            <AccordionContent>
              {isLoadingInit ? (
                <div className="text-muted-foreground py-8 text-center">
                  Loading initiative data...
                </div>
              ) : (
                <InitiativeForm
                  formData={initiativeForm}
                  onChange={setInitiativeForm}
                  errors={errors.initiative}
                />
              )}
            </AccordionContent>
          </AccordionItem>
        </Accordion>

        <div className="border-border mt-6 border-t pt-6">
          <Button
            onClick={handleSubmit}
            className="w-full"
            size="lg"
            disabled={isSubmitting || isLoadingOrg || isLoadingInit}
          >
            {isSubmitting ? "Saving..." : "Save Information"}
          </Button>
        </div>

        {showResults && grantResults.length > 0 && (
          <GrantResults grants={grantResults} />
        )}
      </CardContent>
    </Card>
  )
}
