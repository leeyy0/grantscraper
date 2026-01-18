import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getRatingColor(value: number, isUncertainty = false) {
  // For match rating: high = green, low = red
  // For uncertainty rating: low = green, high = red (inverted)
  const effectiveValue = isUncertainty ? 100 - value : value

  if (effectiveValue >= 70) {
    return "text-green-500"
  } else if (effectiveValue >= 40) {
    return "text-yellow-500"
  } else {
    return "text-red-500"
  }
}
