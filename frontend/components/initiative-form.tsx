"use client"

import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"

export interface InitiativeFormInput {
  title: string
  stage: string
  audience: string
  goals: string
  costs: string
  demographic: string
  remarks: string
  organisation_id: number
}

export interface InitiativeFormErrors {
  title?: string
  stage?: string
  audience?: string
  goals?: string
  costs?: string
  demographic?: string
  remarks?: string
  organisation_id?: string
}

interface InitiativeFormProps {
  formData: InitiativeFormInput
  onChange: (data: InitiativeFormInput) => void
  errors: InitiativeFormErrors
}

export function InitiativeForm({
  formData,
  onChange,
  errors,
}: InitiativeFormProps) {
  return (
    <div className="space-y-4 pt-4">
      <div className="space-y-2">
        <Label htmlFor="title">
          Title <span className="text-destructive">*</span>
        </Label>
        <Input
          id="title"
          placeholder="Enter initiative title"
          value={formData.title}
          onChange={(e) => onChange({ ...formData, title: e.target.value })}
        />
        {errors.title && (
          <p className="text-destructive text-sm">{errors.title}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="stage">
          Stage <span className="text-destructive">*</span>
        </Label>
        <Input
          id="stage"
          placeholder="e.g., Planning, Active, Completed"
          value={formData.stage}
          onChange={(e) => onChange({ ...formData, stage: e.target.value })}
        />
        {errors.stage && (
          <p className="text-destructive text-sm">{errors.stage}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="audience">
          Audience <span className="text-destructive">*</span>
        </Label>
        <Input
          id="audience"
          placeholder="Target audience for this initiative"
          value={formData.audience}
          onChange={(e) => onChange({ ...formData, audience: e.target.value })}
        />
        {errors.audience && (
          <p className="text-destructive text-sm">{errors.audience}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="goals">
          Goals <span className="text-destructive">*</span>
        </Label>
        <Textarea
          id="goals"
          placeholder="Describe the goals of this initiative"
          className="min-h-32"
          rows={4}
          value={formData.goals}
          onChange={(e) => onChange({ ...formData, goals: e.target.value })}
        />
        {errors.goals && (
          <p className="text-destructive text-sm">{errors.goals}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="costs">Estimated Costs (Optional)</Label>
        <Input
          id="costs"
          type="number"
          placeholder="0"
          value={formData.costs}
          onChange={(e) => onChange({ ...formData, costs: e.target.value })}
        />
        {errors.costs && (
          <p className="text-destructive text-sm">{errors.costs}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="demographic">Demographic (Optional)</Label>
        <Input
          id="demographic"
          placeholder="Target demographic"
          value={formData.demographic}
          onChange={(e) =>
            onChange({ ...formData, demographic: e.target.value })
          }
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="remarks">Remarks (Optional)</Label>
        <Textarea
          id="remarks"
          className="min-h-24"
          placeholder="Any additional remarks"
          rows={3}
          value={formData.remarks}
          onChange={(e) => onChange({ ...formData, remarks: e.target.value })}
        />
      </div>
    </div>
  )
}
