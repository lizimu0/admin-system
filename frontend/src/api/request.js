import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

// 可通过 .env 的 VITE_API_BASE 覆盖(生产部署时指向后端地址),开发默认走 Vite 代理
const BASE_URL = import.meta.env.VITE_API_BASE || ''

const request = axios.create({
  baseURL: `${BASE_URL}/api`,
  timeout: 15000
})

// 请求拦截:自动携带 token
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截:统一处理错误与 401
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail

    if (status === 401) {
      localStorage.removeItem('token')
      ElMessage.error('登录已过期,请重新登录')
      router.push('/login')
    } else {
      const msg = typeof detail === 'string' ? detail : '请求失败,请稍后重试'
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  }
)

/**
 * 下载文件(处理后端返回的 Blob + Content-Disposition 文件名)
 */
export function downloadFile(url, params, fallbackName = 'download.xlsx') {
  return axios({
    url: `${BASE_URL}/api${url}`,
    method: 'GET',
    params,
    responseType: 'blob',
    headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` }
  }).then((response) => {
    // 优先从 Content-Disposition 解析文件名
    const disposition = response.headers['content-disposition'] || ''
    const match = disposition.match(/filename\*=UTF-8''([^;]+)/)
    let name = fallbackName
    if (match) {
      try {
        name = decodeURIComponent(match[1])
      } catch {
        name = fallbackName
      }
    }
    const blob = new Blob([response.data])
    const objectUrl = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = objectUrl
    link.download = name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(objectUrl)
  })
}

export default request
