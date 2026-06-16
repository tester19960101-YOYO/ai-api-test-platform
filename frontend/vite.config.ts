import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiBaseURL = env.VITE_APP_API_BASEURL || env.VITE_API_BASE_URL || '/api/v1'
  const proxyTarget = env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:8000'

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      port: 5173,
      proxy: apiBaseURL.startsWith('/api')
        ? {
            '/api/v1': {
              target: proxyTarget,
              changeOrigin: true
            }
          }
        : undefined
    }
  }
})
