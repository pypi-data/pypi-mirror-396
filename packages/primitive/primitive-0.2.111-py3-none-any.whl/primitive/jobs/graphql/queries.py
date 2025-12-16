from primitive.graphql.utility_fragments import page_info_fragment

from .fragments import job_fragment, job_run_fragment, job_run_status_fragment

jobs_query = (
    page_info_fragment
    + job_fragment
    + """
query jobs(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $filters: JobFilters
) {
    jobs(
        before: $before
        after: $after
        first: $first
        last: $last
        filters: $filters
    ) {
        totalCount
        pageInfo {
            ...PageInfoFragment
        }
        edges {
            cursor
            node {
                ...JobFragment
            }
        }
    }
}
"""
)


job_runs_query = (
    page_info_fragment
    + job_run_fragment
    + """
query jobRuns(
  $before: String
  $after: String
  $first: Int
  $last: Int
  $filters: JobRunFilters
  $order: JobRunOrder
) {
  jobRuns(
    before: $before
    after: $after
    first: $first
    last: $last
    filters: $filters
    order: $order
  ) {
    totalCount
    pageInfo {
      ...PageInfoFragment
    }
    edges {
      cursor
      node {
        ...JobRunFragment
      }
    }
  }
}
"""
)

job_run_query = (
    job_run_fragment
    + """
query jobRun($id: ID!) {
    jobRun(id: $id) {
        ...JobRunFragment
    }
}
"""
)

github_app_token_for_job_run_query = """
query ghAppTokenForJobRun($jobRunId: ID!) {
    ghAppTokenForJobRun(jobRunId: $jobRunId)
}
"""

job_run_status_query = (
    job_run_status_fragment
    + """
query jobRun($id: ID!) {
    jobRun(id: $id) {
        ...JobRunStatusFragment
    }
}
"""
)


job_secrets_for_job_run_query = """
query jobSecretsForJobRun($jobRunId: ID!) {
    jobSecretsForJobRun(jobRunId: $jobRunId)
}
"""
