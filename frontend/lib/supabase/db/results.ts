import supabase from "../client"
import type {
  Result,
  ResultInsert,
  ResultUpdate,
  Grant,
  Initiative,
  DbResult,
  DbResults,
} from "./types"

/**
 * Get all results
 */
export async function getAll(): Promise<DbResults<Result>> {
  const { data, error } = await supabase
    .from("results")
    .select("*")
    .order("prelim_rating", { ascending: false })

  return { data, error }
}

/**
 * Get results by initiative
 */
export async function getByInitiative(
  initiativeId: number,
): Promise<DbResults<Result>> {
  const { data, error } = await supabase
    .from("results")
    .select("*")
    .eq("initiative_id", initiativeId)
    .order("match_rating", { ascending: false })

  return { data, error }
}

/**
 * Get count of shortlisted grants for an initiative (prelim_rating > 61)
 */
export async function getShortlistedCount(
  initiativeId: number,
): Promise<{ count: number; error: Error | null }> {
  const { count, error } = await supabase
    .from("results")
    .select("*", { count: "exact", head: true })
    .eq("initiative_id", initiativeId)
    .gt("prelim_rating", 61)

  return { count: count || 0, error }
}

/**
 * Get results by grant
 */
export async function getByGrant(grantId: number): Promise<DbResults<Result>> {
  const { data, error } = await supabase
    .from("results")
    .select("*")
    .eq("grant_id", grantId)
    .order("match_rating", { ascending: false })

  return { data, error }
}

/**
 * Get result with grant and initiative details
 */
export async function getByInitiativeWithDetails(
  initiativeId: number,
): Promise<DbResults<Result & { grants: Grant; initiatives: Initiative }>> {
  const { data, error } = await supabase
    .from("results")
    .select("*, grants(*), initiatives(*)")
    .eq("initiative_id", initiativeId)

  // Sort the data with custom logic:
  // 1. Records with match_rating should come first, ordered by (match_rating - uncertainty_rating) descending
  // 2. Records with null match_rating should come after, ordered by prelim_rating descending
  const sortedData =
    data?.sort((a, b) => {
      const hasMatchRatingA = a.match_rating !== null
      const hasMatchRatingB = b.match_rating !== null

      // If both have match_rating, sort by (match_rating - uncertainty_rating) descending
      if (hasMatchRatingA && hasMatchRatingB) {
        const scoreA = (a.match_rating ?? 0) - (a.uncertainty_rating ?? 0)
        const scoreB = (b.match_rating ?? 0) - (b.uncertainty_rating ?? 0)
        return scoreB - scoreA // descending
      }

      // If only A has match_rating, A comes first
      if (hasMatchRatingA && !hasMatchRatingB) {
        return -1
      }

      // If only B has match_rating, B comes first
      if (!hasMatchRatingA && hasMatchRatingB) {
        return 1
      }

      // If both have null match_rating, sort by prelim_rating descending
      const prelimA = a.prelim_rating ?? 0
      const prelimB = b.prelim_rating ?? 0
      return prelimB - prelimA // descending
    }) ?? null

  return {
    data: sortedData as
      | (Result & { grants: Grant; initiatives: Initiative })[]
      | null,
    error,
  }
}

/**
 * Get top matches for an initiative
 */
export async function getTopMatches(
  initiativeId: number,
  limit: number = 10,
): Promise<DbResults<Result>> {
  const { data, error } = await supabase
    .from("results")
    .select("*")
    .eq("initiative_id", initiativeId)
    .not("match_rating", "is", null)
    .order("match_rating", { ascending: false })
    .limit(limit)

  return { data, error }
}

/**
 * Get results by match rating range
 */
export async function getByMatchRatingRange(
  min: number,
  max: number,
): Promise<DbResults<Result>> {
  const { data, error } = await supabase
    .from("results")
    .select("*")
    .gte("match_rating", min)
    .lte("match_rating", max)
    .order("match_rating", { ascending: false })

  return { data, error }
}

/**
 * Create a new result
 */
export async function create(result: ResultInsert): Promise<DbResult<Result>> {
  const { data, error } = await supabase
    .from("results")
    .insert(result)
    .select()
    .single()

  return { data, error }
}

/**
 * Create multiple results
 */
export async function createMany(
  results: ResultInsert[],
): Promise<DbResults<Result>> {
  const { data, error } = await supabase
    .from("results")
    .insert(results)
    .select()

  return { data, error }
}

/**
 * Update a result
 */
export async function update(
  grantId: number,
  initiativeId: number,
  updates: ResultUpdate,
): Promise<DbResult<Result>> {
  const { data, error } = await supabase
    .from("results")
    .update(updates)
    .eq("grant_id", grantId)
    .eq("initiative_id", initiativeId)
    .select()
    .single()

  return { data, error }
}

/**
 * Delete results for an initiative
 */
export async function deleteByInitiative(
  initiativeId: number,
): Promise<DbResults<Result>> {
  const { data, error } = await supabase
    .from("results")
    .delete()
    .eq("initiative_id", initiativeId)
    .select()

  return { data, error }
}

/**
 * Delete results for a grant
 */
export async function deleteByGrant(
  grantId: number,
): Promise<DbResults<Result>> {
  const { data, error } = await supabase
    .from("results")
    .delete()
    .eq("grant_id", grantId)
    .select()

  return { data, error }
}
