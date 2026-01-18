import type { Tables, TablesInsert, TablesUpdate } from "../database.types"

// ============================================================================
// Type Aliases for easier use
// ============================================================================

export type Grant = Tables<"grants">
export type GrantInsert = TablesInsert<"grants">
export type GrantUpdate = TablesUpdate<"grants">

export type Initiative = Tables<"initiatives">
export type InitiativeInsert = TablesInsert<"initiatives">
export type InitiativeUpdate = TablesUpdate<"initiatives">

export type Organisation = Tables<"organisations">
export type OrganisationInsert = TablesInsert<"organisations">
export type OrganisationUpdate = TablesUpdate<"organisations">

export type Result = Tables<"results">
export type ResultInsert = TablesInsert<"results">
export type ResultUpdate = TablesUpdate<"results">

// ============================================================================
// Generic Response Types
// ============================================================================

export type DbResult<T> = {
  data: T | null
  error: Error | null
}

export type DbResults<T> = {
  data: T[] | null
  error: Error | null
}
