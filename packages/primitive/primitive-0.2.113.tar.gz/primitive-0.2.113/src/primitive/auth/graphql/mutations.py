from primitive.graphql.utility_fragments import operation_info_fragment

authentication_token_create = (
    operation_info_fragment
    + """
fragment AuthenticationTokenCreateFragment on AuthenticationToken {
  id
  pk
  createdAt
  keyName
  keySlug
  key
}

mutation authenticationTokenCreate($input: AuthenticationTokenCreateInput!) {
  authenticationTokenCreate(input: $input) {
    ...AuthenticationTokenCreateFragment
    ...OperationInfoFragment
  }
}
"""
)
