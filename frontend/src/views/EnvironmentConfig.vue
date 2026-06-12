<template>
  <div class="page">
    <ProjectRequired :project-id="projectId" />
    <div class="page-toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :disabled="!projectId" @click="openCreate">新建环境</el-button>
        <el-button :disabled="!projectId" @click="loadEnvironments">刷新</el-button>
      </div>
    </div>

    <el-table v-loading="loading" :data="environments" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="环境名称" width="160" />
      <el-table-column prop="base_url" label="base_url" min-width="260" show-overflow-tooltip />
      <el-table-column prop="is_default" label="默认" width="90">
        <template #default="{ row }">
          <el-tag :type="row.is_default ? 'success' : 'info'">{{ row.is_default ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="110" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="removeEnvironment(row)">停用</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑环境' : '新建环境'" width="760px">
      <el-form label-width="140px">
        <el-form-item label="环境名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="base_url">
          <el-input v-model="form.base_url" />
        </el-form-item>
        <el-form-item label="默认环境">
          <el-switch v-model="form.is_default" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="active" value="active" />
            <el-option label="inactive" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item label="headers_json">
          <JsonTextarea v-model="form.headers_json" :rows="5" />
        </el-form-item>
        <el-form-item label="auth_config_json">
          <JsonTextarea v-model="form.auth_config_json" :rows="4" />
        </el-form-item>
        <el-form-item label="timeout_seconds">
          <el-input-number v-model="form.timeout_seconds" :min="1" :max="120" />
        </el-form-item>
        <el-form-item label="retry_count">
          <el-input-number v-model="form.retry_count" :min="0" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEnvironment">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'

import { environmentApi } from '@/api'
import JsonTextarea from '@/components/JsonTextarea.vue'
import ProjectRequired from '@/components/ProjectRequired.vue'
import { useProjectStore } from '@/stores/project'
import type { Environment } from '@/types'
import { parseJsonObject, stringifyJson } from '@/utils/json'

const projectStore = useProjectStore()
const projectId = computed(() => projectStore.currentProjectId)
const loading = ref(false)
const environments = ref<Environment[]>([])
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const form = reactive({
  name: '',
  base_url: '',
  is_default: false,
  status: 'active',
  headers_json: '{}',
  auth_config_json: '{}',
  timeout_seconds: 10,
  retry_count: 0
})

async function loadEnvironments() {
  if (!projectId.value) return
  loading.value = true
  try {
    environments.value = await environmentApi.list(projectId.value)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    name: '',
    base_url: '',
    is_default: false,
    status: 'active',
    headers_json: '{}',
    auth_config_json: '{}',
    timeout_seconds: 10,
    retry_count: 0
  })
  dialogVisible.value = true
}

function openEdit(environment: Environment) {
  const variables = environment.variables || {}
  editingId.value = environment.id
  Object.assign(form, {
    name: environment.name,
    base_url: environment.base_url,
    is_default: environment.is_default,
    status: environment.status,
    headers_json: stringifyJson(environment.headers || {}),
    auth_config_json: stringifyJson(variables.auth_config_json || {}),
    timeout_seconds: Number(variables.timeout_seconds || 10),
    retry_count: Number(variables.retry_count || 0)
  })
  dialogVisible.value = true
}

async function submitEnvironment() {
  try {
    const payload = {
      name: form.name,
      base_url: form.base_url,
      is_default: form.is_default,
      status: form.status,
      headers: parseJsonObject(form.headers_json, {}),
      variables: {
        auth_config_json: parseJsonObject(form.auth_config_json, {}),
        timeout_seconds: form.timeout_seconds,
        retry_count: form.retry_count
      }
    }
    if (editingId.value) {
      await environmentApi.update(editingId.value, payload)
    } else {
      await environmentApi.create(projectId.value, payload)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    await loadEnvironments()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : 'JSON 格式错误')
  }
}

async function removeEnvironment(environment: Environment) {
  await ElMessageBox.confirm(`确认停用环境「${environment.name}」？`, '确认操作')
  await environmentApi.remove(environment.id)
  ElMessage.success('已停用')
  await loadEnvironments()
}

onMounted(loadEnvironments)
</script>
