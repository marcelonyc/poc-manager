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
    _hasHydrated: boolean
    setHasHydrated: (hydrated: boolean) => void
    login: (token: string, user: User) => void
    logout: () => void
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            _hasHydrated: false,
            setHasHydrated: (hydrated) => set({ _hasHydrated: hydrated }),
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
            onRehydrateStorage: () => (state, error) => {
                if (!error && state) {
                    // Set isAuthenticated based on token presence after rehydration
                    const hasToken = !!state.token
                    if (hasToken !== state.isAuthenticated) {
                        state.isAuthenticated = hasToken
                    }
                    state._hasHydrated = true
                }
            },
        }
    )
)
