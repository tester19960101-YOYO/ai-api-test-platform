<template>
  <el-container class="app-shell">
    <el-aside width="220px" class="side">
      <div class="brand">AI API Test Platform</div>
      <el-menu :default-active="$route.path" router class="menu">
        <el-menu-item index="/projects">项目管理</el-menu-item>
        <el-menu-item index="/environments">环境配置</el-menu-item>
        <el-menu-item index="/api-import">接口导入</el-menu-item>
        <el-menu-item index="/endpoints">接口列表</el-menu-item>
        <el-menu-item index="/ai-cases">AI 用例生成</el-menu-item>
        <el-menu-item index="/test-cases">测试用例</el-menu-item>
        <el-menu-item index="/reports">执行报告</el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div>
          <div class="title">{{ routeTitle }}</div>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>工作台</el-breadcrumb-item>
            <el-breadcrumb-item>{{ routeTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-button size="small" @click="checkHealth">健康检查</el-button>
          <el-tag v-if="healthStatus" :type="healthStatus === 'ok' ? 'success' : 'danger'">
            API：{{ healthStatus }}
          </el-tag>
          <el-tag v-if="projectStore.currentProjectId" type="success">
            项目 ID：{{ projectStore.currentProjectId }}
          </el-tag>
          <el-tag v-else type="info">未选择项目</el-tag>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

import { healthApi } from '@/api'
import { useProjectStore } from '@/stores/project'

const route = useRoute()
const projectStore = useProjectStore()
const healthStatus = ref('')
const routeTitle = computed(() => String(route.meta.title || '工作台'))

async function checkHealth() {
  const result = await healthApi.check()
  healthStatus.value = result.status
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.side {
  background: #1f2937;
  color: #fff;
}

.brand {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 18px;
  font-weight: 700;
  font-size: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.menu {
  border-right: 0;
  background: transparent;
}

.menu :deep(.el-menu-item) {
  color: #d1d5db;
}

.menu :deep(.el-menu-item.is-active) {
  color: #fff;
  background: #2563eb;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.title {
  font-size: 20px;
  font-weight: 650;
  margin-bottom: 8px;
}

.main {
  background: #f5f7fb;
  padding: 18px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
