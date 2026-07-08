/**
 * 管理端 API 调用函数（B1-B17）
 * 所有请求需带 Authorization: Bearer <token>
 */
import apiClient, { USE_MOCK } from './index.js'
import {
  mockLogin,
  mockUpload,
  mockSaveDetection,
  mockGetDetections,
  mockGetDetectionById,
  mockDeleteDetection,
  mockGetLocations,
  mockCreateLocation,
  mockUpdateLocation,
  mockDeleteLocation,
  mockGetSafetyTips,
  mockCreateSafetyTip,
  mockUpdateSafetyTip,
  mockUpdateSafetyTipStatus,
  mockDeleteSafetyTip,
  mockGetSuggestions,
  mockGetAdminDashboard,
  mockGetWeeklyReport,
  mockGetMonthlyReport,
} from './mock.js'

// ---- 鉴权 ----
// A1. POST /api/auth/login
export function login(username, password) {
  if (USE_MOCK) return mockLogin(username, password)
  return apiClient.post('/api/auth/login', { username, password }).then((r) => r.data)
}

// ---- 管理端 ----
// B1. POST /api/upload
export function uploadImage(file, locationId) {
  if (USE_MOCK) return mockUpload(file, locationId)
  const fd = new FormData()
  fd.append('file', file)
  fd.append('location_id', locationId)
  return apiClient.post('/api/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data)
}

// B2. POST /api/detections
export function saveDetection(data) {
  if (USE_MOCK) return mockSaveDetection(data)
  return apiClient.post('/api/detections', data).then((r) => r.data)
}

// B3. GET /api/detections
export function getDetections(params = {}) {
  if (USE_MOCK) return mockGetDetections(params)
  return apiClient.get('/api/detections', { params }).then((r) => r.data)
}

// B4. GET /api/detections/{id}
export function getDetectionById(id) {
  if (USE_MOCK) return mockGetDetectionById(id)
  return apiClient.get(`/api/detections/${id}`).then((r) => r.data)
}

// B5. DELETE /api/detections/{id}
export function deleteDetection(id) {
  if (USE_MOCK) return mockDeleteDetection(id)
  return apiClient.delete(`/api/detections/${id}`).then((r) => r.data)
}

// B6. GET /api/locations
export function getLocations() {
  if (USE_MOCK) return mockGetLocations()
  return apiClient.get('/api/locations').then((r) => r.data)
}

// B7. POST /api/locations
export function createLocation(data) {
  if (USE_MOCK) return mockCreateLocation(data)
  return apiClient.post('/api/locations', data).then((r) => r.data)
}

// B8. PUT /api/locations/{id}
export function updateLocation(id, data) {
  if (USE_MOCK) return mockUpdateLocation(id, data)
  return apiClient.put(`/api/locations/${id}`, data).then((r) => r.data)
}

// B9. DELETE /api/locations/{id}
export function deleteLocation(id) {
  if (USE_MOCK) return mockDeleteLocation(id)
  return apiClient.delete(`/api/locations/${id}`).then((r) => r.data)
}

// B10. GET /api/safety-tips
export function getSafetyTips() {
  if (USE_MOCK) return mockGetSafetyTips()
  return apiClient.get('/api/safety-tips').then((r) => r.data)
}

// B11. POST /api/safety-tips
export function createSafetyTip(data) {
  if (USE_MOCK) return mockCreateSafetyTip(data)
  return apiClient.post('/api/safety-tips', data).then((r) => r.data)
}

// B12. PUT /api/safety-tips/{id}
export function updateSafetyTip(id, data) {
  if (USE_MOCK) return mockUpdateSafetyTip(id, data)
  return apiClient.put(`/api/safety-tips/${id}`, data).then((r) => r.data)
}

// B13. PUT /api/safety-tips/{id}/status
// B13.5 DELETE /api/safety-tips/{id}
export function deleteSafetyTip(id) {
  if (USE_MOCK) return mockDeleteSafetyTip(id)
  return apiClient.delete(`/api/safety-tips/${id}`).then((r) => r.data)
}

export function updateSafetyTipStatus(id, status) {
  if (USE_MOCK) return mockUpdateSafetyTipStatus(id, status)
  return apiClient.put(`/api/safety-tips/${id}/status`, { status }).then((r) => r.data)
}

// B14. GET /api/safety-tips/suggestions
export function getSuggestions() {
  if (USE_MOCK) return mockGetSuggestions()
  return apiClient.get('/api/safety-tips/suggestions').then((r) => r.data)
}

// B15. GET /api/dashboard
export function getAdminDashboard() {
  if (USE_MOCK) return mockGetAdminDashboard()
  return apiClient.get('/api/dashboard').then((r) => r.data)
}

// B16. GET /api/reports/weekly
export function getWeeklyReport(params = {}) {
  if (USE_MOCK) return mockGetWeeklyReport(params)
  return apiClient.get('/api/reports/weekly', { params, responseType: params.format === 'csv' ? 'text' : 'json' }).then((r) => r.data)
}

// B17. GET /api/reports/monthly
export function getMonthlyReport(params = {}) {
  if (USE_MOCK) return mockGetMonthlyReport(params)
  return apiClient.get('/api/reports/monthly', { params, responseType: params.format === 'csv' ? 'text' : 'json' }).then((r) => r.data)
}
