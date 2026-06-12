<template>
  <el-input
    class="json-textarea"
    :model-value="modelValue"
    type="textarea"
    :rows="rows"
    resize="vertical"
    spellcheck="false"
    @update:model-value="$emit('update:modelValue', $event)"
  />
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
  rows?: number
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>
