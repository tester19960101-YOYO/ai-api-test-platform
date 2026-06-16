<template>
  <div class="page">
    <ProjectRequired :project-id="projectId" />
    <el-alert title="当前使用真实 OpenAI 生成测试用例；如未配置 AI_API_KEY，后端会返回明确配置错误，不会自动 fallback 到 mock" type="info" :closable="false" show-icon />
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

    <el-table :data="generatedCases" border>
      <el-table-column prop="name" label="用例名称" min-width="220" />
      <el-table-column prop="priority" label="优先级" width="110" />
      <el-table-column prop="status" label="状态" width="110" />
      <el-table-column label="场景" width="120">
        <template #default="{ row }">{{ row.variables?.case_type || '-' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="disableCase(row)">禁用</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-drawer v-model="drawerVisible" title="编辑测试用例" size="50%">
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
import type { ApiEndpoint, TestCase } from '@/types'

const route = useRoute()
const projectStore = useProjectStore()
const projectId = computed(() => projectStore.currentProjectId)
const endpoints = ref<ApiEndpoint[]>([])
const selectedEndpointId = ref<number | null>(Number(route.query.endpointId) || null)
const generatedCases = ref<TestCase[]>([])
const generating = ref(false)
const drawerVisible = ref(false)
const editingCase = ref<TestCase | null>(null)

async function loadEndpoints() {
  if (!projectId.value) return
  endpoints.value = await endpointApi.list(projectId.value)
}

async function generateCases() {
  if (!selectedEndpointId.value) return
  generating.value = true
  try {
    const result = await aiApi.generateCases(selectedEndpointId.value)
    generatedCases.value = result.test_cases
    ElMessage.success(`已生成 ${result.case_count} 条 AI 用例`)
  } finally {
    generating.value = false
  }
}

function openEdit(testCase: TestCase) {
  editingCase.value = testCase
  drawerVisible.value = true
}

async function disableCase(testCase: TestCase) {
  await testCaseApi.remove(testCase.id)
  ElMessage.success('已禁用')
  generatedCases.value = generatedCases.value.map((item) =>
    item.id === testCase.id ? { ...item, status: 'inactive' } : item
  )
}

function afterCaseSaved(testCase: TestCase) {
  generatedCases.value = generatedCases.value.map((item) => (item.id === testCase.id ? testCase : item))
  drawerVisible.value = false
}

onMounted(loadEndpoints)
</script>
