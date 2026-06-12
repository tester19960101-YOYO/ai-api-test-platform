import http, { request } from './http'

import type {
  AiGenerationResult,
  ApiDocumentImportResult,
  ApiEndpoint,
  DocumentImportUrlRequest,
  DocumentImportUrlResponse,
  DocumentPreviewRequest,
  DocumentPreviewResponse,
  Environment,
  ExecutionRunResponse,
  Project,
  TestCase
} from '@/types'

export const healthApi = {
  check: () => request<{ status: string }>(http.get('/health'))
}

export const projectApi = {
  list: () => request<Project[]>(http.get('/projects')),
  create: (data: Partial<Project>) => request<Project>(http.post('/projects', data)),
  update: (id: number, data: Partial<Project>) => request<Project>(http.put(`/projects/${id}`, data)),
  remove: (id: number) => request<Project>(http.delete(`/projects/${id}`))
}

export const environmentApi = {
  list: (projectId: number) => request<Environment[]>(http.get(`/projects/${projectId}/environments`)),
  create: (projectId: number, data: Partial<Environment>) =>
    request<Environment>(http.post(`/projects/${projectId}/environments`, data)),
  update: (id: number, data: Partial<Environment>) => request<Environment>(http.put(`/environments/${id}`, data)),
  remove: (id: number) => request<Environment>(http.delete(`/environments/${id}`))
}

export const documentApi = {
  importOpenApi: (projectId: number, data: { name: string; content?: unknown; url?: string }) =>
    request<ApiDocumentImportResult>(http.post(`/projects/${projectId}/api-documents/openapi`, data)),
  importCurl: (projectId: number, data: { name: string; curl_text: string }) =>
    request<ApiDocumentImportResult>(http.post(`/projects/${projectId}/api-documents/curl`, data)),
  previewInput: (projectId: number, data: DocumentPreviewRequest) =>
    request<DocumentPreviewResponse>(http.post(`/projects/${projectId}/documents/preview-url`, data)),
  importInput: (projectId: number, data: DocumentImportUrlRequest) =>
    request<DocumentImportUrlResponse>(http.post(`/projects/${projectId}/documents/import-url`, data))
}

export const endpointApi = {
  list: (projectId: number) => request<ApiEndpoint[]>(http.get(`/projects/${projectId}/api-endpoints`)),
  detail: (id: number) => request<ApiEndpoint>(http.get(`/api-endpoints/${id}`)),
  update: (id: number, data: Partial<ApiEndpoint>) => request<ApiEndpoint>(http.put(`/api-endpoints/${id}`, data)),
  updateStatus: (id: number, status: string) =>
    request<ApiEndpoint>(http.patch(`/api-endpoints/${id}/status`, { status }))
}

export const testCaseApi = {
  list: (projectId: number) => request<TestCase[]>(http.get(`/projects/${projectId}/test-cases`)),
  create: (data: Partial<TestCase>) => request<TestCase>(http.post('/test-cases', data)),
  detail: (id: number) => request<TestCase>(http.get(`/test-cases/${id}`)),
  update: (id: number, data: Partial<TestCase>) => request<TestCase>(http.put(`/test-cases/${id}`, data)),
  remove: (id: number) => request<TestCase>(http.delete(`/test-cases/${id}`))
}

export const aiApi = {
  generateCases: (endpointId: number) =>
    request<AiGenerationResult>(http.post(`/endpoints/${endpointId}/testcases/generate`))
}

export const executionApi = {
  run: (data: { project_id: number; environment_id: number; case_ids?: number[]; timeout?: number }) =>
    request<ExecutionRunResponse>(http.post('/executions/run', data))
}
