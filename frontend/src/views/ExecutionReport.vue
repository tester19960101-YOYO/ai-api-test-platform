<template>
  <div class="page report-page">
    <ProjectRequired :project-id="projectId" />

    <el-form class="report-toolbar" inline>
      <el-form-item label="环境">
        <el-select v-model="form.environment_id" filterable placeholder="选择环境" style="width: 300px">
          <el-option
            v-for="environment in environments"
            :key="environment.id"
            :label="`${environment.name} - ${environment.base_url}`"
            :value="environment.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="测试用例">
        <el-select
          v-model="form.case_ids"
          multiple
          filterable
          clearable
          collapse-tags
          collapse-tags-tooltip
          placeholder="可多选测试用例"
          style="width: 420px"
        >
          <el-option v-for="item in cases" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="超时">
        <el-input-number v-model="form.timeout" :min="1" :max="120" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :disabled="!canRun" :loading="running" @click="runExecution">执行测试</el-button>
      </el-form-item>
    </el-form>

    <el-row v-if="execution" class="summary-row" :gutter="12">
      <el-col :span="6"><el-statistic title="总数" :value="execution.task.total_cases" /></el-col>
      <el-col :span="6"><el-statistic title="通过" :value="execution.task.passed_cases" /></el-col>
      <el-col :span="6"><el-statistic title="失败" :value="execution.task.failed_cases" /></el-col>
      <el-col :span="6"><el-statistic title="跳过" :value="0" /></el-col>
    </el-row>

    <el-descriptions v-if="execution" class="task-descriptions" border :column="1">
      <el-descriptions-item label="任务状态">
        <el-tag :type="execution.task.status === 'passed' ? 'success' : 'danger'">{{ execution.task.status }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="报告路径">
        {{ execution.report_path }}
      </el-descriptions-item>
      <el-descriptions-item label="日志路径">
        {{ execution.log_path }}
      </el-descriptions-item>
      <el-descriptions-item label="生成工程">
        {{ execution.generated_project_path }}
      </el-descriptions-item>
    </el-descriptions>

    <el-table v-if="execution" class="result-table" :data="execution.results" border row-key="id">
      <el-table-column type="expand" width="48">
        <template #default="{ row }">
          <div class="result-expand">
            <div class="detail-card">
              <div class="detail-card-header">
                <strong>请求参数 JSON</strong>
                <el-button size="small" @click="copyText(formatJson(row.request_data), '请求参数')">复制</el-button>
              </div>
              <pre class="code-block">{{ formatJson(row.request_data) }}</pre>
            </div>

            <div class="detail-card">
              <div class="detail-card-header">
                <strong>响应体 JSON</strong>
                <el-button size="small" @click="copyText(formatJson(row.response_data), '响应体')">复制</el-button>
              </div>
              <pre class="code-block">{{ formatJson(row.response_data) }}</pre>
            </div>

            <div class="detail-card detail-card-wide">
              <div class="detail-card-header">
                <strong>curl 命令</strong>
                <el-button size="small" @click="copyText(buildCurl(row), 'curl')">复制</el-button>
              </div>
              <pre class="code-block curl-block">{{ buildCurl(row) }}</pre>
            </div>

            <div class="detail-card detail-card-wide">
              <div class="detail-card-header">
                <strong>断言结果</strong>
                <el-button size="small" @click="copyText(formatJson(row.assertion_result), '断言结果')">复制</el-button>
              </div>
              <pre class="code-block">{{ formatJson(row.assertion_result) }}</pre>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="test_case_id" label="用例 ID" width="100" />
      <el-table-column prop="status" label="状态" width="110" />
      <el-table-column prop="status_code" label="状态码" width="100" />
      <el-table-column prop="response_time_ms" label="耗时 ms" width="120" />
      <el-table-column prop="error_message" label="错误信息" min-width="260" show-overflow-tooltip />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'

import { environmentApi, executionApi, testCaseApi } from '@/api'
import ProjectRequired from '@/components/ProjectRequired.vue'
import { useProjectStore } from '@/stores/project'
import type { Environment, ExecutionResult, ExecutionRunResponse, TestCase } from '@/types'

const projectStore = useProjectStore()
const projectId = computed(() => projectStore.currentProjectId)
const environments = ref<Environment[]>([])
const cases = ref<TestCase[]>([])
const running = ref(false)
const execution = ref<ExecutionRunResponse | null>(null)
const form = reactive({
  environment_id: null as number | null,
  case_ids: [] as number[],
  timeout: 10
})
const canRun = computed(() => Boolean(projectId.value && form.environment_id && form.case_ids.length))

async function loadOptions() {
  if (!projectId.value) return
  environments.value = await environmentApi.list(projectId.value)
  cases.value = await testCaseApi.list(projectId.value)
  form.environment_id = environments.value.find((item) => item.is_default)?.id || environments.value[0]?.id || null
}

async function runExecution() {
  if (!form.environment_id) return
  running.value = true
  try {
    execution.value = await executionApi.run({
      project_id: projectId.value,
      environment_id: form.environment_id,
      case_ids: form.case_ids,
      timeout: form.timeout
    })
    ElMessage.success('执行完成')
  } finally {
    running.value = false
  }
}

function formatJson(value: unknown) {
  if (value === null || value === undefined) return '{}'
  try {
    return JSON.stringify(value, null, 2)
  } catch {
    return String(value)
  }
}

function buildCurl(row: ExecutionResult) {
  const request = row.request_data || {}
  if (typeof request.curl === 'string' && request.curl) {
    return request.curl
  }
  const environment = environments.value.find((item) => item.id === form.environment_id)
  const baseUrl = (environment?.base_url || '').replace(/\/+$/, '')
  const path = String(request.path || '/')
  const query = request.query && typeof request.query === 'object' ? request.query as Record<string, unknown> : {}
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined && value !== null && value !== '') {
      search.append(key, String(value))
    }
  }
  const url = `${baseUrl}${path.startsWith('/') ? path : `/${path}`}${search.size ? `?${search.toString()}` : ''}`
  const method = String(request.method || 'GET').toUpperCase()
  const parts = [`curl -X ${method} ${shellQuote(url)}`]
  const headers = request.headers && typeof request.headers === 'object' ? request.headers as Record<string, unknown> : {}

  for (const [key, value] of Object.entries(headers)) {
    parts.push(`-H ${shellQuote(`${key}: ${String(value)}`)}`)
  }
  if (request.body !== undefined && request.body !== null) {
    parts.push("-H 'Content-Type: application/json'")
    parts.push(`--data ${shellQuote(JSON.stringify(request.body))}`)
  }
  return parts.join(' \\\n  ')
}

function shellQuote(value: string) {
  return `'${value.replace(/'/g, "'\\''")}'`
}

async function copyText(text: string, label: string) {
  await navigator.clipboard?.writeText(text)
  ElMessage.success(`${label}已复制`)
}

onMounted(loadOptions)
</script>

<style scoped>
.report-page {
  background: #f5f7fb;
  margin: -20px;
  min-height: calc(100vh - 40px);
  padding: 20px;
}

.report-toolbar,
.summary-row,
.task-descriptions,
.result-table {
  margin-bottom: 16px;
}

.report-toolbar {
  background: #fff;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  padding: 16px 16px 0;
}

.summary-row {
  background: #fff;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  padding: 14px 0;
}

.result-expand {
  background: #f8fafc;
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  padding: 16px;
}

.detail-card {
  background: #fff;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  min-width: 0;
}

.detail-card-wide {
  grid-column: 1 / -1;
}

.detail-card-header {
  align-items: center;
  border-bottom: 1px solid var(--el-border-color-lighter);
  display: flex;
  justify-content: space-between;
  padding: 10px 12px;
}

.code-block {
  color: #1f2937;
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
  max-height: 320px;
  overflow: auto;
  padding: 12px;
  white-space: pre-wrap;
  word-break: break-word;
}

.curl-block {
  color: #0f766e;
}

@media (max-width: 1100px) {
  .result-expand {
    grid-template-columns: 1fr;
  }

  .detail-card-wide {
    grid-column: auto;
  }
}
</style>
