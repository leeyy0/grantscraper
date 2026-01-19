"use client"

import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react"
import type { OrganisationFormInput } from "@/components/organisation-form"
import type { InitiativeFormInput } from "@/components/initiative-form"
import type { GrantResult } from "@/components/grants-results"

interface FormContextType {
  organisationForm: OrganisationFormInput
  setOrganisationForm: (data: OrganisationFormInput) => void
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
  organisationForm: OrganisationFormInput
  initiativeForm: InitiativeFormInput
  showResults: boolean
  grantResults: GrantResult[]
  accordionValue: string[]
}

function getInitialState(): PersistedState {
  if (typeof window === "undefined") {
    return {
      organisationForm: {
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
      accordionValue: ["organisation", "initiative"],
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
    organisationForm: {
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
    accordionValue: ["organisation", "initiative"],
  }
}

export function FormProvider({ children }: { children: ReactNode }) {
  const [organisationForm, setOrganisationForm] =
    useState<OrganisationFormInput>(() => getInitialState().organisationForm)
  const [initiativeForm, setInitiativeForm] = useState<InitiativeFormInput>(
    () => getInitialState().initiativeForm,
  )
  const [showResults, setShowResults] = useState(
    () => getInitialState().showResults,
  )
  const [grantResults, setGrantResults] = useState<GrantResult[]>(
    () => getInitialState().grantResults,
  )
  const [accordionValue, setAccordionValue] = useState<string[]>(
    () => getInitialState().accordionValue,
  )

  useEffect(() => {
    const state: PersistedState = {
      organisationForm,
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
  }, [
    organisationForm,
    initiativeForm,
    showResults,
    grantResults,
    accordionValue,
  ])

  return (
    <FormContext.Provider
      value={{
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
