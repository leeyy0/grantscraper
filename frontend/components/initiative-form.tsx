"use client"

import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"

export interface InitiativeFormInput {
  title: string
  goals_objective: string
  audience_beneficiaries: string
  estimated_cost: string
  stage_of_initiative: string
  demographic: string
  remarks: string
}

export interface InitiativeFormErrors {
  title?: string
  goals_objective?: string
  audience_beneficiaries?: string
  estimated_cost?: string
  stage_of_initiative?: string
  demographic?: string
  remarks?: string
}

interface InitiativeFormProps {
  formData: InitiativeFormInput
  onChange: (data: InitiativeFormInput) => void
  errors: InitiativeFormErrors
}

export function InitiativeForm({ formData, onChange, errors }: InitiativeFormProps) {
  return (
    <div className="space-y-4 pt-4">
      <div className="space-y-2">
        <Label htmlFor="init-title">
          Title <span className="text-destructive">*</span>
        </Label>
        <Input
          id="init-title"
          placeholder="Enter initiative title"
          value={formData.title}
          onChange={(e) => onChange({ ...formData, title: e.target.value })}
        />
        {errors.title && <p className="text-sm text-destructive">{errors.title}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="goals">
          Goals/Objective of the Initiative <span className="text-destructive">*</span>
        </Label>
        <Textarea
          id="goals"
          placeholder="Describe the goals and objectives"
          rows={3}
          value={formData.goals_objective}
          onChange={(e) => onChange({ ...formData, goals_objective: e.target.value })}
        />
        {errors.goals_objective && <p className="text-sm text-destructive">{errors.goals_objective}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="audience">
          Audience/Target Beneficiaries <span className="text-destructive">*</span>
        </Label>
        <Textarea
          id="audience"
          placeholder="Who will benefit from this initiative?"
          rows={2}
          value={formData.audience_beneficiaries}
          onChange={(e) => onChange({ ...formData, audience_beneficiaries: e.target.value })}
        />
        {errors.audience_beneficiaries && <p className="text-sm text-destructive">{errors.audience_beneficiaries}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="cost">Estimated Cost of the Initiative in SGD (Optional)</Label>
        <Input
          id="cost"
          type="number"
          min={0}
          placeholder="Enter estimated cost"
          value={formData.estimated_cost}
          onChange={(e) => onChange({ ...formData, estimated_cost: e.target.value })}
        />
        {errors.estimated_cost && <p className="text-sm text-destructive">{errors.estimated_cost}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="stage">Stage of Initiative (Optional)</Label>
        <Input
          id="stage"
          placeholder="Enter stage of initiative"
          value={formData.stage_of_initiative}
          onChange={(e) => onChange({ ...formData, stage_of_initiative: e.target.value })}
        />
        {errors.stage_of_initiative && <p className="text-sm text-destructive">{errors.stage_of_initiative}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="demographic">Demographic (Optional)</Label>
        <Input
          id="demographic"
          placeholder="Enter target demographic"
          value={formData.demographic}
          onChange={(e) => onChange({ ...formData, demographic: e.target.value })}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="init-remarks">Remarks (Optional)</Label>
        <Textarea
          id="init-remarks"
          placeholder="Any additional remarks"
          rows={2}
          value={formData.remarks}
          onChange={(e) => onChange({ ...formData, remarks: e.target.value })}
        />
      </div>
    </div>
  )
}
