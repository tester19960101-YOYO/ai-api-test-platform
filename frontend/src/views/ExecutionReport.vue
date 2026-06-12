<template>
  <div class="page">
    <ProjectRequired :project-id="projectId" />
    <el-form inline>
      <el-form-item label="环境">
        <el-select v-model="form.environment_id" placeholder="选择环境" style="width: 260px">
          <el-option
            v-for="environment in environments"
            :key="environment.id"
            :label="`${environment.name} - ${environment.base_url}`"
            :value="environment.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="测试用例">
        <el-select v-model="form.case_ids" multiple collapse-tags placeholder="选择用例" style="width: 360px">
          <el-option v-for="item in cases" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="超时">
        <el-input-number v-model="form.timeout" :min="1" :max="120" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :disabled="!canRun" :loading="running" @click="runExecution">执行测试</el-button>
      </el-form-item>
    </el-form>

    <el-row v-if="execution" :gutter="12">
      <el-col :span="6">
        <el-statistic title="总数" :value="execution.task.total_cases" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="通过" :value="execution.task.passed_cases" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="失败" :value="execution.task.failed_cases" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="跳过" :value="0" />
      </el-col>
    </el-row>

    <el-descriptions v-if="execution" border :column="1">
      <el-descriptions-item label="任务状态">
        <el-tag :type="execution.task.status === 'passed' ? 'success' : 'danger'">{{ execution.task.status }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="报告路径">
        {{ execution.report_path }}
      </el-descriptions-item>
      <el-descriptions-item label="日志路径">
        {{ execution.log_path }}
      </el-descriptions-item>
      <el-descriptions-item label="生成工程">
        {{ execution.generated_project_path }}
      </el-descriptions-item>
    </el-descriptions>

    <el-table v-if="execution" :data="execution.results" border>
      <el-table-column prop="test_case_id" label="用例 ID" width="100" />
      <el-table-column prop="status" label="状态" width="110" />
      <el-table-column prop="status_code" label="状态码" width="100" />
      <el-table-column prop="response_time_ms" label="耗时 ms" width="120" />
      <el-table-column prop="error_message" label="错误信息" min-width="260" show-overflow-tooltip />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'

import { environmentApi, executionApi, testCaseApi } from '@/api'
import ProjectRequired from '@/components/ProjectRequired.vue'
import { useProjectStore } from '@/stores/project'
import type { Environment, ExecutionRunResponse, TestCase } from '@/types'

const projectStore = useProjectStore()
const projectId = computed(() => projectStore.currentProjectId)
const environments = ref<Environment[]>([])
const cases = ref<TestCase[]>([])
const running = ref(false)
const execution = ref<ExecutionRunResponse | null>(null)
const form = reactive({
  environment_id: null as number | null,
  case_ids: [] as number[],
  timeout: 10
})
const canRun = computed(() => Boolean(projectId.value && form.environment_id && form.case_ids.length))

async function loadOptions() {
  if (!projectId.value) return
  environments.value = await environmentApi.list(projectId.value)
  cases.value = await testCaseApi.list(projectId.value)
  form.environment_id = environments.value.find((item) => item.is_default)?.id || environments.value[0]?.id || null
}

async function runExecution() {
  if (!form.environment_id) return
  running.value = true
  try {
    execution.value = await executionApi.run({
      project_id: projectId.value,
      environment_id: form.environment_id,
      case_ids: form.case_ids,
      timeout: form.timeout
    })
    ElMessage.success('执行完成')
  } finally {
    running.value = false
  }
}

onMounted(loadOptions)
</script>
