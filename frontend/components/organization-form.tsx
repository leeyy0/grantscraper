"use client"

import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"

export interface OrganizationFormInput {
  name: string
  mission_and_focus: string
  about_us: string
  remarks: string
}

export interface OrganizationFormErrors {
  name?: string
  mission_and_focus?: string
  about_us?: string
  remarks?: string
}

interface OrganizationFormProps {
  formData: OrganizationFormInput
  onChange: (data: OrganizationFormInput) => void
  errors: OrganizationFormErrors
}

export function OrganizationForm({ formData, onChange, errors }: OrganizationFormProps) {
  return (
    <div className="space-y-4 pt-4">
      <div className="space-y-2">
        <Label htmlFor="org-name">
          Name <span className="text-destructive">*</span>
        </Label>
        <Input
          id="org-name"
          placeholder="Enter organization name"
          value={formData.name}
          onChange={(e) => onChange({ ...formData, name: e.target.value })}
        />
        {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="mission">
          Mission and Focus <span className="text-destructive">*</span>
        </Label>
        <Textarea
          id="mission"
          placeholder="Describe your mission and focus"
          rows={3}
          value={formData.mission_and_focus}
          onChange={(e) => onChange({ ...formData, mission_and_focus: e.target.value })}
        />
        {errors.mission_and_focus && <p className="text-sm text-destructive">{errors.mission_and_focus}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="about">
          About Us <span className="text-destructive">*</span>
        </Label>
        <Textarea
          id="about"
          placeholder="Tell us about your organization"
          rows={4}
          value={formData.about_us}
          onChange={(e) => onChange({ ...formData, about_us: e.target.value })}
        />
        {errors.about_us && <p className="text-sm text-destructive">{errors.about_us}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="org-remarks">Remarks (Optional)</Label>
        <Textarea
          id="org-remarks"
          placeholder="Any additional remarks"
          rows={2}
          value={formData.remarks}
          onChange={(e) => onChange({ ...formData, remarks: e.target.value })}
        />
      </div>
    </div>
  )
}
