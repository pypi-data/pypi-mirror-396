from .fragments import hardware_fragment

hardware_list = (
    hardware_fragment
    + """

query hardwareList(
  $before: String
  $after: String
  $first: Int
  $last: Int
  $filters: HardwareFilters
) {
  hardwareList(
    before: $before
    after: $after
    first: $first
    last: $last
    filters: $filters
  ) {
    totalCount
    edges {
      cursor
      node {
        ...HardwareFragment
      }
    }
  }
}
"""
)

hardware_with_parent_list = (
    hardware_fragment
    + """
query hardwareWithParentList(
  $before: String
  $after: String
  $first: Int
  $last: Int
  $filters: HardwareFilters
) {
  hardwareList(
    before: $before
    after: $after
    first: $first
    last: $last
    filters: $filters
  ) {
    totalCount
    edges {
      cursor
      node {
        ...HardwareFragment
        parent {
          id
          pk
          name
          slug
          defaultIpv4Address
          defaultMacAddress
          defaultBmcIpv4Address
          manufacturer {
            id
            pk
            name
            slug
          }
        }
      }
    }
  }
}
"""
)

nested_children_hardware_list = (
    hardware_fragment
    + """

query hardwareList(
  $before: String
  $after: String
  $first: Int
  $last: Int
  $filters: HardwareFilters
) {
  hardwareList(
    before: $before
    after: $after
    first: $first
    last: $last
    filters: $filters
  ) {
    totalCount
    edges {
      cursor
      node {
        ...HardwareFragment
        children {
          ...HardwareFragment
          fingerprint
        }
      }
    }
  }
}
"""
)

hardware_details = (
    hardware_fragment
    + """

query hardwareDetails(
  $before: String
  $after: String
  $first: Int
  $last: Int
  $filters: HardwareFilters
) {
  hardwareList(
    before: $before
    after: $after
    first: $first
    last: $last
    filters: $filters
  ) {
    totalCount
    edges {
      cursor
      node {
        ...HardwareFragment
        children {
          ...HardwareFragment
          fingerprint
        }
      }
    }
  }
}
"""
)

hardware_details_with_controller = (
    hardware_fragment
    + """

query hardwareDetails(
  $before: String
  $after: String
  $first: Int
  $last: Int
  $filters: HardwareFilters
) {
  hardwareList(
    before: $before
    after: $after
    first: $first
    last: $last
    filters: $filters
  ) {
    totalCount
    edges {
      cursor
      node {
        ...HardwareFragment
        children {
          ...HardwareFragment
          fingerprint
        }
        controller {
          id
          pk
          name
          slug
          defaultIpv4Address
          defaultMacAddress
          defaultBmcIpv4Address
        }
      }
    }
  }
}
"""
)


hardware_secret = """
query hardwareSecret($hardwareId: ID!) {
  hardwareSecret(hardwareId: $hardwareId)
}
"""
