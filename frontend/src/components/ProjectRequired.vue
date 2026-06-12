<template>
  <el-alert
    v-if="!projectId"
    title="请先在项目管理页选择项目工作区"
    type="warning"
    :closable="false"
    show-icon
  />
</template>

<script setup lang="ts">
defineProps<{
  projectId: number
}>()
</script>
