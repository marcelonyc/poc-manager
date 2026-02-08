import axios from 'axios'

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }

    // Remove Content-Type for FormData to let axios set it with boundary
    if (config.data instanceof FormData) {
        delete config.headers['Content-Type']
    }

    return config
})

// Handle auth errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token')
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

// Demo Users API
export const demoUsersApi = {
    list: () => api.get('/demo/users'),
    block: (userId: number, isBlocked: boolean, reason?: string) =>
        api.post(`/demo/users/${userId}/block`, { is_blocked: isBlocked, reason }),
    upgrade: (userId: number) =>
        api.post(`/demo/users/${userId}/upgrade`, {}),
    resendEmail: (userId: number) =>
        api.post(`/demo/users/${userId}/resend-email`, {}),
}

export default api
