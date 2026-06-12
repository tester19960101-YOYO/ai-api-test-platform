import { createRouter, createWebHistory } from 'vue-router'

import AppLayout from '@/layouts/AppLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: AppLayout,
      redirect: '/projects',
      children: [
        {
          path: 'projects',
          name: 'projects',
          component: () => import('@/views/ProjectManagement.vue'),
          meta: { title: '项目管理' }
        },
        {
          path: 'environments',
          name: 'environments',
          component: () => import('@/views/EnvironmentConfig.vue'),
          meta: { title: '环境配置' }
        },
        {
          path: 'api-import',
          name: 'api-import',
          component: () => import('@/views/ApiImport.vue'),
          meta: { title: '接口导入' }
        },
        {
          path: 'endpoints',
          name: 'endpoints',
          component: () => import('@/views/EndpointList.vue'),
          meta: { title: '接口列表' }
        },
        {
          path: 'endpoints/:id',
          name: 'endpoint-detail',
          component: () => import('@/views/EndpointDetail.vue'),
          meta: { title: '接口详情' }
        },
        {
          path: 'ai-cases',
          name: 'ai-cases',
          component: () => import('@/views/AICaseGeneration.vue'),
          meta: { title: 'AI 用例生成' }
        },
        {
          path: 'test-cases',
          name: 'test-cases',
          component: () => import('@/views/TestCaseManagement.vue'),
          meta: { title: '测试用例' }
        },
        {
          path: 'reports',
          name: 'reports',
          component: () => import('@/views/ExecutionReport.vue'),
          meta: { title: '执行报告' }
        }
      ]
    }
  ]
})

export default router
