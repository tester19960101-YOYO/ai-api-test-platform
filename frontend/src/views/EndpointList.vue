<template>
  <div class="page">
    <ProjectRequired :project-id="projectId" />
    <div class="page-toolbar">
      <div class="toolbar-left">
        <el-button :disabled="!projectId" @click="loadEndpoints">刷新</el-button>
      </div>
    </div>

    <el-table v-loading="loading" :data="endpoints" border>
      <el-table-column prop="name" label="接口名称" min-width="180" />
      <el-table-column prop="method" label="方法" width="100">
        <template #default="{ row }">
          <el-tag class="method-tag" type="primary">{{ row.method }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="path" label="路径" min-width="260" show-overflow-tooltip />
      <el-table-column prop="group_name" label="分组" width="140" />
      <el-table-column prop="auth_required" label="鉴权" width="90">
        <template #default="{ row }">{{ row.auth_required ? '是' : '否' }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="110" />
      <el-table-column label="操作" width="260" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="$router.push(`/endpoints/${row.id}`)">详情</el-button>
          <el-button size="small" @click="toggleStatus(row)">
            {{ row.status === 'active' ? '禁用' : '启用' }}
          </el-button>
          <el-button size="small" type="success" @click="$router.push({ path: '/ai-cases', query: { endpointId: row.id } })">
            生成用例
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'

import { endpointApi } from '@/api'
import ProjectRequired from '@/components/ProjectRequired.vue'
import { useProjectStore } from '@/stores/project'
import type { ApiEndpoint } from '@/types'

const projectStore = useProjectStore()
const projectId = computed(() => projectStore.currentProjectId)
const loading = ref(false)
const endpoints = ref<ApiEndpoint[]>([])

async function loadEndpoints() {
  if (!projectId.value) return
  loading.value = true
  try {
    endpoints.value = await endpointApi.list(projectId.value)
  } finally {
    loading.value = false
  }
}

async function toggleStatus(endpoint: ApiEndpoint) {
  const nextStatus = endpoint.status === 'active' ? 'inactive' : 'active'
  await endpointApi.updateStatus(endpoint.id, nextStatus)
  ElMessage.success('状态已更新')
  await loadEndpoints()
}

onMounted(loadEndpoints)
</script>
