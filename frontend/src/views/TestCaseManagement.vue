<template>
  <div class="page">
    <ProjectRequired :project-id="projectId" />
    <div class="page-toolbar">
      <div class="toolbar-left">
        <el-button :disabled="!projectId" @click="loadCases">刷新</el-button>
      </div>
    </div>

    <el-table v-loading="loading" :data="cases" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="用例名称" min-width="220" />
      <el-table-column label="接口名称" min-width="180">
        <template #default="{ row }">{{ row.endpoint?.name || row.endpoint_name || '-' }}</template>
      </el-table-column>
      <el-table-column label="接口路径" min-width="220">
        <template #default="{ row }">{{ endpointPath(row) }}</template>
      </el-table-column>
      <el-table-column label="类型" width="130">
        <template #default="{ row }">{{ typeLabel(row) }}</template>
      </el-table-column>
      <el-table-column label="优先级" width="100">
        <template #default="{ row }">
          <el-tag :type="priorityTag(priorityValue(row))">{{ priorityValue(row) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">{{ statusLabel(row.status) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="openDetail(row)">详情 / 编辑</el-button>
          <el-button size="small" type="danger" @click="disableCase(row)">禁用</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-drawer v-model="drawerVisible" title="测试用例详情" size="58%">
      <CaseEditor v-if="editingCase" :case-item="editingCase" @saved="afterSaved" />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'

import { testCaseApi } from '@/api'
import ProjectRequired from '@/components/ProjectRequired.vue'
import { useProjectStore } from '@/stores/project'
import type { TestCase } from '@/types'
import CaseEditor from '@/views/parts/CaseEditor.vue'

const projectStore = useProjectStore()
const projectId = computed(() => projectStore.currentProjectId)
const loading = ref(false)
const cases = ref<TestCase[]>([])
const drawerVisible = ref(false)
const editingCase = ref<TestCase | null>(null)

const typeMap: Record<string, string> = {
  functional: '功能正确性',
  validation: '参数校验',
  boundary: '边界值',
  negative: '异常场景',
  security: '安全测试',
  business: '业务语义',
  dependency: '数据依赖'
}

const statusMap: Record<string, string> = {
  generated: '已生成',
  edited: '已编辑',
  disabled: '已禁用',
  passed: '通过',
  failed: '失败'
}

async function loadCases() {
  if (!projectId.value) return
  loading.value = true
  try {
    cases.value = await testCaseApi.list(projectId.value)
  } finally {
    loading.value = false
  }
}

function openDetail(testCase: TestCase) {
  editingCase.value = testCase
  drawerVisible.value = true
}

async function disableCase(testCase: TestCase) {
  await testCaseApi.remove(testCase.id)
  ElMessage.success('已禁用')
  await loadCases()
}

function afterSaved(testCase: TestCase) {
  cases.value = cases.value.map((item) => (item.id === testCase.id ? testCase : item))
  drawerVisible.value = false
}

function typeLabel(testCase: TestCase) {
  const type = normalizeType(testCase)
  return typeMap[type] || type || '-'
}

function statusLabel(status: string) {
  return statusMap[status] || status || '-'
}

function priorityValue(testCase: TestCase) {
  const raw = String(testCase.priority || '')
  const map: Record<string, string> = { high: 'P0', medium: 'P1', low: 'P2' }
  return map[raw.toLowerCase()] || raw || '-'
}

function priorityTag(priority: string) {
  const value = typeof priority === 'string' ? priority : ''
  if (value === 'P0') return 'danger'
  if (value === 'P1') return 'warning'
  return 'info'
}

function normalizeType(testCase: TestCase) {
  const legacy = testCase as unknown as { variables?: Record<string, unknown> }
  const raw = String(testCase.type || legacy.variables?.coverage_dimension || legacy.variables?.case_type || '')
  const map: Record<string, string> = { normal: 'functional', error: 'negative', exception: 'negative', auth: 'security' }
  return map[raw] || raw
}

function endpointPath(testCase: TestCase) {
  const legacy = testCase as unknown as { steps?: Array<{ request?: { path?: string } }> }
  return testCase.endpoint?.path || testCase.endpoint_path || legacy.steps?.[0]?.request?.path || '-'
}

onMounted(loadCases)
</script>
