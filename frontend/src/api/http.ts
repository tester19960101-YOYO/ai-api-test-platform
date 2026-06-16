import axios from 'axios'
import { ElMessage } from 'element-plus'

import type { ApiResponse } from '@/types'

const baseURL = import.meta.env.VITE_APP_API_BASEURL || import.meta.env.VITE_API_BASE_URL || '/api/v1'

const http = axios.create({
  baseURL,
  timeout: 20000
})

http.interceptors.request.use((config) => {
  console.log('API BASE URL:', baseURL)
  console.log('REQUEST URL:', config.url)
  return config
})

http.interceptors.response.use(
  (response) => {
    console.log('RESPONSE STATUS:', response.status, response.config.url)
    const payload = response.data as ApiResponse<unknown>
    if (payload && typeof payload.code === 'number' && payload.code !== 0) {
      ElMessage.error(payload.message || '请求失败')
      return Promise.reject(new Error(payload.message || '请求失败'))
    }
    return response
  },
  (error) => {
    const message = error?.response?.data?.message || error?.message || '网络请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export async function request<T>(promise: Promise<{ data: ApiResponse<T> }>): Promise<T> {
  const response = await promise
  return response.data.data
}

export default http
