<template>
  <el-form label-width="120px">
    <el-form-item label="用例名称">
      <el-input v-model="form.name" />
    </el-form-item>
    <el-form-item label="用例类型">
      <el-select v-model="form.type">
        <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
    </el-form-item>
    <el-form-item label="优先级">
      <el-select v-model="form.priority">
        <el-option label="P0" value="P0" />
        <el-option label="P1" value="P1" />
        <el-option label="P2" value="P2" />
      </el-select>
    </el-form-item>
    <el-form-item label="状态">
      <el-select v-model="form.status">
        <el-option label="已生成" value="generated" />
        <el-option label="已编辑" value="edited" />
        <el-option label="已禁用" value="disabled" />
        <el-option label="通过" value="passed" />
        <el-option label="失败" value="failed" />
      </el-select>
    </el-form-item>
    <el-form-item label="风险等级">
      <el-select v-model="form.risk_level">
        <el-option label="高" value="high" />
        <el-option label="中" value="medium" />
        <el-option label="低" value="low" />
      </el-select>
    </el-form-item>
    <el-form-item label="描述">
      <el-input v-model="form.description" type="textarea" :rows="3" />
    </el-form-item>
    <el-form-item label="请求参数">
      <JsonTextarea v-model="form.request_json" :rows="10" />
    </el-form-item>
    <el-form-item label="断言 DSL">
      <AssertionDslBuilder
        v-model="form.dsl_assertions"
        :ai-assertions="aiAssertions"
        :swagger-assertions="swaggerAssertions"
      />
    </el-form-item>
    <el-form-item label="结构化断言">
      <JsonTextarea v-model="assertionsPreview" :rows="8" />
    </el-form-item>
    <el-form-item label="覆盖标签">
      <JsonTextarea v-model="form.coverage_tag_json" :rows="3" />
    </el-form-item>
    <el-form-item label="数据依赖">
      <JsonTextarea v-model="form.data_dependency_json" :rows="4" />
    </el-form-item>
    <el-form-item label="AI 元数据">
      <JsonTextarea v-model="form.ai_metadata_json" :rows="6" />
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
  type: 'functional',
  priority: 'P1',
  status: 'generated',
  risk_level: 'medium',
  description: '',
  request_json: '{}',
  dsl_assertions: [] as string[],
  coverage_tag_json: '[]',
  data_dependency_json: '{}',
  ai_metadata_json: '{}'
})

const typeOptions = [
  { label: '功能正确性', value: 'functional' },
  { label: '参数校验', value: 'validation' },
  { label: '边界值', value: 'boundary' },
  { label: '异常场景', value: 'negative' },
  { label: '安全测试', value: 'security' },
  { label: '业务语义', value: 'business' },
  { label: '数据依赖', value: 'dependency' }
]

const aiAssertions = computed(() => {
  const metadata = safeParseObject(form.ai_metadata_json)
  const legacy = props.caseItem as unknown as {
    variables?: { ai_assertion_dsl?: string[] | string }
  }
  const items = metadata.dsl_assertions || metadata.ai_assertion_dsl || legacy.variables?.ai_assertion_dsl || props.caseItem.dsl_assertions
  return Array.isArray(items) ? items.filter((item): item is string => typeof item === 'string') : []
})

const swaggerAssertions = computed(() => ['status_code == 200', '$.code == 200', '$.data != null'])

const assertionsPreview = computed({
  get() {
    return stringifyJson(form.dsl_assertions.map(dslToAssertion))
  },
  set() {
    return
  }
})

function safeParseObject(text: string) {
  try {
    return parseJsonObject(text, {}) || {}
  } catch {
    return {}
  }
}

function dslToAssertion(dsl: string) {
  const normalized = dsl.trim()
  if (normalized.startsWith('status_code')) {
    return { type: 'status_code', expression: normalized, expected: extractExpected(normalized), description: 'HTTP状态码断言' }
  }
  return { type: 'jsonpath', expression: normalized, expected: extractExpected(normalized), description: 'JSONPath断言' }
}

function extractExpected(dsl: string) {
  const matched = dsl.match(/(?:==|!=|>|<|contains)\s+(.+)$/)
  return matched ? matched[1].replace(/^['"]|['"]$/g, '') : null
}

function syncForm(testCase: TestCase) {
  const normalizedType = normalizeCaseType(testCase)
  const normalizedPriority = normalizePriority(testCase)
  const normalizedRequest = normalizeRequest(testCase)
  const normalizedDsl = normalizeDslAssertions(testCase)
  Object.assign(form, {
    name: testCase.name,
    type: normalizedType,
    priority: normalizedPriority,
    status: testCase.status || 'generated',
    risk_level: testCase.risk_level || priorityToRisk(normalizedPriority),
    description: testCase.description || '',
    request_json: stringifyJson(normalizedRequest),
    dsl_assertions: normalizedDsl,
    coverage_tag_json: stringifyJson(testCase.coverage_tag?.length ? testCase.coverage_tag : [normalizedType]),
    data_dependency_json: stringifyJson(testCase.data_dependency || {}),
    ai_metadata_json: stringifyJson(normalizeAiMetadata(testCase))
  })
}

function normalizeCaseType(testCase: TestCase) {
  const legacy = testCase as unknown as { variables?: Record<string, unknown> }
  const raw = String(testCase.type || legacy.variables?.coverage_dimension || legacy.variables?.case_type || 'functional')
  const map: Record<string, string> = {
    normal: 'functional',
    error: 'negative',
    exception: 'negative',
    auth: 'security'
  }
  return map[raw] || raw
}

function normalizePriority(testCase: TestCase) {
  const legacy = testCase as unknown as { variables?: Record<string, unknown> }
  const raw = String(testCase.priority || legacy.variables?.risk_level || 'P1')
  const map: Record<string, string> = {
    high: 'P0',
    medium: 'P1',
    low: 'P2'
  }
  return map[raw.toLowerCase()] || raw
}

function priorityToRisk(priority: string) {
  if (priority === 'P0') return 'high'
  if (priority === 'P2') return 'low'
  return 'medium'
}

function normalizeRequest(testCase: TestCase) {
  if (testCase.request && Object.keys(testCase.request as Record<string, unknown>).length) return testCase.request
  if (testCase.request_data && Object.keys(testCase.request_data).length) return testCase.request_data
  const legacy = testCase as unknown as {
    steps?: Array<{ request?: Record<string, unknown> }>
  }
  const request = legacy.steps?.[0]?.request
  return request && typeof request === 'object' ? request : {}
}

function normalizeDslAssertions(testCase: TestCase) {
  if (Array.isArray(testCase.dsl_assertions) && testCase.dsl_assertions.length) return [...testCase.dsl_assertions]
  const legacy = testCase as unknown as {
    variables?: { ai_assertion_dsl?: string[] | string }
  }
  const value = legacy.variables?.ai_assertion_dsl
  if (Array.isArray(value)) return value.filter((item): item is string => typeof item === 'string')
  if (typeof value === 'string' && value.trim()) return value.split(/\n+/).map((item) => item.trim()).filter(Boolean)
  return []
}

function normalizeAiMetadata(testCase: TestCase) {
  const legacy = testCase as unknown as { variables?: Record<string, unknown> }
  return Object.keys(testCase.ai_metadata || {}).length ? testCase.ai_metadata : legacy.variables || {}
}

async function save() {
  saving.value = true
  try {
    const saved = await testCaseApi.update(props.caseItem.id, {
      name: form.name,
      type: form.type,
      priority: form.priority,
      status: form.status === 'generated' ? 'edited' : form.status,
      risk_level: form.risk_level,
      description: form.description,
      request: parseJsonObject(form.request_json, {}) || {},
      dsl_assertions: form.dsl_assertions,
      coverage_tag: (parseJsonArray(form.coverage_tag_json, []) || []).filter(
        (item): item is string => typeof item === 'string'
      ),
      data_dependency: parseJsonObject(form.data_dependency_json, {}) || {},
      ai_metadata: parseJsonObject(form.ai_metadata_json, {}) || {}
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
