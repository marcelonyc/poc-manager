import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
    id: number
    email: string
    full_name: string
    role: string
    tenant_id: number | null
}

interface AuthState {
    user: User | null
    token: string | null
    isAuthenticated: boolean
    login: (token: string, user: User) => void
    logout: () => void
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            login: (token, user) => {
                localStorage.setItem('access_token', token)
                set({ token, user, isAuthenticated: true })
            },
            logout: () => {
                localStorage.removeItem('access_token')
                set({ token: null, user: null, isAuthenticated: false })
            },
        }),
        {
            name: 'auth-storage',
            onRehydrateStorage: () => (state) => {
                // After rehydration, update isAuthenticated based on token presence
                if (state && state.token) {
                    state.isAuthenticated = true
                }
            },
        }
    )
)
