file_fragment = """
fragment FileFragment on File {
  id
  pk
  createdAt
  updatedAt
  createdBy {
    id
    pk
    username
  }
  location
  fileName
  fileSize
  fileChecksum
  isUploading
  isComplete
  partsDetails
  humanReadableMemorySize
}
"""
