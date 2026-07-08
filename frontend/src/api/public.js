/**
 * 公共端 API 调用函数（C1-C9）
 * 无需鉴权
 */
import apiClient, { USE_MOCK } from './index.js'
import {
  mockGetPublicDashboard,
  mockGetBreedStats,
  mockGetCalendar,
  mockGetPublicDetections,
  mockGetRankings,
  mockGetGuide,
  mockGetPublicSafetyTips,
  mockGetShareCard,
  mockUploadCommunity,
  mockGetCommunity,
  mockAddComment,
} from './mock.js'

// C1. GET /api/public/dashboard
export function getPublicDashboard() {
  if (USE_MOCK) return mockGetPublicDashboard()
  return apiClient.get('/api/public/dashboard').then((r) => r.data)
}

// 品种检测统计（非标准接口，前端辅助数据）
export function getBreedStats() {
  if (USE_MOCK) return mockGetBreedStats()
  return apiClient.get('/api/public/breed-stats').then((r) => r.data)
}

// C2. GET /api/public/calendar
export function getCalendar(month) {
  if (USE_MOCK) return mockGetCalendar(month)
  return apiClient.get('/api/public/calendar', { params: { month } }).then((r) => r.data)
}

// C3. GET /api/public/detections
export function getPublicDetections(date) {
  if (USE_MOCK) return mockGetPublicDetections(date)
  return apiClient.get('/api/public/detections', { params: { date } }).then((r) => r.data)
}

// C4. GET /api/public/rankings
export function getRankings() {
  if (USE_MOCK) return mockGetRankings()
  return apiClient.get('/api/public/rankings').then((r) => r.data)
}

// C5. GET /api/public/guide
export function getGuide() {
  if (USE_MOCK) return mockGetGuide()
  return apiClient.get('/api/public/guide').then((r) => r.data)
}

// C6. GET /api/public/safety-tips
export function getPublicSafetyTips() {
  if (USE_MOCK) return mockGetPublicSafetyTips()
  return apiClient.get('/api/public/safety-tips').then((r) => r.data)
}

// C7. GET /api/public/share-card/{detection_id}
export function getShareCard(detectionId) {
  if (USE_MOCK) return mockGetShareCard(detectionId)
  return apiClient.get(`/api/public/share-card/${detectionId}`).then((r) => r.data)
}

// C8. POST /api/public/community
export function uploadCommunity(formData) {
  if (USE_MOCK) return mockUploadCommunity(formData)
  return apiClient.post('/api/public/community', formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data)
}

// C9. GET /api/public/community
export function getCommunity(params = {}) {
  if (USE_MOCK) return mockGetCommunity(params)
  return apiClient.get('/api/public/community', { params }).then((r) => r.data)
}

// 评论（非标准接口，前端辅助）
export function addComment(shareId, nickname, text) {
  if (USE_MOCK) return mockAddComment(shareId, nickname, text)
  return apiClient.post(`/api/public/community/${shareId}/comments`, { nickname, text }).then((r) => r.data)
}
