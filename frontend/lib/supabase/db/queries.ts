import supabase from "../client"
import * as grants from "./grants"
import * as organisations from "./organisations"
import * as initiatives from "./initiatives"

/**
 * Get complete initiative analysis with organisation, results, and grants
 */
export async function getInitiativeAnalysis(initiativeId: number) {
  const { data, error } = await supabase
    .from("initiatives")
    .select(`
      *,
      organisations(*),
      results(
        *,
        grants(*)
      )
    `)
    .eq("id", initiativeId)
    .single()
  
  return { data, error }
}

/**
 * Get organisation with all initiatives and their results
 */
export async function getOrganisationComplete(organisationId: number) {
  const { data, error } = await supabase
    .from("organisations")
    .select(`
      *,
      initiatives(
        *,
        results(
          *,
          grants(*)
        )
      )
    `)
    .eq("id", organisationId)
    .single()
  
  return { data, error }
}

/**
 * Get grant with all matched initiatives
 */
export async function getGrantWithMatches(grantId: number) {
  const { data, error } = await supabase
    .from("grants")
    .select(`
      *,
      results(
        *,
        initiatives(
          *,
          organisations(*)
        )
      )
    `)
    .eq("id", grantId)
    .single()
  
  return { data, error }
}

/**
 * Search across all entities
 */
export async function globalSearch(searchTerm: string) {
  const [grantsResult, orgsResult, initiativesResult] = await Promise.all([
    grants.searchByName(searchTerm),
    organisations.searchByName(searchTerm),
    initiatives.searchByTitle(searchTerm),
  ])

  return {
    grants: grantsResult.data || [],
    organisations: orgsResult.data || [],
    initiatives: initiativesResult.data || [],
    errors: [grantsResult.error, orgsResult.error, initiativesResult.error].filter(Boolean),
  }
}
