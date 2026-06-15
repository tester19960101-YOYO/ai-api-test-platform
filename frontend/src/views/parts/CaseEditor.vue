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
    <el-form-item label="断言DSL">
      <AssertionDslBuilder
        v-model="form.assertions_dsl"
        :ai-assertions="aiAssertions"
        :swagger-assertions="swaggerAssertions"
      />
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
import { computed, reactive, ref, watch } from 'vue'

import { testCaseApi } from '@/api'
import AssertionDslBuilder from '@/components/AssertionDslBuilder.vue'
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
  assertions_dsl: [] as string[],
  variables_json: '{}'
})

const aiAssertions = computed(() => {
  const variables = safeParseObject(form.variables_json)
  const current = variables.ai_assertion_dsl
  if (Array.isArray(current)) {
    return current.filter((item): item is string => typeof item === 'string')
  }
  const legacy = variables.ai_assertion_suggestions
  if (isRecord(legacy) && Array.isArray(legacy.suggestions)) {
    return legacy.suggestions.map(assertionToDsl).filter(Boolean)
  }
  return []
})

const swaggerAssertions = computed(() => ['status_code == 200', '$.code == 200', '$.data != null'])

function safeParseObject(text: string) {
  try {
    return parseJsonObject(text, {}) || {}
  } catch {
    return {}
  }
}

function safeParseArray(text: string) {
  try {
    return parseJsonArray(text, []) || []
  } catch {
    return []
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function assertionToDsl(value: unknown): string {
  if (typeof value === 'string') {
    return value
  }
  if (!isRecord(value)) {
    return ''
  }
  const type = String(value.type || 'json_path')
  const path = typeof value.path === 'string' ? value.path : '$.code'
  const expected = value.expected
  if (type === 'status_code') {
    return `status_code == ${expected ?? 200}`
  }
  if (type === 'business_code' || path === '$.code') {
    return `${path} == ${expected ?? 200}`
  }
  if (type === 'json_path_not_null') {
    return `${path} != null`
  }
  if (type === 'json_path_contains') {
    return `${path} contains ${expected ?? ''}`.trim()
  }
  const operator = typeof value.operator === 'string' ? value.operator : '=='
  if (operator === 'exists') {
    return `${path} exists`
  }
  return `${path} ${operator} ${expected ?? 'null'}`
}

function syncForm(testCase: TestCase) {
  Object.assign(form, {
    name: testCase.name,
    priority: testCase.priority,
    status: testCase.status,
    description: testCase.description || '',
    steps_json: stringifyJson(testCase.steps || []),
    assertions_dsl: (testCase.assertions || []).map(assertionToDsl).filter(Boolean),
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
      assertions: form.assertions_dsl,
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
