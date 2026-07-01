<template>
  <div class="page">
    <ProjectRequired :project-id="projectId" />
    <el-alert
      title="当前使用真实大模型生成测试用例；如未配置 AI_API_KEY，后端会返回明确配置错误，不会自动 fallback 到 mock"
      type="info"
      :closable="false"
      show-icon
    />
    <div class="page-toolbar">
      <div class="toolbar-left">
        <el-select v-model="selectedEndpointId" placeholder="选择接口" filterable style="width: 360px">
          <el-option
            v-for="endpoint in endpoints"
            :key="endpoint.id"
            :label="`${endpoint.method} ${endpoint.path}`"
            :value="endpoint.id"
          />
        </el-select>
        <el-button type="primary" :disabled="!selectedEndpointId" :loading="generating" @click="generateCases">
          生成 AI 用例
        </el-button>
      </div>
    </div>

    <el-card v-if="coverageRows.length" class="coverage-card" shadow="never">
      <template #header>
        <div class="coverage-header">
          <span>测试覆盖率</span>
          <el-tag :type="coverageComplete ? 'success' : 'danger'">
            {{ coverageComplete ? '覆盖完整' : '存在缺失' }}
          </el-tag>
        </div>
      </template>
      <el-row :gutter="12">
        <el-col v-for="item in coverageRows" :key="item.key" :span="6">
          <div class="coverage-item" :class="{ missing: item.missing }">
            <div class="coverage-name">{{ item.label }}</div>
            <div class="coverage-count">{{ item.count }} 条</div>
            <el-tag size="small" :type="item.missing ? 'danger' : 'success'">
              {{ item.missing ? '缺失' : '已覆盖' }}
            </el-tag>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-table :data="generatedCases" border>
      <el-table-column prop="name" label="用例名称" min-width="220" />
      <el-table-column label="类型" width="130">
        <template #default="{ row }">{{ typeLabel(row) }}</template>
      </el-table-column>
      <el-table-column label="优先级" width="100">
        <template #default="{ row }">{{ priorityLabel(row) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">{{ statusLabel(row.status) }}</template>
      </el-table-column>
      <el-table-column label="接口路径" min-width="220">
        <template #default="{ row }">{{ endpointPath(row) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="disableCase(row)">禁用</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-drawer v-model="drawerVisible" title="编辑测试用例" size="58%">
      <CaseEditor v-if="editingCase" :case-item="editingCase" @saved="afterCaseSaved" />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { aiApi, endpointApi, testCaseApi } from '@/api'
import ProjectRequired from '@/components/ProjectRequired.vue'
import CaseEditor from '@/views/parts/CaseEditor.vue'
import { useProjectStore } from '@/stores/project'
import type { AiGenerationResult, ApiEndpoint, TestCase } from '@/types'

const route = useRoute()
const projectStore = useProjectStore()
const projectId = computed(() => projectStore.currentProjectId)
const endpoints = ref<ApiEndpoint[]>([])
const selectedEndpointId = ref<number | null>(Number(route.query.endpointId) || null)
const generatedCases = ref<TestCase[]>([])
const aiGenerationResult = ref<AiGenerationResult | null>(null)
const generating = ref(false)
const drawerVisible = ref(false)
const editingCase = ref<TestCase | null>(null)

const coverageLabels: Record<string, string> = {
  functional: '功能正确性',
  validation: '参数校验',
  boundary: '边界值',
  negative: '异常场景',
  security: '安全测试',
  business: '业务语义',
  dependency: '数据依赖'
}

const statusLabels: Record<string, string> = {
  generated: '已生成',
  edited: '已编辑',
  disabled: '已禁用',
  passed: '通过',
  failed: '失败'
}

async function loadEndpoints() {
  if (!projectId.value) return
  endpoints.value = await endpointApi.list(projectId.value)
}

async function generateCases() {
  if (!selectedEndpointId.value) return
  generating.value = true
  try {
    const result = await aiApi.generateCases(selectedEndpointId.value)
    aiGenerationResult.value = result
    generatedCases.value = result.test_cases
    ElMessage.success(`已生成 ${result.case_count} 条 AI 用例`)
  } finally {
    generating.value = false
  }
}

const coverageRows = computed(() => {
  const matrix = aiGenerationResult.value?.coverage_matrix || {}
  const counts = aiGenerationResult.value?.coverage_summary?.counts || {}
  const missing = new Set(aiGenerationResult.value?.coverage_summary?.missing_dimensions || [])
  return Object.keys(coverageLabels)
    .filter((key) => matrix[key])
    .map((key) => ({
      key,
      label: coverageLabels[key],
      count: Number(counts[key] || 0),
      missing: missing.has(key) || Number(counts[key] || 0) <= 0
    }))
})

const coverageComplete = computed(
  () => coverageRows.value.length > 0 && coverageRows.value.every((item) => !item.missing)
)

function openEdit(testCase: TestCase) {
  editingCase.value = testCase
  drawerVisible.value = true
}

async function disableCase(testCase: TestCase) {
  await testCaseApi.remove(testCase.id)
  ElMessage.success('已禁用')
  generatedCases.value = generatedCases.value.map((item) =>
    item.id === testCase.id ? { ...item, status: 'disabled' } : item
  )
}

function afterCaseSaved(testCase: TestCase) {
  generatedCases.value = generatedCases.value.map((item) => (item.id === testCase.id ? testCase : item))
  drawerVisible.value = false
}

function typeLabel(testCase: TestCase) {
  const type = normalizeType(testCase)
  return coverageLabels[type] || type || '-'
}

function statusLabel(status: string) {
  return statusLabels[status] || status || '-'
}

function priorityLabel(testCase: TestCase) {
  const raw = String(testCase.priority || '')
  const map: Record<string, string> = { high: 'P0', medium: 'P1', low: 'P2' }
  return map[raw.toLowerCase()] || raw || '-'
}

function normalizeType(testCase: TestCase) {
  const legacy = testCase as unknown as { variables?: Record<string, unknown> }
  const raw = String(testCase.type || legacy.variables?.coverage_dimension || legacy.variables?.case_type || '')
  const map: Record<string, string> = {
    normal: 'functional',
    error: 'negative',
    exception: 'negative',
    auth: 'security'
  }
  return map[raw] || raw
}

function endpointPath(testCase: TestCase) {
  const legacy = testCase as unknown as { steps?: Array<{ request?: { path?: string } }> }
  return testCase.endpoint?.path || testCase.endpoint_path || legacy.steps?.[0]?.request?.path || '-'
}

onMounted(loadEndpoints)
</script>

<style scoped>
.coverage-card {
  margin-bottom: 16px;
}

.coverage-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}

.coverage-item {
  min-height: 84px;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: #f8fbff;
  margin-bottom: 12px;
}

.coverage-item.missing {
  background: #fff5f5;
  border-color: #fab6b6;
}

.coverage-name {
  color: #606266;
  font-size: 13px;
}

.coverage-count {
  margin: 8px 0;
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}
</style>
