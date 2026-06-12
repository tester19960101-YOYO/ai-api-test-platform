export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface Project {
  id: number
  name: string
  description?: string | null
  owner_name?: string | null
  status: string
  config?: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface Environment {
  id: number
  project_id: number
  name: string
  base_url: string
  variables?: Record<string, unknown> | null
  headers?: Record<string, unknown> | null
  is_default: boolean
  status: string
  created_at: string
  updated_at: string
}

export interface ApiEndpoint {
  id: number
  project_id: number
  api_document_id?: number | null
  name: string
  group_name?: string | null
  method: string
  path: string
  description?: string | null
  headers?: Record<string, unknown> | null
  request_params?: Record<string, unknown> | null
  request_body_schema?: Record<string, unknown> | null
  response_schema?: Record<string, unknown> | null
  example_request?: Record<string, unknown> | null
  example_response?: Record<string, unknown> | null
  auth_required: boolean
  tags?: unknown[] | null
  status: string
  created_at: string
  updated_at: string
}

export interface TestCase {
  id: number
  project_id: number
  api_endpoint_id?: number | null
  name: string
  description?: string | null
  priority: string
  status: string
  steps?: unknown[] | null
  assertions?: unknown[] | null
  variables?: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface ExecutionTask {
  id: number
  project_id: number
  environment_id?: number | null
  task_name: string
  status: string
  trigger_type: string
  total_cases: number
  passed_cases: number
  failed_cases: number
  started_at?: string | null
  finished_at?: string | null
  config?: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface ExecutionResult {
  id: number
  execution_task_id: number
  test_case_id?: number | null
  api_endpoint_id?: number | null
  status: string
  status_code?: number | null
  response_time_ms?: number | null
  request_data?: Record<string, unknown> | null
  response_data?: Record<string, unknown> | null
  assertion_result?: Record<string, unknown> | null
  error_message?: string | null
  created_at: string
  updated_at: string
}

export interface TestReport {
  id: number
  execution_task_id: number
  project_id: number
  title: string
  summary?: Record<string, unknown> | null
  report_path?: string | null
  status: string
  created_at: string
  updated_at: string
}

export interface ApiDocumentImportResult {
  document: Record<string, unknown>
  endpoints: ApiEndpoint[]
  endpoint_count: number
}

export interface AiGenerationResult {
  endpoint_id: number
  analysis_record_id: number
  case_count: number
  test_cases: TestCase[]
}

export interface ExecutionRunResponse {
  task: ExecutionTask
  results: ExecutionResult[]
  report: TestReport
  generated_project_path: string
  report_path: string
  log_path: string
  pytest_exit_code: number
  stdout: string
  stderr: string
}
