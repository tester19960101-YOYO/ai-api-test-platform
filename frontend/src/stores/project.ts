import { defineStore } from 'pinia'

import type { Project } from '@/types'

const STORAGE_KEY = 'ai-api-test-platform-current-project'

export const useProjectStore = defineStore('project', {
  state: () => ({
    currentProjectId: Number(localStorage.getItem(STORAGE_KEY) || 0),
    currentProject: null as Project | null
  }),
  actions: {
    setCurrentProject(project: Project) {
      this.currentProject = project
      this.currentProjectId = project.id
      localStorage.setItem(STORAGE_KEY, String(project.id))
    },
    clearCurrentProject() {
      this.currentProject = null
      this.currentProjectId = 0
      localStorage.removeItem(STORAGE_KEY)
    }
  }
})
