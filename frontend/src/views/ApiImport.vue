<template>
  <div class="page">
    <ProjectRequired :project-id="projectId" />
    <el-tabs v-model="activeTab">
      <el-tab-pane label="OpenAPI JSON" name="openapi">
        <el-form label-width="110px">
          <el-form-item label="文档名称">
            <el-input v-model="openapiForm.name" />
          </el-form-item>
          <el-form-item label="JSON 内容">
            <JsonTextarea v-model="openapiForm.content" :rows="16" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :disabled="!projectId" :loading="loading" @click="importOpenApi">
              导入并解析
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      <el-tab-pane label="curl 文本" name="curl">
        <el-form label-width="110px">
          <el-form-item label="文档名称">
            <el-input v-model="curlForm.name" />
          </el-form-item>
          <el-form-item label="curl 文本">
            <JsonTextarea v-model="curlForm.curl_text" :rows="10" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :disabled="!projectId" :loading="loading" @click="importCurl">
              导入并解析
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <el-table v-if="result" :data="result.endpoints" border>
      <el-table-column prop="name" label="接口名称" min-width="180" />
      <el-table-column prop="method" label="方法" width="100" />
      <el-table-column prop="path" label="路径" min-width="240" />
      <el-table-column prop="group_name" label="分组" width="140" />
      <el-table-column prop="auth_required" label="鉴权" width="90">
        <template #default="{ row }">{{ row.auth_required ? '是' : '否' }}</template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, reactive, ref } from 'vue'

import { documentApi } from '@/api'
import JsonTextarea from '@/components/JsonTextarea.vue'
import ProjectRequired from '@/components/ProjectRequired.vue'
import { useProjectStore } from '@/stores/project'
import type { ApiDocumentImportResult } from '@/types'

const projectStore = useProjectStore()
const projectId = computed(() => projectStore.currentProjectId)
const activeTab = ref('openapi')
const loading = ref(false)
const result = ref<ApiDocumentImportResult | null>(null)

const openapiForm = reactive({
  name: 'OpenAPI 文档',
  content: '{\n  "openapi": "3.0.0",\n  "info": { "title": "Demo API", "version": "1.0.0" },\n  "paths": {}\n}'
})
const curlForm = reactive({
  name: 'curl 导入',
  curl_text: "curl -X GET 'https://api.example.com/users?id=1'"
})

async function importOpenApi() {
  loading.value = true
  try {
    result.value = await documentApi.importOpenApi(projectId.value, {
      name: openapiForm.name,
      content: JSON.parse(openapiForm.content)
    })
    ElMessage.success(`导入成功，解析 ${result.value.endpoint_count} 个接口`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '导入失败')
  } finally {
    loading.value = false
  }
}

async function importCurl() {
  loading.value = true
  try {
    result.value = await documentApi.importCurl(projectId.value, curlForm)
    ElMessage.success(`导入成功，解析 ${result.value.endpoint_count} 个接口`)
  } finally {
    loading.value = false
  }
}
</script>
