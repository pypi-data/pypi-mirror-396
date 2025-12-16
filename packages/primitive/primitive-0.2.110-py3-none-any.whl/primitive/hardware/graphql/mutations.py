from primitive.graphql.utility_fragments import operation_info_fragment
from primitive.hardware.graphql.fragments import hardware_fragment

hardware_certificate_create_mutation = (
    operation_info_fragment
    + """
mutation hardwareCertificateCreate($input: HardwareCertificateCreateInput!) {
    hardwareCertificateCreate(input: $input) {
        __typename
        ... on HardwareCertificate {
            id
            certificatePem
        }
        ...OperationInfoFragment
    }
}
"""
)

register_hardware_mutation = (
    operation_info_fragment
    + """
mutation registerHardware($input: RegisterHardwareInput!) {
    registerHardware(input: $input) {
        __typename
        ... on Hardware {
            id
            pk
            fingerprint
        }
        ...OperationInfoFragment
    }
}
"""
)

register_child_hardware_mutation = (
    operation_info_fragment
    + """
mutation registerChildHardware($input: RegisterChildHardwareInput!) {
    registerChildHardware(input: $input) {
        __typename
        ... on Hardware {
            fingerprint
        }
        ...OperationInfoFragment
    }
}
"""
)

unregister_hardware_mutation = (
    operation_info_fragment
    + """
mutation unregisterHardware($input: UnregisterHardwareInput!) {
    unregisterHardware(input: $input) {
        __typename
        ... on Hardware {
            fingerprint
        }
        ...OperationInfoFragment
    }
}
"""
)

hardware_update_system_info_mutation = (
    operation_info_fragment
    + """
mutation hardwareUpdate($input: HardwareUpdateInput!) {
    hardwareUpdate(input: $input) {
        __typename
        ... on Hardware {
            systemInfo
        }
        ...OperationInfoFragment
    }
}
"""
)

hardware_update_mutation = (
    operation_info_fragment
    + hardware_fragment
    + """
mutation xx($input: HardwareUpdateInput!) {
    hardwareUpdate(input: $input) {
        __typename
        ... on Hardware {
            ...HardwareFragment
        }
        ...OperationInfoFragment
    }
}
"""
)

hardware_checkin_mutation = (
    operation_info_fragment
    + """
mutation checkIn($input: CheckInInput!) {
    checkIn(input: $input) {
        __typename
        ... on Hardware {
            createdAt
            updatedAt
            lastCheckIn
        }
        ...OperationInfoFragment
    }
}
"""
)
