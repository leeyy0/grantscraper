"use client"

import { useState } from "react"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { OrganizationForm, type OrganizationFormErrors } from "@/components/organization-form"
import { InitiativeForm, type InitiativeFormErrors } from "@/components/initiative-form"
import { GrantResults, type GrantResult } from "@/components/grants-results"
import { useFormContext } from "@/lib/form-context"
import { grantDetails, type GrantDetail } from "@/lib/grant-data"

function formatDeadline(deadline: string | null): string {
  if (!deadline) return "No deadline specified"
  try {
    const date = new Date(deadline)
    return date.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })
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
    organizationForm,
    setOrganizationForm,
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
    organization: OrganizationFormErrors
    initiative: InitiativeFormErrors
  }>({
    organization: {},
    initiative: {},
  })

  const validateForms = () => {
    const newErrors = {
      organization: {} as OrganizationFormErrors,
      initiative: {} as InitiativeFormErrors,
    }

    // Validate Organization Form
    if (!organizationForm.name.trim()) {
      newErrors.organization.name = "Name is required"
    }
    if (!organizationForm.mission_and_focus.trim()) {
      newErrors.organization.mission_and_focus = "Mission and Focus is required"
    }
    if (!organizationForm.about_us.trim()) {
      newErrors.organization.about_us = "About Us is required"
    }

    // Validate Initiative Form
    if (!initiativeForm.title.trim()) {
      newErrors.initiative.title = "Title is required"
    }
    if (!initiativeForm.goals_objective.trim()) {
      newErrors.initiative.goals_objective = "Goals/Objective is required"
    }
    if (!initiativeForm.audience_beneficiaries.trim()) {
      newErrors.initiative.audience_beneficiaries = "Audience/Target Beneficiaries is required"
    }
    if (
      initiativeForm.estimated_cost.trim() &&
      (isNaN(Number.parseInt(initiativeForm.estimated_cost)) || Number.parseInt(initiativeForm.estimated_cost) < 0)
    ) {
      newErrors.initiative.estimated_cost = "Estimated Cost must be a valid positive integer"
    }

    setErrors(newErrors)

    return Object.keys(newErrors.organization).length === 0 && Object.keys(newErrors.initiative).length === 0
  }

  const handleSubmit = () => {
    if (validateForms()) {
      const submissionData = {
        organization: {
          name: organizationForm.name,
          mission_and_focus: organizationForm.mission_and_focus,
          about_us: organizationForm.about_us,
          remarks: organizationForm.remarks.trim() || null,
        },
        initiative: {
          title: initiativeForm.title,
          goals_objective: initiativeForm.goals_objective,
          audience_beneficiaries: initiativeForm.audience_beneficiaries,
          estimated_cost: initiativeForm.estimated_cost.trim() ? Number.parseInt(initiativeForm.estimated_cost) : null,
          stage_of_initiative: initiativeForm.stage_of_initiative.trim() || null,
          demographic: initiativeForm.demographic.trim() || null,
          remarks: initiativeForm.remarks.trim() || null,
        },
      }
      console.log("Form submitted:", submissionData)
      // Convert GrantDetail[] to GrantResult[] format
      const results = grantDetails.map(convertGrantDetailToResult)
      setGrantResults(results)
      setShowResults(true)
      setAccordionValue([])
    }
  }

  return (
    <Card className="border border-border">
      <CardContent className="p-6">
        <Accordion type="multiple" value={accordionValue} onValueChange={setAccordionValue} className="w-full">
          <AccordionItem value="organization">
            <AccordionTrigger className="text-lg font-semibold">Organization Information</AccordionTrigger>
            <AccordionContent>
              <OrganizationForm
                formData={organizationForm}
                onChange={setOrganizationForm}
                errors={errors.organization}
              />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="initiative">
            <AccordionTrigger className="text-lg font-semibold">Initiative Details</AccordionTrigger>
            <AccordionContent>
              <InitiativeForm formData={initiativeForm} onChange={setInitiativeForm} errors={errors.initiative} />
            </AccordionContent>
          </AccordionItem>
        </Accordion>

        <div className="mt-6 pt-6 border-t border-border">
          <Button onClick={handleSubmit} className="w-full" size="lg">
            Submit Information
          </Button>
        </div>

        {showResults && grantResults.length > 0 && <GrantResults grants={grantResults} />}
      </CardContent>
    </Card>
  )
}
