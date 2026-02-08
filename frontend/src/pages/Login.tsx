import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { api } from '../lib/api'
import toast from 'react-hot-toast'

export default function Login() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()
    const location = useLocation()
    const login = useAuthStore((state) => state.login)

    useEffect(() => {
        // Check for message from redirect (e.g., after accepting invitation)
        const state = location.state as { message?: string; email?: string }
        if (state?.message) {
            toast.success(state.message)
            if (state.email) {
                setEmail(state.email)
            }
            // Clear the state
            navigate(location.pathname, { replace: true, state: {} })
        }
    }, [location])

    const handleForgotPassword = () => {
        navigate('forgot-password')
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)

        try {
            const response = await api.post('/auth/login', { email, password })
            const data = response.data

            // Check if user is platform admin (token provided directly)
            if (data.access_token) {
                // Platform admin - token already provided
                const userResponse = await api.get('/auth/me', {
                    headers: { Authorization: `Bearer ${data.access_token}` }
                })

                login(data.access_token, {
                    id: userResponse.data.id,
                    email: userResponse.data.email,
                    full_name: userResponse.data.full_name,
                    role: userResponse.data.current_role || 'platform_admin',
                    tenant_id: null
                })
                toast.success('Login successful!')
                navigate('/')
            } else if (data.tenants && data.tenants.length > 0) {
                // Regular user - needs to select tenant
                if (data.requires_selection) {
                    // Multiple tenants - redirect to selection page
                    navigate('tenant-selection', {
                        state: {
                            tenants: data.tenants,
                            user: {
                                id: data.user_id,
                                email: data.email,
                                full_name: data.full_name
                            },
                            credentials: { email, password }
                        }
                    })
                } else {
                    // Single tenant - auto-select
                    const tenant = data.tenants[0]
                    const selectResponse = await api.post('/auth/select-tenant', {
                        tenant_id: tenant.tenant_id,
                        email: email,
                        password: password
                    })

                    login(selectResponse.data.access_token, {
                        id: selectResponse.data.user_id,
                        email: selectResponse.data.email,
                        full_name: selectResponse.data.full_name,
                        role: selectResponse.data.role,
                        tenant_id: selectResponse.data.tenant_id
                    })
                    toast.success('Login successful!')
                    navigate('/')
                }
            } else {
                toast.error('No tenant associations found')
            }
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Login failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div className="absolute top-4 right-4">
                    <button
                        onClick={() => navigate('demo/request')}
                        className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
                    >
                        Setup a test Account
                    </button>
                </div>

                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        POC Manager
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Sign in to your account
                    </p>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="rounded-md shadow-sm -space-y-px">
                        <div>
                            <label htmlFor="email" className="sr-only">
                                Email address
                            </label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-400 text-gray-900 bg-white rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                                placeholder="Email address"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                        <div>
                            <label htmlFor="password" className="sr-only">
                                Password
                            </label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-400 text-gray-900 bg-white rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                    </div>

                    <div className="flex items-center justify-end">
                        <div className="text-sm">
                            <button
                                type="button"
                                onClick={handleForgotPassword}
                                className="font-medium text-blue-600 hover:text-blue-700"
                            >
                                Forgot your password?
                            </button>
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                        >
                            {loading ? 'Signing in...' : 'Sign in'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
