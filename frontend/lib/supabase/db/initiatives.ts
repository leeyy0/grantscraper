import supabase from "../client"
import type {
  Initiative,
  InitiativeInsert,
  InitiativeUpdate,
  Organisation,
  DbResult,
  DbResults,
} from "./types"

/**
 * Get all initiatives
 */
export async function getAll(): Promise<DbResults<Initiative>> {
  const { data, error } = await supabase
    .from("initiatives")
    .select("*")
    .order("id", { ascending: false })

  return { data, error }
}

/**
 * Get a single initiative by ID
 */
export async function getById(id: number): Promise<DbResult<Initiative>> {
  const { data, error } = await supabase
    .from("initiatives")
    .select("*")
    .eq("id", id)
    .single()

  return { data, error }
}

/**
 * Get initiatives by organisation
 */
export async function getByOrganisation(
  organisationId: number,
): Promise<DbResults<Initiative>> {
  const { data, error } = await supabase
    .from("initiatives")
    .select("*")
    .eq("organisation_id", organisationId)

  return { data, error }
}

/**
 * Get initiative with organisation details
 */
export async function getWithOrganisation(
  id: number,
): Promise<DbResult<Initiative & { organisations: Organisation }>> {
  const { data, error } = await supabase
    .from("initiatives")
    .select("*, organisations(*)")
    .eq("id", id)
    .single()

  return { data: data as any, error }
}

/**
 * Get initiatives by stage
 */
export async function getByStage(
  stage: string,
): Promise<DbResults<Initiative>> {
  const { data, error } = await supabase
    .from("initiatives")
    .select("*")
    .eq("stage", stage)

  return { data, error }
}

/**
 * Search initiatives by title
 */
export async function searchByTitle(
  searchTerm: string,
): Promise<DbResults<Initiative>> {
  const { data, error } = await supabase
    .from("initiatives")
    .select("*")
    .ilike("title", `%${searchTerm}%`)

  return { data, error }
}

/**
 * Create a new initiative
 */
export async function create(
  initiative: InitiativeInsert,
): Promise<DbResult<Initiative>> {
  const { data, error } = await supabase
    .from("initiatives")
    .insert(initiative)
    .select()
    .single()

  return { data, error }
}

/**
 * Update an initiative
 */
export async function update(
  id: number,
  updates: InitiativeUpdate,
): Promise<DbResult<Initiative>> {
  const { data, error } = await supabase
    .from("initiatives")
    .update(updates)
    .eq("id", id)
    .select()
    .single()

  return { data, error }
}

/**
 * Delete an initiative
 */
export async function deleteInitiative(
  id: number,
): Promise<DbResult<Initiative>> {
  const { data, error } = await supabase
    .from("initiatives")
    .delete()
    .eq("id", id)
    .select()
    .single()

  return { data, error }
}
