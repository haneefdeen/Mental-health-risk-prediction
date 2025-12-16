import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API endpoints
export const authAPI = {
  login: (data) => api.post('/api/auth/login', data),
  register: (data) => api.post('/api/auth/register', data),
  get: (url) => api.get(`/api/auth${url}`),
  post: (url, data) => api.post(`/api/auth${url}`, data),
}

export const analysisAPI = {
  analyzeText: (data) => api.post('/api/analysis/text', data),
  analyzeImage: (formData) => api.post('/api/analysis/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  analyzeMultimodal: (data) => api.post('/api/analysis/multimodal', data),
  getCopingGuide: (stressLevel) => api.get(`/api/analysis/coping-guide?stress_level=${stressLevel}`),
  getUserHistory: () => api.get('/api/analysis/user-history'),
}

export const reportAPI = {
  generatePDF: (data) => api.post('/api/reports/generate-pdf', data),
  exportData: (data) => api.post('/api/reports/export-data', data),
  deleteData: () => api.delete('/api/reports/delete-data'),
  getConsentInfo: () => api.get('/api/reports/data-consent'),
  updateConsent: (consent) => api.post('/api/reports/update-consent', { consent }),
}

export const adminAPI = {
  getSummary: () => api.get('/api/admin/summary'),
  getUsers: () => api.get('/api/admin/users'),
  getStressTrends: (days) => api.get(`/api/admin/stress-trends?days=${days}`),
  getFlaggedUsers: () => api.get('/api/admin/flagged-users'),
  exportData: () => api.get('/api/admin/export-data'),
  deleteUser: (userId) => api.delete(`/api/admin/user/${userId}`),
}

export default api