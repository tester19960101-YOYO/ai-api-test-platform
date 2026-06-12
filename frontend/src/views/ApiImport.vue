<template>
  <div class="page import-page">
    <ProjectRequired :project-id="projectId" />

    <section class="wizard-shell">
      <el-steps class="import-steps" :active="currentStep" align-center>
        <el-step title="选择导入方式" />
        <el-step title="解析与预览" />
        <el-step title="选择与编辑" />
        <el-step title="导入结果" />
      </el-steps>

      <div class="step-title">
        <div>
          <span class="step-index">{{ currentStep + 1 }}</span>
          <h1>{{ stepTitle }}</h1>
        </div>
        <span class="step-progress">第 {{ currentStep + 1 }} / 4 步</span>
      </div>
    </section>

    <section v-show="currentStep === 0" class="step-card">
      <el-form class="tool-form" label-width="120px">
        <el-form-item label="文档名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="输入类型">
          <el-segmented v-model="form.input_type" :options="inputTypeOptions" />
        </el-form-item>
        <el-form-item label="输入内容">
          <JsonTextarea
            v-model="form.input_content"
            :rows="inputRows"
            placeholder="支持在线文档 URL、doc.html 页面 URL、OpenAPI/Swagger JSON、curl 文本或接口路径"
          />
        </el-form-item>
        <el-form-item label="Cookie">
          <JsonTextarea v-model="form.cookie" :rows="3" placeholder="JSESSIONID=xxxx; SESSION=yyyy; token=zzzz" />
          <div class="form-tip">
            可选。用于访问需要登录态的 Knife4j / Swagger 文档。请从浏览器开发者工具中复制 Cookie 值，不需要填写“Cookie:”前缀。
          </div>
        </el-form-item>
        <el-form-item label="AI 辅助">
          <el-switch v-model="form.need_ai_parse" active-text="mock AI 辅助提示" inactive-text="仅结构化解析" />
        </el-form-item>
      </el-form>
    </section>

    <section v-show="currentStep === 1" class="step-card">
      <el-alert
        v-if="previewResult"
        class="summary"
        type="success"
        :closable="false"
        :title="`解析成功，共解析 ${previewResult.total_endpoint_count} 个接口，当前显示 ${previewResult.matched_endpoint_count} 个`"
      >
        <template #default>
          <div class="summary-grid">
            <span>文档类型：{{ previewResult.detected_type }}</span>
            <span>文档地址：{{ form.input_content }}</span>
            <span>真实文档：{{ previewResult.resolved_spec_url || '-' }}</span>
            <span>分组：{{ activeEndpoint?.group_name || form.group_filter || '-' }}</span>
            <span>匹配接口数：{{ previewResult.matched_endpoint_count }} / {{ previewResult.total_endpoint_count }}</span>
            <span>解析耗时：{{ parseCostText }}</span>
          </div>
        </template>
      </el-alert>

      <el-empty v-else description="还没有解析结果，请返回上一步输入内容并解析" />

      <div class="filter-bar">
        <el-form label-width="88px">
          <el-row :gutter="12">
            <el-col :span="8">
              <el-form-item label="接口路径">
                <el-input v-model="form.api_path_filter" placeholder="/saw/rainfallmonitor/add" clearable />
              </el-form-item>
            </el-col>
            <el-col :span="5">
              <el-form-item label="请求方法">
                <el-select v-model="form.method_filter" clearable placeholder="不限">
                  <el-option v-for="method in methods" :key="method" :label="method" :value="method" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="5">
              <el-form-item label="接口分组">
                <el-input v-model="form.group_filter" clearable placeholder="请输入分组" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="关键词">
                <el-input v-model="form.keyword_filter" placeholder="接口名称 / summary / 描述" clearable />
              </el-form-item>
            </el-col>
          </el-row>
          <div class="filter-actions">
            <el-button type="primary" :loading="loading" @click="preview">筛选</el-button>
            <el-button @click="resetFilters">重置</el-button>
            <el-button :loading="loading" @click="preview">重新解析</el-button>
          </div>
        </el-form>
      </div>

      <PreviewAlerts />

      <el-table v-if="editableEndpoints.length" :data="editableEndpoints" border>
        <el-table-column label="方法" width="92">
          <template #default="{ row }">
            <el-tag :type="methodTagType(row.method)">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="接口名称" min-width="180" />
        <el-table-column prop="path" label="接口路径" min-width="260" />
        <el-table-column prop="group_name" label="分组" min-width="140" />
        <el-table-column label="是否鉴权" width="100">
          <template #default="{ row }">
            <el-tag :type="row.auth_required ? 'primary' : 'info'">{{ row.auth_required ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="110" />
      </el-table>
    </section>

    <section v-show="currentStep === 2" class="step-card edit-step">
      <el-alert
        class="notice"
        type="warning"
        :closable="false"
        title="文档示例与 Schema 结构可能存在差异，请以实际接口定义和编辑后的请求数据为准。展开示例用于参考和快速请求，展开 Schema 用于查看完整字段结构。保存后系统将使用当前编辑后的 JSON 生成测试用例。"
      />
      <PreviewAlerts />

      <div v-if="previewResult && editableEndpoints.length" class="preview-layout">
        <aside class="endpoint-panel">
          <div class="panel-title">接口列表（{{ editableEndpoints.length }}）</div>
          <div class="endpoint-list">
            <div
              v-for="endpoint in editableEndpoints"
              :key="endpoint.endpoint_key"
              class="endpoint-item"
              :class="{ active: endpoint.endpoint_key === activeKey }"
              @click="selectEndpoint(endpoint.endpoint_key)"
            >
              <el-checkbox
                :model-value="isSelected(endpoint.endpoint_key)"
                @click.stop
                @change="toggleSelected(endpoint.endpoint_key, Boolean($event))"
              />
              <div class="endpoint-text">
                <div>
                  <el-tag size="small" :type="methodTagType(endpoint.method)">{{ endpoint.method }}</el-tag>
                  <strong>{{ endpoint.name }}</strong>
                </div>
                <span>{{ endpoint.path }}</span>
                <span v-if="endpoint.group_name">分组：{{ endpoint.group_name }}</span>
              </div>
            </div>
          </div>
          <div class="panel-actions">
            <el-checkbox :model-value="allSelected" @change="toggleAll(Boolean($event))">全选</el-checkbox>
            <span>已选择 {{ selectedKeys.length }} 个</span>
            <el-button size="small" @click="selectedKeys = []">清空</el-button>
          </div>
        </aside>

        <section class="endpoint-detail" v-if="activeEndpoint">
          <div class="detail-header">
            <div>
              <h2>{{ activeEndpoint.name }}</h2>
              <div class="endpoint-meta">
                <el-tag :type="methodTagType(activeEndpoint.method)">{{ activeEndpoint.method }}</el-tag>
                <span>{{ activeEndpoint.path }}</span>
              </div>
            </div>
            <el-button @click="openEdit(activeEndpoint)">编辑基本信息</el-button>
          </div>

          <div class="detail-fields">
            <span>分组：{{ activeEndpoint.group_name || '-' }}</span>
            <span>接口ID：{{ operationDisplay(activeEndpoint) }}</span>
            <span>操作ID：{{ activeEndpoint.operation_id || '-' }}</span>
            <span>是否鉴权：<el-switch v-model="activeEndpoint.auth_required" /></span>
          </div>

          <el-tabs v-model="activeTab">
            <el-tab-pane label="请求参数" name="params">
              <JsonPreviewEditor
                title="参数 JSON"
                content-type="application/json"
                :example-json="activeEndpoint.params_example_json"
                :schema-json="activeEndpoint.params_schema_json"
                v-model="activeEndpoint.params_edit_json"
                example-description="可执行参数 JSON，可用于请求"
                schema-description="参数 Schema，保留类型、required、description、example"
                @save="saveParamsJson"
              />
            </el-tab-pane>
            <el-tab-pane label="请求体" name="body">
              <JsonPreviewEditor
                title="Body JSON"
                content-type="application/json"
                :example-json="activeEndpoint.body_example_json"
                :schema-json="activeEndpoint.body_schema_json"
                v-model="activeEndpoint.body_edit_json"
                example-description="Body 示例 JSON，来自文档示例或 Schema 自动生成"
                schema-description="Body Schema，展开 $ref 后的完整结构"
                @save="saveBodyJson"
              />
            </el-tab-pane>
            <el-tab-pane label="响应示例" name="response">
              <JsonPreviewEditor
                title="响应 JSON"
                content-type="application/json"
                :example-json="activeEndpoint.response_example_json"
                :schema-json="activeEndpoint.response_schema_json"
                v-model="activeEndpoint.response_edit_json"
                example-description="响应示例 JSON，优先来自 response example / examples"
                schema-description="响应 Schema，展开 $ref 后的响应结构"
                @save="saveResponseJson"
              />
            </el-tab-pane>
            <el-tab-pane label="接口描述" name="description">
              <el-input v-model="activeEndpoint.description" type="textarea" :rows="8" />
            </el-tab-pane>
            <el-tab-pane label="其他信息" name="extra">
              <JsonTextarea :model-value="stringifyJson(activeEndpoint)" :rows="16" />
            </el-tab-pane>
          </el-tabs>
        </section>
      </div>

      <el-empty v-else description="没有可选择和编辑的接口" />
    </section>

    <section v-show="currentStep === 3" class="step-card result-step">
      <el-result
        icon="success"
        title="导入完成"
        :sub-title="`已保存 ${importResult?.endpoint_count || 0} 个接口资产，可继续查看接口列表或生成 mock AI 测试用例。`"
      />
      <el-descriptions v-if="importResult" :column="2" border>
        <el-descriptions-item label="文档类型">{{ importResult.detected_type }}</el-descriptions-item>
        <el-descriptions-item label="真实文档">{{ importResult.resolved_spec_url || '-' }}</el-descriptions-item>
        <el-descriptions-item label="匹配接口">{{ importResult.matched_endpoint_count }}</el-descriptions-item>
        <el-descriptions-item label="总接口数">{{ importResult.total_endpoint_count }}</el-descriptions-item>
      </el-descriptions>
      <el-alert
        class="notice"
        type="info"
        :closable="false"
        title="导入后不会自动生成测试用例，请在 AI 用例生成页选择接口后手动触发 mock AI 用例生成。"
      />
    </section>

    <div class="footer-actions">
      <el-button v-if="currentStep > 0" @click="goPrev">上一步</el-button>
      <el-button v-if="currentStep === 0" @click="clearPreview">清空</el-button>
      <el-button v-if="currentStep === 1" @click="resetFilters">重置筛选</el-button>
      <el-button v-if="currentStep === 2" :disabled="!selectedEndpoints.length" :loading="saving" @click="saveSelected">
        保存选中接口
      </el-button>
      <el-button v-if="currentStep === 2" :disabled="!editableEndpoints.length" :loading="saving" @click="saveAll">
        保存全部接口
      </el-button>
      <el-button
        v-if="currentStep < 3"
        type="primary"
        :disabled="nextDisabled"
        :loading="loading || saving"
        @click="goNext"
      >
        {{ nextButtonText }}
      </el-button>
      <el-button v-else type="primary" @click="finishImport">完成</el-button>
    </div>

    <el-dialog v-model="editVisible" title="编辑接口基础信息" width="640px">
      <el-form v-if="editing" label-width="110px">
        <el-form-item label="接口名称"><el-input v-model="editing.name" /></el-form-item>
        <el-form-item label="请求方法">
          <el-select v-model="editing.method">
            <el-option v-for="method in methods" :key="method" :label="method" :value="method" />
          </el-select>
        </el-form-item>
        <el-form-item label="接口路径"><el-input v-model="editing.path" /></el-form-item>
        <el-form-item label="接口分组"><el-input v-model="editing.group_name" /></el-form-item>
        <el-form-item label="是否鉴权"><el-switch v-model="editing.auth_required" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="editing.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="applyBasicEdit">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ElAlert, ElMessage } from 'element-plus'
import { computed, defineComponent, h, nextTick, reactive, ref } from 'vue'

import { documentApi } from '@/api'
import JsonPreviewEditor from '@/components/JsonPreviewEditor.vue'
import JsonTextarea from '@/components/JsonTextarea.vue'
import ProjectRequired from '@/components/ProjectRequired.vue'
import { useProjectStore } from '@/stores/project'
import type {
  DocumentImportUrlResponse,
  DocumentPreviewRequest,
  DocumentPreviewResponse,
  EndpointPreviewItem
} from '@/types'
import { stringifyJson } from '@/utils/json'

type JsonMode = 'example' | 'schema'
type EndpointPreviewDraft = EndpointPreviewItem & {
  params_example_json: Record<string, unknown>
  params_schema_json: unknown
  params_edit_json: Record<string, unknown>
  body_example_json: unknown
  body_schema_json: unknown
  body_edit_json: unknown
  response_example_json: unknown
  response_schema_json: unknown
  response_edit_json: unknown
}

const projectStore = useProjectStore()
const projectId = computed(() => projectStore.currentProjectId)
const methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
const inputTypeOptions = [
  { label: '自动识别', value: 'auto' },
  { label: '在线 URL', value: 'online_url' },
  { label: '单接口页面', value: 'single_api_doc_url' },
  { label: 'JSON 内容', value: 'openapi_json_text' },
  { label: 'curl', value: 'curl_text' },
  { label: '接口路径', value: 'api_path' }
]

const loading = ref(false)
const saving = ref(false)
const currentStep = ref(0)
const previewResult = ref<DocumentPreviewResponse | null>(null)
const importResult = ref<DocumentImportUrlResponse | null>(null)
const editableEndpoints = ref<EndpointPreviewDraft[]>([])
const selectedKeys = ref<string[]>([])
const activeKey = ref('')
const activeTab = ref('params')
const parseCostMs = ref<number | null>(null)
const editVisible = ref(false)
const editing = ref<EndpointPreviewItem | null>(null)
const editingKey = ref('')
const jsonModes = reactive<Record<string, JsonMode>>({
  params: 'example',
  body: 'example',
  response: 'example'
})

const form = reactive<DocumentPreviewRequest & { cookie: string }>({
  name: '接口文档导入',
  input_type: 'auto',
  input_content: 'http://127.0.0.1:8000/openapi.json',
  cookie: '',
  api_path_filter: '',
  method_filter: '',
  keyword_filter: '',
  group_filter: '',
  need_ai_parse: true
})

const stepTitle = computed(() => ['选择导入方式', '解析与预览', '选择与编辑', '导入结果'][currentStep.value])
const inputRows = computed(() => (form.input_type === 'openapi_json_text' ? 12 : 6))
const parseCostText = computed(() => (parseCostMs.value == null ? '-' : `${(parseCostMs.value / 1000).toFixed(2)}s`))
const activeEndpoint = computed(() => editableEndpoints.value.find((item) => item.endpoint_key === activeKey.value) || null)
const selectedEndpoints = computed(() => editableEndpoints.value.filter((item) => selectedKeys.value.includes(item.endpoint_key)))
const allSelected = computed(() => editableEndpoints.value.length > 0 && selectedKeys.value.length === editableEndpoints.value.length)
const nextButtonText = computed(() => {
  if (currentStep.value === 0) return '下一步：解析与预览'
  if (currentStep.value === 1) return '下一步：选择与编辑'
  return `保存并下一步（${selectedEndpoints.value.length || editableEndpoints.value.length}）`
})
const nextDisabled = computed(() => {
  if (!projectId.value) return true
  if (currentStep.value === 0) return !form.input_content.trim()
  if (currentStep.value === 1) return !editableEndpoints.value.length
  if (currentStep.value === 2) return !editableEndpoints.value.length
  return false
})

const PreviewAlerts = defineComponent({
  name: 'PreviewAlerts',
  setup() {
    return () => h('div', [
      ...(previewResult.value?.warnings || []).map((warning) => h('div', { class: 'alert-wrap', key: warning }, [
        h(ElAlert, { type: 'warning', closable: false, title: warning })
      ])),
      ...(previewResult.value?.errors || []).map((error) => h('div', { class: 'alert-wrap', key: error }, [
        h(ElAlert, { type: 'error', closable: false, title: error })
      ]))
    ])
  }
})

function buildPayload(): DocumentPreviewRequest {
  return {
    ...form,
    cookie: form.cookie?.trim() || null,
    api_path_filter: form.api_path_filter || null,
    method_filter: form.method_filter || null,
    keyword_filter: form.keyword_filter || null,
    group_filter: form.group_filter || null
  }
}

async function preview() {
  if (!projectId.value) return
  loading.value = true
  currentStep.value = 1
  importResult.value = null
  const startedAt = performance.now()
  try {
    previewResult.value = await documentApi.previewInput(projectId.value, buildPayload())
    parseCostMs.value = Math.round(performance.now() - startedAt)
    editableEndpoints.value = previewResult.value.endpoints.map(mapEndpointPreview)
    selectedKeys.value = editableEndpoints.value.map((item) => item.endpoint_key)
    activeKey.value = editableEndpoints.value[0]?.endpoint_key || ''
    await nextTick()
    ElMessage.success(`预览完成，匹配 ${previewResult.value.matched_endpoint_count} 个接口`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '预览失败')
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  form.api_path_filter = ''
  form.method_filter = ''
  form.keyword_filter = ''
  form.group_filter = ''
}

function goPrev() {
  if (currentStep.value > 0) {
    currentStep.value -= 1
  }
}

async function goNext() {
  if (currentStep.value === 0) {
    await preview()
    return
  }
  if (currentStep.value === 1) {
    if (!editableEndpoints.value.length) {
      ElMessage.warning('当前没有可编辑接口，请调整输入或筛选条件后重新解析')
      return
    }
    currentStep.value = 2
    return
  }
  if (currentStep.value === 2) {
    await save('save_selected', selectedEndpoints.value.length ? selectedEndpoints.value : editableEndpoints.value)
  }
}

async function saveSelected() {
  await save('save_selected', selectedEndpoints.value)
}

async function saveAll() {
  await save('save_all', editableEndpoints.value)
}

async function save(saveMode: 'save_selected' | 'save_all', rows: EndpointPreviewDraft[]) {
  if (!projectId.value || !rows.length) return
  saving.value = true
  try {
    const result = await documentApi.importInput(projectId.value, {
      ...buildPayload(),
      save_mode: saveMode,
      selected_endpoint_keys: rows.map((row) => row.endpoint_key),
      endpoints: rows.map(toEndpointPreviewItem)
    })
    importResult.value = result
    currentStep.value = 3
    ElMessage.success(`保存成功，写入 ${result.endpoint_count} 个接口资产`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存失败')
  } finally {
    saving.value = false
  }
}

function clearPreview() {
  previewResult.value = null
  importResult.value = null
  editableEndpoints.value = []
  selectedKeys.value = []
  activeKey.value = ''
  currentStep.value = 0
}

function finishImport() {
  clearPreview()
}

function selectEndpoint(key: string) {
  activeKey.value = key
}

function isSelected(key: string) {
  return selectedKeys.value.includes(key)
}

function toggleSelected(key: string, checked: boolean) {
  if (checked && !selectedKeys.value.includes(key)) {
    selectedKeys.value = [...selectedKeys.value, key]
  }
  if (!checked) {
    selectedKeys.value = selectedKeys.value.filter((item) => item !== key)
  }
}

function toggleAll(checked: boolean) {
  selectedKeys.value = checked ? editableEndpoints.value.map((item) => item.endpoint_key) : []
}

function openEdit(row: EndpointPreviewDraft) {
  editingKey.value = row.endpoint_key
  editing.value = { ...row }
  editVisible.value = true
}

function applyBasicEdit() {
  if (!editing.value) return
  editing.value.method = editing.value.method.toUpperCase()
  editing.value.endpoint_key = `${editing.value.method} ${editing.value.path}`
  const index = editableEndpoints.value.findIndex((item) => item.endpoint_key === editingKey.value)
  if (index >= 0) {
    editableEndpoints.value[index] = mapEndpointPreview(editing.value)
    activeKey.value = editing.value.endpoint_key
    selectedKeys.value = selectedKeys.value.map((key) => (key === editingKey.value ? editing.value!.endpoint_key : key))
  }
  editVisible.value = false
}

function operationDisplay(endpoint: EndpointPreviewItem) {
  return endpoint.operation_id || endpoint.endpoint_key.replace(/\s+/g, '_')
}

function methodTagType(method: string) {
  const upper = method.toUpperCase()
  if (upper === 'GET') return 'success'
  if (upper === 'POST') return 'warning'
  if (upper === 'PUT') return 'primary'
  if (upper === 'DELETE') return 'danger'
  return 'info'
}

function parameterExample(endpoint: EndpointPreviewItem) {
  const request = endpoint.example_request || {}
  return {
    query: request.query || {},
    path: request.path_params || {},
    header: request.headers || {},
    cookie: request.cookies || {}
  }
}

function bodyExample(endpoint: EndpointPreviewItem) {
  if (endpoint.example_request && typeof endpoint.example_request === 'object' && 'body' in endpoint.example_request) {
    return endpoint.example_request.body ?? {}
  }
  return endpoint.request_body_schema?.['x-example'] || {}
}

function saveParamsJson(value: unknown, mode: JsonMode) {
  const endpoint = activeEndpoint.value
  if (!endpoint) return
  if (mode === 'schema') {
    endpoint.params_schema_json = value
    endpoint.request_params = value as Record<string, unknown>
    return
  }
  const example = normalizeParamExample(value)
  endpoint.params_edit_json = example
  endpoint.params_example_json = example
  endpoint.example_request = {
    ...(endpoint.example_request || {}),
    headers: example.header,
    query: example.query,
    path_params: example.path,
    cookies: example.cookie
  }
  endpoint.request_params = applyValuesToParamSchema(endpoint.request_params, example)
  endpoint.headers = endpoint.request_params?.header as Record<string, unknown> | null
}

function saveBodyJson(value: unknown, mode: JsonMode) {
  const endpoint = activeEndpoint.value
  if (!endpoint) return
  if (mode === 'schema') {
    endpoint.body_schema_json = value
    endpoint.request_body_schema = value as Record<string, unknown>
    return
  }
  endpoint.body_edit_json = value
  endpoint.body_example_json = value
  endpoint.example_request = { ...(endpoint.example_request || {}), body: value }
  endpoint.request_body_schema = { ...(endpoint.request_body_schema || {}), 'x-example': value }
}

function saveResponseJson(value: unknown, mode: JsonMode) {
  const endpoint = activeEndpoint.value
  if (!endpoint) return
  if (mode === 'schema') {
    endpoint.response_schema_json = value
    endpoint.response_schema = value as Record<string, unknown>
    return
  }
  endpoint.response_edit_json = value
  endpoint.response_example_json = value
  endpoint.example_response = value
  endpoint.response_schema = { ...(endpoint.response_schema || {}), 'x-example': value }
}

function normalizeParamExample(value: unknown) {
  const data = value && typeof value === 'object' ? value as Record<string, Record<string, unknown>> : {}
  return {
    query: data.query || {},
    path: data.path || {},
    header: data.header || {},
    cookie: data.cookie || {}
  }
}

function applyValuesToParamSchema(schema: unknown, example: ReturnType<typeof normalizeParamExample>) {
  const next = schema && typeof schema === 'object' ? JSON.parse(JSON.stringify(schema)) : { query: {}, path: {}, header: {}, cookie: {} }
  for (const location of ['query', 'path', 'header', 'cookie'] as const) {
    next[location] = next[location] || {}
    for (const [key, value] of Object.entries(example[location])) {
      next[location][key] = {
        ...(next[location][key] || { name: key, in: location }),
        value
      }
    }
  }
  return next
}

function mapEndpointPreview(item: EndpointPreviewItem): EndpointPreviewDraft {
  const paramsExample = parameterExample(item)
  const bodyValue = bodyExample(item)
  return {
    ...item,
    params_example_json: paramsExample,
    params_schema_json: item.request_params || { query: {}, path: {}, header: {}, cookie: {} },
    params_edit_json: paramsExample,
    body_example_json: bodyValue,
    body_schema_json: item.request_body_schema || {},
    body_edit_json: bodyValue,
    response_example_json: item.example_response || item.response_schema?.['x-example'] || {},
    response_schema_json: item.response_schema || {},
    response_edit_json: item.example_response || item.response_schema?.['x-example'] || {}
  }
}

function toEndpointPreviewItem(item: EndpointPreviewDraft): EndpointPreviewItem {
  return {
    endpoint_key: item.endpoint_key,
    name: item.name,
    group_name: item.group_name,
    summary: item.summary,
    operation_id: item.operation_id,
    method: item.method,
    path: item.path,
    description: item.description,
    headers: item.headers,
    request_params: item.request_params,
    request_body_schema: item.request_body_schema,
    response_schema: item.response_schema,
    example_request: item.example_request,
    example_response: item.example_response,
    auth_required: item.auth_required,
    tags: item.tags,
    status: item.status,
    source: item.source
  }
}
</script>

<style scoped>
.import-page {
  background: #f5f7fb;
  margin: -20px;
  padding-bottom: 76px;
  padding-left: 20px;
  padding-right: 20px;
  padding-top: 20px;
}

.wizard-shell,
.step-card {
  background: #fff;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  margin-bottom: 14px;
}

.wizard-shell {
  padding: 18px 20px 14px;
}

.import-steps {
  margin-bottom: 18px;
}

.step-title {
  align-items: center;
  border-top: 1px solid var(--el-border-color-lighter);
  display: flex;
  justify-content: space-between;
  padding-top: 14px;
}

.step-title > div {
  align-items: center;
  display: flex;
  gap: 10px;
}

.step-title h1 {
  font-size: 18px;
  line-height: 1;
  margin: 0;
}

.step-index {
  align-items: center;
  background: var(--el-color-primary);
  border-radius: 50%;
  color: #fff;
  display: inline-flex;
  font-weight: 700;
  height: 24px;
  justify-content: center;
  width: 24px;
}

.step-progress {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.step-card {
  padding: 18px;
}

.edit-step {
  background: #f5f7fb;
  border: 0;
  padding: 0;
}

.tool-form {
  max-width: 1120px;
}

.form-tip {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  line-height: 1.6;
  margin-top: 6px;
}

.summary,
.notice,
.alert-wrap {
  margin-bottom: 10px;
}

.summary-grid {
  display: grid;
  gap: 8px 20px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.filter-bar {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  margin-bottom: 12px;
  padding: 14px 14px 0;
}

.filter-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-bottom: 14px;
}

.preview-layout {
  display: grid;
  gap: 16px;
  grid-template-columns: 300px minmax(0, 1fr);
}

.endpoint-panel,
.endpoint-detail {
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  background: #fff;
}

.panel-title {
  border-bottom: 1px solid var(--el-border-color-light);
  font-weight: 700;
  padding: 14px 16px;
}

.endpoint-list {
  max-height: 560px;
  overflow: auto;
  padding: 8px;
}

.endpoint-item {
  align-items: flex-start;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  gap: 10px;
  padding: 12px;
}

.endpoint-item.active {
  background: #edf5ff;
}

.endpoint-text {
  display: grid;
  gap: 6px;
}

.endpoint-text > div {
  align-items: center;
  display: flex;
  gap: 8px;
}

.endpoint-text span {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.panel-actions {
  align-items: center;
  border-top: 1px solid var(--el-border-color-light);
  display: flex;
  gap: 12px;
  justify-content: space-between;
  padding: 12px;
}

.endpoint-detail {
  padding: 16px;
}

.detail-header,
.json-toolbar,
.footer-actions {
  align-items: center;
  display: flex;
  justify-content: space-between;
}

.detail-header h2 {
  font-size: 20px;
  margin: 0 0 8px;
}

.endpoint-meta {
  align-items: center;
  display: flex;
  gap: 12px;
}

.detail-fields {
  border-bottom: 1px solid var(--el-border-color-light);
  border-top: 1px solid var(--el-border-color-light);
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin: 16px 0;
  padding: 12px 0;
}

.result-step {
  display: grid;
  gap: 14px;
}

.footer-actions {
  background: #fff;
  border-top: 1px solid var(--el-border-color-light);
  bottom: 0;
  gap: 12px;
  justify-content: flex-end;
  left: 0;
  padding: 14px 26px;
  position: sticky;
  z-index: 3;
}

@media (max-width: 1200px) {
  .preview-layout {
    grid-template-columns: 280px minmax(0, 1fr);
  }

  .summary-grid,
  .detail-fields {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
