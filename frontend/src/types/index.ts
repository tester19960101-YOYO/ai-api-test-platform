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
  endpoint?: {
    id?: number | null
    name?: string | null
    method?: string | null
    path?: string | null
  } | null
  endpoint_name?: string | null
  endpoint_path?: string | null
  name: string
  description?: string | null
  type: string
  priority: string
  status: string
  request?: {
    method?: string | null
    path?: string | null
    headers: Record<string, unknown>
    query: Record<string, unknown>
    path_params?: Record<string, unknown>
    body: Record<string, unknown>
  } | Record<string, unknown> | null
  request_data?: Record<string, unknown> | null
  assertions: Array<{
    type: string
    path?: string | null
    operator?: string | null
    expression?: string | null
    expected?: unknown
    description?: string | null
    success_codes?: unknown[] | null
    success_expression?: string | null
  }>
  dsl_assertions: string[]
  coverage_tag: string[]
  risk_level: string
  data_dependency: Record<string, unknown>
  ai_metadata: Record<string, unknown>
  timestamps?: {
    created_at?: string | null
    updated_at?: string | null
  }
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

export interface EndpointPreviewItem {
  endpoint_key: string
  name: string
  group_name?: string | null
  summary?: string | null
  operation_id?: string | null
  method: string
  path: string
  description?: string | null
  headers?: Record<string, unknown> | null
  request_params?: Record<string, unknown> | null
  request_body_schema?: Record<string, unknown> | null
  response_schema?: Record<string, unknown> | null
  example_request?: Record<string, unknown> | null
  example_response?: unknown
  params_example_json?: Record<string, unknown>
  params_schema_json?: unknown
  params_edit_json?: Record<string, unknown>
  body_example_json?: unknown
  body_schema_json?: unknown
  body_edit_json?: unknown
  response_example_json?: unknown
  response_schema_json?: unknown
  response_edit_json?: unknown
  auth_required: boolean
  tags?: unknown[] | null
  status: string
  source: string
}

export interface DocumentPreviewRequest {
  name: string
  input_type: string
  input_content: string
  cookie?: string | null
  api_path_filter?: string | null
  method_filter?: string | null
  keyword_filter?: string | null
  group_filter?: string | null
  need_ai_parse: boolean
}

export interface DocumentPreviewResponse {
  detected_type: string
  resolved_spec_url?: string | null
  hash_hint?: string | null
  total_endpoint_count: number
  matched_endpoint_count: number
  endpoints: EndpointPreviewItem[]
  warnings: string[]
  errors: string[]
}

export interface DocumentImportUrlRequest extends DocumentPreviewRequest {
  save_mode: 'save_selected' | 'save_all'
  selected_endpoint_keys: string[]
  endpoints?: EndpointPreviewItem[]
}

export interface DocumentImportUrlResponse extends ApiDocumentImportResult {
  detected_type: string
  resolved_spec_url?: string | null
  hash_hint?: string | null
  total_endpoint_count: number
  matched_endpoint_count: number
  warnings: string[]
  errors: string[]
}

export interface AiGenerationResult {
  endpoint_id: number
  analysis_record_id: number
  case_count: number
  coverage_matrix?: Record<string, boolean> | null
  coverage_summary?: {
    required_dimensions?: string[]
    counts?: Record<string, number>
    missing_dimensions?: string[]
  } | null
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

export interface AssertionParseResult {
  dsl: string
  assertion: Record<string, unknown>
}

export interface AssertionToDslResult {
  dsl: string | string[]
}
