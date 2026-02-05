import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { useState, useEffect } from 'react'
import { api, API_URL } from '../lib/api'
import HelpBubble from './HelpBubble'

// Helper function to adjust color brightness
function adjustBrightness(color: string, amount: number): string {
    const hex = color.replace('#', '')
    const r = Math.max(0, Math.min(255, parseInt(hex.slice(0, 2), 16) + amount))
    const g = Math.max(0, Math.min(255, parseInt(hex.slice(2, 4), 16) + amount))
    const b = Math.max(0, Math.min(255, parseInt(hex.slice(4, 6), 16) + amount))
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
}

export default function Layout() {
    const { user, logout } = useAuthStore()
    const navigate = useNavigate()
    const [tenantLogoUrl, setTenantLogoUrl] = useState<string | null>(null)
    const [primaryColor, setPrimaryColor] = useState<string>('#0066cc')
    const [secondaryColor, setSecondaryColor] = useState<string>('#333333')

    useEffect(() => {
        // Fetch tenant logo if user has a tenant
        if (user?.tenant_id && user.role !== 'platform_admin') {
            fetchTenantLogo()
        }
    }, [user])

    const fetchTenantLogo = async () => {
        try {
            const response = await api.get(`/tenants/${user?.tenant_id}`)
            // Prepend API URL to relative logo path
            if (response.data.logo_url) {
                setTenantLogoUrl(`${API_URL}${response.data.logo_url}`)
            }
            // Load tenant colors
            if (response.data.primary_color) {
                setPrimaryColor(response.data.primary_color)
            }
            if (response.data.secondary_color) {
                setSecondaryColor(response.data.secondary_color)
            }
        } catch (err) {
            console.error('Failed to fetch tenant logo:', err)
        }
    }

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    return (
        <div className="min-h-screen bg-gray-100">
            {/* Apply tenant colors dynamically */}
            <style>{`
                :root {
                    --color-primary: ${primaryColor};
                    --color-secondary: ${secondaryColor};
                }
                .bg-primary-600 { background-color: ${primaryColor} !important; }
                .bg-primary-700 { background-color: ${adjustBrightness(primaryColor, -20)} !important; }
                .text-primary-600 { color: ${primaryColor} !important; }
                .text-primary-700 { color: ${adjustBrightness(primaryColor, -20)} !important; }
                .border-primary-600 { border-color: ${primaryColor} !important; }
                .hover\:bg-primary-700:hover { background-color: ${adjustBrightness(primaryColor, -20)} !important; }
                .focus\:ring-primary-500:focus { --tw-ring-color: ${primaryColor}; }
                .bg-blue-600 { background-color: ${primaryColor} !important; }
                .bg-blue-700 { background-color: ${adjustBrightness(primaryColor, -20)} !important; }
                .hover\:bg-blue-700:hover { background-color: ${adjustBrightness(primaryColor, -20)} !important; }
                .text-blue-600 { color: ${primaryColor} !important; }
                .text-blue-800 { color: ${adjustBrightness(primaryColor, -30)} !important; }
                .hover\:text-blue-800:hover { color: ${adjustBrightness(primaryColor, -30)} !important; }
                .border-blue-400 { border-color: ${adjustBrightness(primaryColor, 20)} !important; }
                .border-blue-300 { border-color: ${adjustBrightness(primaryColor, 40)} !important; }
                .focus\:ring-blue-500:focus { --tw-ring-color: ${primaryColor}; }
            `}</style>
            <nav className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex">
                            <div className="flex-shrink-0 flex items-center gap-3">
                                {tenantLogoUrl ? (
                                    <img
                                        src={tenantLogoUrl}
                                        alt="Tenant logo"
                                        className="h-10 w-auto object-contain"
                                    />
                                ) : (
                                    <h1 className="text-xl font-bold text-primary-600">POC Manager</h1>
                                )}
                            </div>
                            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                                {user?.role !== 'customer' && (
                                    <Link
                                        to="/"
                                        className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900"
                                    >
                                        Dashboard
                                    </Link>
                                )}
                                {user?.role === 'platform_admin' && (
                                    <>
                                        <Link
                                            to="/tenants"
                                            className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900"
                                        >
                                            Tenants
                                        </Link>
                                        <Link
                                            to="/invitations"
                                            className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900"
                                        >
                                            Invitations
                                        </Link>
                                        <Link
                                            to="/demo-requests"
                                            className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900"
                                        >
                                            Demo Requests
                                        </Link>
                                    </>
                                )}
                                {(user?.role === 'tenant_admin' || user?.role === 'administrator') && (
                                    <Link
                                        to="/users"
                                        className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900"
                                    >
                                        Users
                                    </Link>
                                )}
                                <Link
                                    to="/pocs"
                                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900"
                                >
                                    POCs
                                </Link>
                                {user?.role !== 'customer' && (
                                    <Link
                                        to="/templates"
                                        className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900"
                                    >
                                        Templates
                                    </Link>
                                )}
                                {(user?.role === 'tenant_admin' || user?.role === 'administrator') && (
                                    <Link
                                        to="/products"
                                        className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900"
                                    >
                                        Products
                                    </Link>
                                )}
                                {user?.role !== 'customer' && (
                                    <Link
                                        to="/settings"
                                        className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900"
                                    >
                                        Settings
                                    </Link>
                                )}
                            </div>
                        </div>
                        <div className="flex items-center">
                            <span className="text-sm text-gray-700 mr-4">
                                {user?.full_name} ({user?.role})
                            </span>
                            <button
                                onClick={handleLogout}
                                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
                            >
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <Outlet />
            </main>
        </div>
    )
}
