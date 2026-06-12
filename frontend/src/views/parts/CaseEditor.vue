<template>
  <el-form label-width="110px">
    <el-form-item label="用例名称">
      <el-input v-model="form.name" />
    </el-form-item>
    <el-form-item label="优先级">
      <el-select v-model="form.priority">
        <el-option label="low" value="low" />
        <el-option label="medium" value="medium" />
        <el-option label="high" value="high" />
      </el-select>
    </el-form-item>
    <el-form-item label="状态">
      <el-select v-model="form.status">
        <el-option label="active" value="active" />
        <el-option label="draft" value="draft" />
        <el-option label="generated" value="generated" />
        <el-option label="inactive" value="inactive" />
      </el-select>
    </el-form-item>
    <el-form-item label="描述">
      <el-input v-model="form.description" type="textarea" :rows="3" />
    </el-form-item>
    <el-form-item label="请求参数">
      <JsonTextarea v-model="form.steps_json" :rows="10" />
    </el-form-item>
    <el-form-item label="断言规则">
      <JsonTextarea v-model="form.assertions_json" :rows="10" />
    </el-form-item>
    <el-form-item label="变量">
      <JsonTextarea v-model="form.variables_json" :rows="6" />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" :loading="saving" @click="save">保存</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { reactive, ref, watch } from 'vue'

import { testCaseApi } from '@/api'
import JsonTextarea from '@/components/JsonTextarea.vue'
import type { TestCase } from '@/types'
import { parseJsonArray, parseJsonObject, stringifyJson } from '@/utils/json'

const props = defineProps<{
  caseItem: TestCase
}>()

const emit = defineEmits<{
  saved: [testCase: TestCase]
}>()

const saving = ref(false)
const form = reactive({
  name: '',
  priority: 'medium',
  status: 'draft',
  description: '',
  steps_json: '[]',
  assertions_json: '[]',
  variables_json: '{}'
})

function syncForm(testCase: TestCase) {
  Object.assign(form, {
    name: testCase.name,
    priority: testCase.priority,
    status: testCase.status,
    description: testCase.description || '',
    steps_json: stringifyJson(testCase.steps || []),
    assertions_json: stringifyJson(testCase.assertions || []),
    variables_json: stringifyJson(testCase.variables || {})
  })
}

async function save() {
  saving.value = true
  try {
    const saved = await testCaseApi.update(props.caseItem.id, {
      name: form.name,
      priority: form.priority,
      status: form.status,
      description: form.description,
      steps: parseJsonArray(form.steps_json, []),
      assertions: parseJsonArray(form.assertions_json, []),
      variables: parseJsonObject(form.variables_json, {})
    })
    ElMessage.success('保存成功')
    emit('saved', saved)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存失败')
  } finally {
    saving.value = false
  }
}

watch(() => props.caseItem, syncForm, { immediate: true })
</script>
