from primitive.graphql.utility_fragments import operation_info_fragment

operating_system_create_mutation = (
    operation_info_fragment
    + """
mutation operatingSystemCreate($input: OperatingSystemCreateInput!) {
    operatingSystemCreate(input: $input) {
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
        ...OperationInfoFragment
    }
}
"""
)


operating_system_update_mutation = (
    operation_info_fragment
    + """
mutation operatingSystemUpdate($input: OperatingSystemUpdateInput!) {
    operatingSystemUpdate(input: $input) {
        ... on OperatingSystem {
            id
            pk
        }
        ...OperationInfoFragment
    }
}
"""
)

operating_system_delete_mutation = (
    operation_info_fragment
    + """
mutation operatingSystemDelete($input: NodeInput!) {
    operatingSystemDelete(input: $input) {
        ... on OperatingSystem {
            id
            pk
            slug
        }
        ...OperationInfoFragment
    }
}
"""
)
