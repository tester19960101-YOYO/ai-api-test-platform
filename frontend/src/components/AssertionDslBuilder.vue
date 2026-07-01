<template>
  <div class="assertion-builder">
    <div class="builder-section">
      <div class="section-title">
        <span>用户断言 DSL</span>
        <el-button size="small" type="primary" plain @click="addAssertion">新增断言</el-button>
      </div>
      <div v-if="localItems.length === 0" class="empty-text">暂无用户断言，可从模板、AI 或 Swagger 区插入。</div>
      <div v-for="(_, index) in localItems" :key="index" class="dsl-row">
        <el-input v-model="localItems[index]" placeholder="例如：$.code == 200" @change="emitChange" />
        <el-button size="small" @click="copyText(localItems[index])">复制</el-button>
        <el-button size="small" type="danger" plain @click="removeAssertion(index)">删除</el-button>
      </div>
    </div>

    <div class="builder-section">
      <div class="section-title">模板</div>
      <div class="chip-list">
        <el-button v-for="item in templates" :key="item" size="small" @click="insertAssertion(item)">
          {{ item }}
        </el-button>
      </div>
    </div>

    <div class="builder-section">
      <div class="section-title">AI 断言建议</div>
      <div v-if="aiItems.length === 0" class="empty-text">暂无 AI 建议。</div>
      <div v-for="item in aiItems" :key="item" class="suggestion-row">
        <code>{{ item }}</code>
        <div>
          <el-button size="small" @click="copyText(item)">复制</el-button>
          <el-button size="small" type="primary" plain @click="insertAssertion(item)">插入</el-button>
        </div>
      </div>
    </div>

    <div class="builder-section">
      <div class="section-title">Swagger 断言</div>
      <div v-if="swaggerItems.length === 0" class="empty-text">暂无 Swagger 断言。</div>
      <div v-for="item in swaggerItems" :key="item" class="suggestion-row">
        <code>{{ item }}</code>
        <div>
          <el-button size="small" @click="copyText(item)">复制</el-button>
          <el-button size="small" type="primary" plain @click="insertAssertion(item)">插入</el-button>
        </div>
      </div>
    </div>

    <div class="builder-section">
      <div class="section-title">最终融合断言预览</div>
      <div class="preview-list">
        <div v-for="item in finalPreview" :key="item" class="preview-item">{{ item }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: string[]
    aiAssertions?: string[]
    swaggerAssertions?: string[]
  }>(),
  {
    aiAssertions: () => [],
    swaggerAssertions: () => []
  }
)

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const templates = ['$.code == 200', '$.msg=="操作成功"', '$.data != null', 'status_code == 200']
const localItems = ref<string[]>([])

const aiItems = computed(() => uniqueItems(props.aiAssertions))
const swaggerItems = computed(() => uniqueItems(props.swaggerAssertions))
const finalPreview = computed(() => uniqueItems([...localItems.value, ...swaggerItems.value, ...aiItems.value.map((item) => `${item}  # AI建议`)]))

watch(
  () => props.modelValue,
  (value) => {
    localItems.value = [...(value || [])]
  },
  { immediate: true }
)

function addAssertion() {
  localItems.value.push('$.code == 200')
  emitChange()
}

function removeAssertion(index: number) {
  localItems.value.splice(index, 1)
  emitChange()
}

function insertAssertion(item: string) {
  if (!localItems.value.includes(item)) {
    localItems.value.push(item)
    emitChange()
  }
}

function emitChange() {
  emit(
    'update:modelValue',
    localItems.value.map((item) => item.trim()).filter(Boolean)
  )
}

async function copyText(text: string) {
  await navigator.clipboard.writeText(text)
  ElMessage.success('已复制')
}

function uniqueItems(items: string[]) {
  return Array.from(new Set(items.map((item) => item.trim()).filter(Boolean)))
}
</script>

<style scoped>
.assertion-builder {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.builder-section {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
  background: #fff;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  font-weight: 600;
}

.dsl-row,
.suggestion-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.empty-text {
  color: #909399;
  font-size: 13px;
}

.suggestion-row code,
.preview-item {
  padding: 6px 8px;
  border-radius: 4px;
  background: #f6f8fa;
  color: #1f2937;
  font-family: Consolas, monospace;
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
</style>
