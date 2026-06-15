<template>
  <div class="page">
    <div class="page-toolbar">
      <div class="toolbar-left">
        <el-button @click="$router.back()">返回</el-button>
        <el-button type="primary" :loading="saving" @click="saveEndpoint">保存基础信息</el-button>
      </div>
    </div>

    <el-form v-if="endpoint" label-width="150px">
      <el-form-item label="接口名称">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="请求方法">
        <el-select v-model="form.method">
          <el-option v-for="method in methods" :key="method" :label="method" :value="method" />
        </el-select>
      </el-form-item>
      <el-form-item label="接口路径">
        <el-input v-model="form.path" />
      </el-form-item>
      <el-form-item label="接口分组">
        <el-input v-model="form.group_name" />
      </el-form-item>
      <el-form-item label="是否鉴权">
        <el-switch v-model="form.auth_required" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item label="headers_json">
        <JsonTextarea :model-value="stringifyJson(endpoint.headers)" :rows="5" />
      </el-form-item>
      <el-form-item label="query_params_json">
        <JsonTextarea :model-value="stringifyJson(endpoint.request_params?.query)" :rows="5" />
      </el-form-item>
      <el-form-item label="path_params_json">
        <JsonTextarea :model-value="stringifyJson(endpoint.request_params?.path)" :rows="5" />
      </el-form-item>
      <el-form-item label="body_json">
        <JsonTextarea :model-value="stringifyJson(endpoint.request_body_schema)" :rows="6" />
      </el-form-item>
      <el-form-item label="response_json">
        <JsonTextarea :model-value="stringifyJson(endpoint.response_schema)" :rows="6" />
      </el-form-item>
      <el-form-item label="swagger_assertions">
        <JsonTextarea :model-value="swaggerAssertionPreview" :rows="6" />
      </el-form-item>
      <el-form-item label="examples_json">
        <JsonTextarea :model-value="stringifyJson({ request: endpoint.example_request, response: endpoint.example_response })" :rows="6" />
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'

import { endpointApi } from '@/api'
import JsonTextarea from '@/components/JsonTextarea.vue'
import type { ApiEndpoint } from '@/types'
import { stringifyJson } from '@/utils/json'

const route = useRoute()
const endpoint = ref<ApiEndpoint | null>(null)
const saving = ref(false)
const methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
const form = reactive({
  name: '',
  method: 'GET',
  path: '',
  group_name: '',
  auth_required: false,
  description: ''
})

const swaggerAssertionPreview = computed(() => {
  if (!endpoint.value) return ''
  const responseSchema = endpoint.value.response_schema || {}
  const properties = isRecord(responseSchema) && isRecord(responseSchema.properties) ? responseSchema.properties : {}
  return stringifyJson({
    source: 'swagger',
    assertions: [
      { type: 'status_code', operator: '==', expected: 200 },
      ...('code' in properties ? [{ type: 'business_code', path: '$.code', operator: '==', success_codes: [200, 0] }] : []),
      ...('data' in properties ? [{ type: 'json_path', path: '$.data', operator: 'exists', enabled_when: 'business_success' }] : [])
    ]
  })
})

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

async function loadEndpoint() {
  endpoint.value = await endpointApi.detail(Number(route.params.id))
  Object.assign(form, {
    name: endpoint.value.name,
    method: endpoint.value.method,
    path: endpoint.value.path,
    group_name: endpoint.value.group_name || '',
    auth_required: endpoint.value.auth_required,
    description: endpoint.value.description || ''
  })
}

async function saveEndpoint() {
  saving.value = true
  try {
    endpoint.value = await endpointApi.update(Number(route.params.id), { ...form })
    ElMessage.success('保存成功')
  } finally {
    saving.value = false
  }
}

onMounted(loadEndpoint)
</script>
