"use client"

import { createContext, useContext, useState, useEffect, useRef, type ReactNode } from "react"
import type { OrganizationFormInput } from "@/components/organization-form"
import type { InitiativeFormInput } from "@/components/initiative-form"
import type { GrantResult } from "@/components/grants-results"

interface FormContextType {
  organizationForm: OrganizationFormInput
  setOrganizationForm: (data: OrganizationFormInput) => void
  initiativeForm: InitiativeFormInput
  setInitiativeForm: (data: InitiativeFormInput) => void
  showResults: boolean
  setShowResults: (show: boolean) => void
  grantResults: GrantResult[]
  setGrantResults: (results: GrantResult[]) => void
  accordionValue: string[]
  setAccordionValue: (value: string[]) => void
}

const FormContext = createContext<FormContextType | undefined>(undefined)

const STORAGE_KEY = "form-context-state"

interface PersistedState {
  organizationForm: OrganizationFormInput
  initiativeForm: InitiativeFormInput
  showResults: boolean
  grantResults: GrantResult[]
  accordionValue: string[]
}

function getInitialState(): PersistedState {
  if (typeof window === "undefined") {
    return {
      organizationForm: {
        name: "",
        mission_and_focus: "",
        about_us: "",
        remarks: "",
      },
      initiativeForm: {
        title: "",
        goals_objective: "",
        audience_beneficiaries: "",
        estimated_cost: "",
        stage_of_initiative: "",
        demographic: "",
        remarks: "",
      },
      showResults: false,
      grantResults: [],
      accordionValue: ["organization", "initiative"],
    }
  }

  try {
    const stored = sessionStorage.getItem(STORAGE_KEY)
    if (stored) {
      return JSON.parse(stored)
    }
  } catch (e) {
    console.error("Failed to parse stored state:", e)
  }

  return {
    organizationForm: {
      name: "",
      mission_and_focus: "",
      about_us: "",
      remarks: "",
    },
    initiativeForm: {
      title: "",
      goals_objective: "",
      audience_beneficiaries: "",
      estimated_cost: "",
      stage_of_initiative: "",
      demographic: "",
      remarks: "",
    },
    showResults: false,
    grantResults: [],
    accordionValue: ["organization", "initiative"],
  }
}

export function FormProvider({ children }: { children: ReactNode }) {
  const initialized = useRef(false)

  const [organizationForm, setOrganizationForm] = useState<OrganizationFormInput>({
    name: "",
    mission_and_focus: "",
    about_us: "",
    remarks: "",
  })

  const [initiativeForm, setInitiativeForm] = useState<InitiativeFormInput>({
    title: "",
    goals_objective: "",
    audience_beneficiaries: "",
    estimated_cost: "",
    stage_of_initiative: "",
    demographic: "",
    remarks: "",
  })

  const [showResults, setShowResults] = useState(false)
  const [grantResults, setGrantResults] = useState<GrantResult[]>([])
  const [accordionValue, setAccordionValue] = useState<string[]>(["organization", "initiative"])

  useEffect(() => {
    if (!initialized.current) {
      const storedState = getInitialState()
      setOrganizationForm(storedState.organizationForm)
      setInitiativeForm(storedState.initiativeForm)
      setShowResults(storedState.showResults)
      setGrantResults(storedState.grantResults)
      setAccordionValue(storedState.accordionValue)
      initialized.current = true
    }
  }, [])

  useEffect(() => {
    if (initialized.current) {
      const state: PersistedState = {
        organizationForm,
        initiativeForm,
        showResults,
        grantResults,
        accordionValue,
      }
      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state))
      } catch (e) {
        console.error("Failed to save state:", e)
      }
    }
  }, [organizationForm, initiativeForm, showResults, grantResults, accordionValue])

  return (
    <FormContext.Provider
      value={{
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
      }}
    >
      {children}
    </FormContext.Provider>
  )
}

export function useFormContext() {
  const context = useContext(FormContext)
  if (context === undefined) {
    throw new Error("useFormContext must be used within a FormProvider")
  }
  return context
}
