hardware_fragment = """
fragment HardwareFragment on Hardware {
  id
  pk
  name
  slug
  createdAt
  updatedAt
  isAvailable
  isOnline
  isQuarantined
  isHealthy
  isController
  systemInfo
  hostname

  requiresProvisioning
  requiresOperatingSystemInstallation

  defaultIpv4Address
  defaultMacAddress
  defaultBmcIpv4Address

  manufacturer {
    id
    pk
    name
    slug
  }
  organization {
    id
    pk
    name
    slug
  }
  defaultOperatingSystem {
    id
    pk
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
  activeReservation {
    id
    pk
    status
    reservationNumber
    reason
    hardware {
      id
    }
    createdBy {
      username
    }
  }
}
"""
