import supabase from "../client"
import type { Grant, GrantInsert, GrantUpdate, DbResult, DbResults } from "./types"

/**
 * Get all grants
 */
export async function getAll(): Promise<DbResults<Grant>> {
  const { data, error } = await supabase
    .from("grants")
    .select("*")
    .order("id", { ascending: false })
  
  return { data, error }
}

/**
 * Get a single grant by ID
 */
export async function getById(id: number): Promise<DbResult<Grant>> {
  const { data, error } = await supabase
    .from("grants")
    .select("*")
    .eq("id", id)
    .single()
  
  return { data, error }
}

/**
 * Get grants by URL
 */
export async function getByUrl(url: string): Promise<DbResults<Grant>> {
  const { data, error } = await supabase
    .from("grants")
    .select("*")
    .eq("url", url)
  
  return { data, error }
}

/**
 * Search grants by name
 */
export async function searchByName(searchTerm: string): Promise<DbResults<Grant>> {
  const { data, error } = await supabase
    .from("grants")
    .select("*")
    .ilike("name", `%${searchTerm}%`)
  
  return { data, error }
}

/**
 * Create a new grant
 */
export async function create(grant: GrantInsert): Promise<DbResult<Grant>> {
  const { data, error } = await supabase
    .from("grants")
    .insert(grant)
    .select()
    .single()
  
  return { data, error }
}

/**
 * Create multiple grants
 */
export async function createMany(grants: GrantInsert[]): Promise<DbResults<Grant>> {
  const { data, error } = await supabase
    .from("grants")
    .insert(grants)
    .select()
  
  return { data, error }
}

/**
 * Update a grant
 */
export async function update(id: number, updates: GrantUpdate): Promise<DbResult<Grant>> {
  const { data, error } = await supabase
    .from("grants")
    .update(updates)
    .eq("id", id)
    .select()
    .single()
  
  return { data, error }
}

/**
 * Delete a grant
 */
export async function deleteGrant(id: number): Promise<DbResult<Grant>> {
  const { data, error } = await supabase
    .from("grants")
    .delete()
    .eq("id", id)
    .select()
    .single()
  
  return { data, error }
}
