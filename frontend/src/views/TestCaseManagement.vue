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
      <el-table-column prop="api_endpoint_id" label="接口 ID" width="100" />
      <el-table-column prop="priority" label="优先级" width="110" />
      <el-table-column prop="status" label="状态" width="110" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="openDetail(row)">详情 / 编辑</el-button>
          <el-button size="small" type="danger" @click="disableCase(row)">禁用</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-drawer v-model="drawerVisible" title="测试用例详情" size="50%">
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

onMounted(loadCases)
</script>
