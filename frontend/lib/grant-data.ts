export interface GrantDetail {
  id: string
  match_rating: number
  uncertainty_rating: number
  grant_name: string
  grant_description: string
  criteria: string[]
  grant_amount: string
  grant_sponsors: string
  deadline: string | null
  sources: string[]
  explanations: {
    match_rating: string
    uncertainty_rating: string
  }
}

export const grantDetails: GrantDetail[] = [
  {
    id: "community-development-grant",
    match_rating: 92,
    uncertainty_rating: 8,
    grant_name: "Community Development Grant",
    grant_description:
      "This grant supports grassroots organisations working to strengthen local communities through sustainable development initiatives. The fund prioritizes projects that demonstrate measurable impact on community well-being and economic growth.",
    criteria: [
      "Organisation must be a registered 501(c)(3) nonprofit",
      "Minimum 2 years of operational history",
      "Annual budget under $500,000",
      "Project must serve underrepresented communities",
    ],
    grant_amount: "$50,000",
    grant_sponsors: "Ford Foundation",
    deadline: "2026-03-15T23:59:59",
    sources: [
      "https://www.fordfoundation.org/grants/community-development",
      "https://www.fordfoundation.org/apply",
    ],
    explanations: {
      match_rating:
        "Your organisation's focus on community empowerment and sustainable development aligns strongly with the grant's priorities. Your 5-year track record and budget size meet all eligibility criteria.",
      uncertainty_rating:
        "Low uncertainty due to clear eligibility criteria and your organisation's well-documented history of community impact.",
    },
  },
  {
    id: "youth-education-initiative-fund",
    match_rating: 85,
    uncertainty_rating: 12,
    grant_name: "Youth Education Initiative Fund",
    grant_description:
      "A collaborative funding program dedicated to improving educational outcomes for youth in underserved areas. The fund supports innovative approaches to learning, including technology integration, mentorship programs, and after-school initiatives.",
    criteria: [
      "Must focus on K-12 education",
      "Programs should target underserved youth populations",
      "Demonstrated partnership with local schools or educational institutions",
      "Clear metrics for measuring educational outcomes",
    ],
    grant_amount: "$75,000",
    grant_sponsors: "Gates Foundation, UNICEF",
    deadline: "2026-04-30T23:59:59",
    sources: [
      "https://www.gatesfoundation.org/education-grants",
      "https://www.unicef.org/funding/youth-education",
    ],
    explanations: {
      match_rating:
        "Your initiative's focus on youth education and technology integration aligns well with the fund's goals. Partnership with local schools strengthens your application.",
      uncertainty_rating:
        "Slight uncertainty due to competitive applicant pool and specific metrics requirements that may need additional documentation.",
    },
  },
  {
    id: "environmental-sustainability-grant",
    match_rating: 78,
    uncertainty_rating: 18,
    grant_name: "Environmental Sustainability Grant",
    grant_description:
      "This grant supports organisations implementing innovative environmental solutions at the local level. Priority is given to projects addressing climate resilience, renewable energy adoption, and community-based conservation efforts.",
    criteria: [
      "Project must address measurable environmental impact",
      "Community engagement component required",
      "Matching funds of at least 20% preferred",
      "Implementation timeline of 12-24 months",
    ],
    grant_amount: "$120,000",
    grant_sponsors: "Bloomberg Philanthropies",
    deadline: "2026-05-20T23:59:59",
    sources: [
      "https://www.bloomberg.org/environment/grants",
      "https://www.bloomberg.org/apply-for-funding",
    ],
    explanations: {
      match_rating:
        "Your environmental initiatives show good alignment with sustainability goals. Community engagement approach matches the grant's priorities.",
      uncertainty_rating:
        "Moderate uncertainty due to matching funds requirement and competitive selection process focused on measurable impact metrics.",
    },
  },
  {
    id: "healthcare-access-program",
    match_rating: 71,
    uncertainty_rating: 70,
    grant_name: "Healthcare Access Program",
    grant_description:
      "Funding for organisations working to expand healthcare access in underserved communities. The program supports mobile health clinics, telehealth initiatives, preventive care programs, and health education campaigns.",
    criteria: [
      "Must serve populations with limited healthcare access",
      "Licensed healthcare professionals required on staff or as partners",
      "Compliance with HIPAA and local health regulations",
      "Sustainability plan for program continuation",
    ],
    grant_amount: "$90,000",
    grant_sponsors: "Rockefeller Foundation",
    deadline: "2026-06-01T23:59:59",
    sources: [
      "https://www.rockefellerfoundation.org/health-grants",
      "https://www.rockefellerfoundation.org/our-work/healthcare",
    ],
    explanations: {
      match_rating:
        "Your organisation shows potential alignment with healthcare access goals, though primary focus may differ from the grant's specific healthcare priorities.",
      uncertainty_rating:
        "High uncertainty due to strict regulatory compliance requirements and the need for licensed healthcare partnerships that may not be established.",
    },
  },
  {
    id: "digital-inclusion-fund",
    match_rating: 4,
    uncertainty_rating: 30,
    grant_name: "Digital Inclusion Fund",
    grant_description:
      "Supporting initiatives that bridge the digital divide by providing technology access, digital literacy training, and connectivity solutions to underserved populations. Focus areas include rural connectivity, senior digital education, and youth coding programs.",
    criteria: [
      "Project must address digital equity gaps",
      "Training or education component required",
      "Partnership with technology providers preferred",
      "Scalability potential for broader impact",
    ],
    grant_amount: "$40,000",
    grant_sponsors: "Google.org, Microsoft",
    deadline: "2026-07-15T23:59:59",
    sources: [
      "https://www.google.org/digital-inclusion",
      "https://www.microsoft.com/en-us/corporate-responsibility/philanthropies",
    ],
    explanations: {
      match_rating:
        "Your organisation's current focus does not strongly align with digital inclusion priorities. Limited technology-focused initiatives in your program portfolio.",
      uncertainty_rating:
        "Moderate uncertainty as eligibility requirements are flexible, but your organisation would need to demonstrate stronger digital equity focus.",
    },
  },
]

export function getGrantById(id: string): GrantDetail | undefined {
  return grantDetails.find((grant) => grant.id === id)
}
