import supabase from "../client"
import type {
  Organisation,
  OrganisationInsert,
  OrganisationUpdate,
  Initiative,
  DbResult,
  DbResults,
} from "./types"

/**
 * Get all organisations
 */
export async function getAll(): Promise<DbResults<Organisation>> {
  const { data, error } = await supabase
    .from("organisations")
    .select("*")
    .order("name", { ascending: true })

  return { data, error }
}

/**
 * Get a single organisation by ID
 */
export async function getById(id: number): Promise<DbResult<Organisation>> {
  const { data, error } = await supabase
    .from("organisations")
    .select("*")
    .eq("id", id)
    .single()

  return { data, error }
}

/**
 * Get organisation with its initiatives
 */
export async function getWithInitiatives(
  id: number,
): Promise<DbResult<Organisation & { initiatives: Initiative[] }>> {
  const { data, error } = await supabase
    .from("organisations")
    .select("*, initiatives(*)")
    .eq("id", id)
    .single()

  return {
    data: data as (Organisation & { initiatives: Initiative[] }) | null,
    error,
  }
}

/**
 * Search organisations by name
 */
export async function searchByName(
  searchTerm: string,
): Promise<DbResults<Organisation>> {
  const { data, error } = await supabase
    .from("organisations")
    .select("*")
    .ilike("name", `%${searchTerm}%`)

  return { data, error }
}

/**
 * Create a new organisation
 */
export async function create(
  organisation: OrganisationInsert,
): Promise<DbResult<Organisation>> {
  const { data, error } = await supabase
    .from("organisations")
    .insert(organisation)
    .select()
    .single()

  return { data, error }
}

/**
 * Update an organisation
 */
export async function update(
  id: number,
  updates: OrganisationUpdate,
): Promise<DbResult<Organisation>> {
  const { data, error } = await supabase
    .from("organisations")
    .update(updates)
    .eq("id", id)
    .select()
    .single()

  return { data, error }
}

/**
 * Delete an organisation
 */
export async function deleteOrganisation(
  id: number,
): Promise<DbResult<Organisation>> {
  const { data, error } = await supabase
    .from("organisations")
    .delete()
    .eq("id", id)
    .select()
    .single()

  return { data, error }
}
