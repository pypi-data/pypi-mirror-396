operating_system_list_query = """
query operatingSystemList(
$filters: OperatingSystemFilters
) {
    operatingSystemList(
        filters: $filters
    ) {
        totalCount
        edges {
          cursor
          node {
            ... on OperatingSystem {
                id
                pk
                createdAt
                updatedAt
                slug
                organization {
                  id
                  slug
                }
                isoFile {
                  id
                  fileName
                }
                checksumFile {
                  id
                  fileName
                }
                checksumFileType
            }
          }
        }
    }
} 
"""
