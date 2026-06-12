<template>
  <div class="page">
    <div class="page-toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="openCreate">新建项目</el-button>
        <el-button @click="loadProjects">刷新</el-button>
      </div>
      <el-tag v-if="projectStore.currentProjectId" type="success">
        当前工作区：{{ projectStore.currentProject?.name || projectStore.currentProjectId }}
      </el-tag>
    </div>

    <el-table v-loading="loading" :data="projects" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="项目名称" min-width="180" />
      <el-table-column prop="owner_name" label="负责人" width="140" />
      <el-table-column prop="status" label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="220" show-overflow-tooltip />
      <el-table-column label="操作" width="300" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="enterWorkspace(row)">进入工作区</el-button>
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="removeProject(row)">停用</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑项目' : '新建项目'" width="520px">
      <el-form label-width="90px">
        <el-form-item label="项目名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="form.owner_name" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="active" value="active" />
            <el-option label="inactive" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitProject">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { projectApi } from '@/api'
import { useProjectStore } from '@/stores/project'
import type { Project } from '@/types'

const router = useRouter()
const projectStore = useProjectStore()
const loading = ref(false)
const projects = ref<Project[]>([])
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const form = reactive({
  name: '',
  owner_name: '',
  status: 'active',
  description: ''
})

async function loadProjects() {
  loading.value = true
  try {
    projects.value = await projectApi.list()
    const current = projects.value.find((item) => item.id === projectStore.currentProjectId)
    if (current) {
      projectStore.setCurrentProject(current)
    }
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, { name: '', owner_name: '', status: 'active', description: '' })
  dialogVisible.value = true
}

function openEdit(project: Project) {
  editingId.value = project.id
  Object.assign(form, {
    name: project.name,
    owner_name: project.owner_name || '',
    status: project.status,
    description: project.description || ''
  })
  dialogVisible.value = true
}

async function submitProject() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入项目名称')
    return
  }
  const payload = { ...form }
  if (editingId.value) {
    await projectApi.update(editingId.value, payload)
  } else {
    await projectApi.create(payload)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  await loadProjects()
}

async function removeProject(project: Project) {
  await ElMessageBox.confirm(`确认停用项目「${project.name}」？`, '确认操作')
  await projectApi.remove(project.id)
  if (projectStore.currentProjectId === project.id) {
    projectStore.clearCurrentProject()
  }
  ElMessage.success('已停用')
  await loadProjects()
}

function enterWorkspace(project: Project) {
  projectStore.setCurrentProject(project)
  router.push('/endpoints')
}

onMounted(loadProjects)
</script>
