<template>
  <section class="json-preview-editor">
    <div class="editor-header">
      <div class="title-group">
        <h3>{{ title }}</h3>
        <el-tag size="small" type="info">{{ contentType }}</el-tag>
        <span class="mode-hint">{{ activeModeLabel }}</span>
      </div>
      <div class="toolbar">
        <el-button :type="activeMode === 'example' ? 'primary' : 'default'" @click="activeMode = 'example'">
          展开示例
        </el-button>
        <el-button :type="activeMode === 'schema' ? 'primary' : 'default'" @click="activeMode = 'schema'">
          展开 Schema
        </el-button>
        <el-button @click="copyCurrent">复制</el-button>
        <el-button @click="formatCurrent">格式化</el-button>
        <el-button type="primary" :disabled="readonly" @click="saveCurrent">保存预览修改</el-button>
      </div>
    </div>

    <div class="editor-grid">
      <article class="code-card" :class="{ active: activeMode === 'example' }">
        <div class="code-card-header">
          <div>
            <strong>示例</strong>
            <span>{{ exampleDescription }}</span>
          </div>
          <el-tag size="small" :type="activeMode === 'example' ? 'primary' : 'info'">example</el-tag>
        </div>
        <div class="code-shell">
          <pre class="line-numbers">{{ exampleLineNumbers }}</pre>
          <textarea
            v-model="exampleDraft"
            class="code-editor"
            spellcheck="false"
            :readonly="readonly"
            @focus="activeMode = 'example'"
          />
        </div>
      </article>

      <article class="code-card" :class="{ active: activeMode === 'schema' }">
        <div class="code-card-header">
          <div>
            <strong>Schema</strong>
            <span>{{ schemaDescription }}</span>
          </div>
          <el-tag size="small" :type="activeMode === 'schema' ? 'primary' : 'info'">schema</el-tag>
        </div>
        <div class="code-shell">
          <pre class="line-numbers">{{ schemaLineNumbers }}</pre>
          <textarea
            v-model="schemaDraft"
            class="code-editor"
            spellcheck="false"
            :readonly="readonly"
            @focus="activeMode = 'schema'"
          />
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, ref, watch } from 'vue'

type JsonMode = 'example' | 'schema'

const props = withDefaults(defineProps<{
  title: string
  contentType?: string
  exampleJson: unknown
  schemaJson: unknown
  modelValue: unknown
  readonly?: boolean
  exampleDescription?: string
  schemaDescription?: string
}>(), {
  contentType: 'application/json',
  readonly: false,
  exampleDescription: '示例（来自文档示例或自动生成）',
  schemaDescription: 'Schema（自动展开，可用于查看字段结构）'
})

const emit = defineEmits<{
  'update:modelValue': [value: unknown]
  save: [value: unknown, mode: JsonMode]
}>()

const activeMode = ref<JsonMode>('example')
const exampleDraft = ref('')
const schemaDraft = ref('')

const activeModeLabel = computed(() => {
  return activeMode.value === 'example'
    ? '当前展示：示例（来自文档示例）'
    : '当前展示：Schema（自动展开，可用于请求）'
})
const exampleLineNumbers = computed(() => buildLineNumbers(exampleDraft.value))
const schemaLineNumbers = computed(() => buildLineNumbers(schemaDraft.value))

watch(
  () => props.modelValue,
  (value) => {
    exampleDraft.value = stringify(value ?? props.exampleJson ?? {})
  },
  { immediate: true, deep: true }
)

watch(
  () => props.schemaJson,
  (value) => {
    schemaDraft.value = stringify(value ?? {})
  },
  { immediate: true, deep: true }
)

function stringify(value: unknown) {
  return JSON.stringify(value ?? {}, null, 2)
}

function buildLineNumbers(value: string) {
  const count = Math.max(value.split('\n').length, 1)
  return Array.from({ length: count }, (_, index) => String(index + 1)).join('\n')
}

function currentDraft() {
  return activeMode.value === 'example' ? exampleDraft : schemaDraft
}

async function copyCurrent() {
  await navigator.clipboard?.writeText(currentDraft().value)
  ElMessage.success('已复制')
}

function formatCurrent() {
  try {
    currentDraft().value = stringify(JSON.parse(currentDraft().value || '{}'))
  } catch {
    ElMessage.error('JSON 格式错误')
  }
}

function saveCurrent() {
  try {
    const value = JSON.parse(currentDraft().value || '{}')
    if (activeMode.value === 'example') {
      emit('update:modelValue', value)
    }
    emit('save', value, activeMode.value)
    ElMessage.success('预览修改已保存')
  } catch {
    ElMessage.error('JSON 格式错误')
  }
}
</script>

<style scoped>
.json-preview-editor {
  display: grid;
  gap: 12px;
}

.editor-header {
  align-items: center;
  display: flex;
  gap: 16px;
  justify-content: space-between;
}

.title-group {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  min-width: 0;
}

.title-group h3 {
  font-size: 15px;
  margin: 0;
}

.mode-hint {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
}

.toolbar :deep(.el-button + .el-button) {
  margin-left: 0;
}

.editor-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.code-card {
  background: #fff;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  min-width: 0;
  overflow: hidden;
}

.code-card.active {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 1px rgba(64, 158, 255, 0.14);
}

.code-card-header {
  align-items: center;
  background: #fafafa;
  border-bottom: 1px solid var(--el-border-color-lighter);
  display: flex;
  justify-content: space-between;
  padding: 10px 12px;
}

.code-card-header > div {
  display: grid;
  gap: 3px;
}

.code-card-header span {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.code-shell {
  background: #fff;
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  min-height: 280px;
  max-height: 520px;
  overflow: hidden;
}

.line-numbers {
  background: #f7f8fa;
  border-right: 1px solid var(--el-border-color-lighter);
  color: #8a8f99;
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 13px;
  line-height: 22px;
  margin: 0;
  padding: 14px 10px;
  text-align: right;
  user-select: none;
}

.code-editor {
  background: #fff;
  border: 0;
  box-sizing: border-box;
  color: #1f2937;
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 13px;
  line-height: 22px;
  min-height: 280px;
  outline: none;
  overflow: auto;
  padding: 14px;
  resize: vertical;
  white-space: pre;
  width: 100%;
}

@media (max-width: 1280px) {
  .editor-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .toolbar {
    justify-content: flex-start;
  }
}

@media (max-width: 1100px) {
  .editor-grid {
    grid-template-columns: 1fr;
  }
}
</style>
