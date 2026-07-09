import axios from 'axios'

// 🔧 开发时切换：true=用mock数据, false=连真实后端
const USE_MOCK = true

const apiClient = axios.create({
  baseURL: '', // 走 Vite 代理，避免跨域
  timeout: 30000,
})

// 管理端请求自动带 Token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 401 时自动跳转登录
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export { USE_MOCK }
export default apiClient
