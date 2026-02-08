import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { api } from '../lib/api'

interface PlatformStats {
    active_tenants: number
    inactive_tenants: number
    total_users: number
    logos_uploaded: number
    recent_logins: number
}

interface TenantStats {
    active_pocs: number
    completed_pocs: number
    in_progress_pocs: number
    team_members: number
    customers: number
}

interface POC {
    id: number
    title: string
    description: string
    customer_company_name: string
    status: string
    start_date: string
    end_date: string
    created_at: string
}

export default function Dashboard() {
    const { user } = useAuthStore()
    const [platformStats, setPlatformStats] = useState<PlatformStats | null>(null)
    const [tenantStats, setTenantStats] = useState<TenantStats | null>(null)
    const [recentPOCs, setRecentPOCs] = useState<POC[]>([])
    const [allPOCs, setAllPOCs] = useState<POC[]>([])
    const [loading, setLoading] = useState(true)

    // Filters
    const [statusFilter, setStatusFilter] = useState('')
    const [customerFilter, setCustomerFilter] = useState('')
    const [userFilter, setUserFilter] = useState('')

    useEffect(() => {
        if (user?.role === 'platform_admin') {
            fetchPlatformStats()
        } else {
            fetchTenantStats()
            fetchRecentPOCs()
            fetchAllPOCs()
        }
    }, [user])

    useEffect(() => {
        if (user?.role !== 'platform_admin') {
            fetchAllPOCs()
        }
    }, [statusFilter, customerFilter, userFilter])

    const fetchPlatformStats = async () => {
        try {
            const response = await api.get('/tenants/stats/platform')
            setPlatformStats(response.data)
        } catch (error) {
            console.error('Failed to fetch platform stats:', error)
        } finally {
            setLoading(false)
        }
    }

    const fetchTenantStats = async () => {
        try {
            const response = await api.get('/pocs/stats/dashboard')
            setTenantStats(response.data)
        } catch (error) {
            console.error('Failed to fetch tenant stats:', error)
        } finally {
            setLoading(false)
        }
    }

    const fetchRecentPOCs = async () => {
        try {
            const response = await api.get('/pocs/', { params: { limit: 5 } })
            setRecentPOCs(response.data)
        } catch (error) {
            console.error('Failed to fetch recent POCs:', error)
        }
    }

    const fetchAllPOCs = async () => {
        try {
            const params: any = { limit: 100 }
            if (statusFilter) params.status = statusFilter
            if (customerFilter) params.customer_name = customerFilter
            if (userFilter) params.user_name = userFilter

            const response = await api.get('/pocs/', { params })
            setAllPOCs(response.data)
        } catch (error) {
            console.error('Failed to fetch POCs:', error)
        }
    }

    const getStatusBadgeClass = (status: string) => {
        const classes: Record<string, string> = {
            draft: 'bg-gray-100 text-gray-800',
            planning: 'bg-blue-100 text-blue-800',
            active: 'bg-green-100 text-green-800',
            completed: 'bg-purple-100 text-purple-800',
            archived: 'bg-red-100 text-red-800',
        }
        return classes[status.toLowerCase()] || 'bg-gray-100 text-gray-800'
    }

    if (user?.role === 'platform_admin') {
        if (loading) {
            return (
                <div className="px-4 py-6 sm:px-0">
                    <h1 className="text-3xl font-bold text-gray-900 mb-6">Platform Dashboard</h1>
                    <div className="text-center">Loading statistics...</div>
                </div>
            )
        }

        return (
            <div className="px-4 py-6 sm:px-0">
                <h1 className="text-3xl font-bold text-gray-900 mb-6">Platform Dashboard</h1>

                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-5">
                    <div className="bg-white overflow-hidden shadow rounded-lg">
                        <div className="p-5">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="rounded-md bg-green-500 p-3">
                                        <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                    </div>
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt className="text-sm font-medium text-gray-500 truncate">Active Tenants</dt>
                                        <dd className="text-3xl font-semibold text-gray-900">{platformStats?.active_tenants || 0}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white overflow-hidden shadow rounded-lg">
                        <div className="p-5">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="rounded-md bg-red-500 p-3">
                                        <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </div>
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt className="text-sm font-medium text-gray-500 truncate">Inactive Tenants</dt>
                                        <dd className="text-3xl font-semibold text-gray-900">{platformStats?.inactive_tenants || 0}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white overflow-hidden shadow rounded-lg">
                        <div className="p-5">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="rounded-md bg-blue-500 p-3">
                                        <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                                        </svg>
                                    </div>
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt className="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                                        <dd className="text-3xl font-semibold text-gray-900">{platformStats?.total_users || 0}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white overflow-hidden shadow rounded-lg">
                        <div className="p-5">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="rounded-md bg-purple-500 p-3">
                                        <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                        </svg>
                                    </div>
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt className="text-sm font-medium text-gray-500 truncate">Logos Uploaded</dt>
                                        <dd className="text-3xl font-semibold text-gray-900">{platformStats?.logos_uploaded || 0}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white overflow-hidden shadow rounded-lg">
                        <div className="p-5">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="rounded-md bg-yellow-500 p-3">
                                        <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                    </div>
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt className="text-sm font-medium text-gray-500 truncate">Recent Logins (24h)</dt>
                                        <dd className="text-3xl font-semibold text-gray-900">{platformStats?.recent_logins || 0}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="mt-8 bg-white shadow rounded-lg p-6">
                    <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                        <a
                            to="tenants"
                            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                        >
                            <svg className="h-6 w-6 text-indigo-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                            </svg>
                            <span className="text-sm font-medium text-gray-900">Manage Tenants</span>
                        </Link>
                        <a
                            to="invitations"
                            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                        >
                            <svg className="h-6 w-6 text-indigo-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                            <span className="text-sm font-medium text-gray-900">Platform Admin Invitations</span>
                        </Link>
                        <a
                            to="settings"
                            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                        >
                            <svg className="h-6 w-6 text-indigo-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                            <span className="text-sm font-medium text-gray-900">Platform Settings</span>
                        </Link>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="px-4 py-6 sm:px-0">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>

            {loading ? (
                <div className="text-center">Loading statistics...</div>
            ) : (
                <>
                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-5">
                        <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="p-5">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <div className="rounded-md bg-primary-500 p-3">
                                            <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                            </svg>
                                        </div>
                                    </div>
                                    <div className="ml-5 w-0 flex-1">
                                        <dl>
                                            <dt className="text-sm font-medium text-gray-500 truncate">Active POCs</dt>
                                            <dd className="text-3xl font-semibold text-gray-900">{tenantStats?.active_pocs || 0}</dd>
                                        </dl>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="p-5">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <div className="rounded-md bg-green-500 p-3">
                                            <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                        </div>
                                    </div>
                                    <div className="ml-5 w-0 flex-1">
                                        <dl>
                                            <dt className="text-sm font-medium text-gray-500 truncate">Completed</dt>
                                            <dd className="text-3xl font-semibold text-gray-900">{tenantStats?.completed_pocs || 0}</dd>
                                        </dl>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="p-5">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <div className="rounded-md bg-yellow-500 p-3">
                                            <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                        </div>
                                    </div>
                                    <div className="ml-5 w-0 flex-1">
                                        <dl>
                                            <dt className="text-sm font-medium text-gray-500 truncate">In Progress</dt>
                                            <dd className="text-3xl font-semibold text-gray-900">{tenantStats?.in_progress_pocs || 0}</dd>
                                        </dl>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="p-5">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <div className="rounded-md bg-purple-500 p-3">
                                            <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                                            </svg>
                                        </div>
                                    </div>
                                    <div className="ml-5 w-0 flex-1">
                                        <dl>
                                            <dt className="text-sm font-medium text-gray-500 truncate">Team Members</dt>
                                            <dd className="text-3xl font-semibold text-gray-900">{tenantStats?.team_members || 0}</dd>
                                        </dl>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="p-5">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <div className="rounded-md bg-indigo-500 p-3">
                                            <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                            </svg>
                                        </div>
                                    </div>
                                    <div className="ml-5 w-0 flex-1">
                                        <dl>
                                            <dt className="text-sm font-medium text-gray-500 truncate">Customers</dt>
                                            <dd className="text-3xl font-semibold text-gray-900">{tenantStats?.customers || 0}</dd>
                                        </dl>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="mt-8">
                        <h2 className="text-xl font-bold text-gray-900 mb-4">Recent POCs</h2>
                        <div className="bg-white shadow overflow-hidden sm:rounded-md">
                            {recentPOCs.length === 0 ? (
                                <div className="px-6 py-8 text-center text-gray-500">
                                    No POCs yet. Create your first POC to get started!
                                </div>
                            ) : (
                                <ul className="divide-y divide-gray-200">
                                    {recentPOCs.map((poc) => (
                                        <li key={poc.id} className="px-6 py-4 hover:bg-gray-50">
                                            <Link href={`/pocs/${poc.id}`} className="block">
                                                <div className="flex items-center justify-between">
                                                    <div>
                                                        <h3 className="text-lg font-medium text-gray-900">{poc.title}</h3>
                                                        <p className="text-sm text-gray-500">Customer: {poc.customer_company_name}</p>
                                                    </div>
                                                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeClass(poc.status)}`}>
                                                        {poc.status}
                                                    </span>
                                                </div>
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </div>

                    <div className="mt-8">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-bold text-gray-900">All POCs</h2>
                        </div>

                        {/* Filters */}
                        <div className="bg-white shadow rounded-lg p-4 mb-4">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                                    <select
                                        value={statusFilter}
                                        onChange={(e) => setStatusFilter(e.target.value)}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                    >
                                        <option value="">All Statuses</option>
                                        <option value="draft">Draft</option>
                                        <option value="planning">Planning</option>
                                        <option value="active">Active</option>
                                        <option value="completed">Completed</option>
                                        <option value="archived">Archived</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Customer Name</label>
                                    <input
                                        type="text"
                                        value={customerFilter}
                                        onChange={(e) => setCustomerFilter(e.target.value)}
                                        placeholder="Search by customer..."
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">User Name</label>
                                    <input
                                        type="text"
                                        value={userFilter}
                                        onChange={(e) => setUserFilter(e.target.value)}
                                        placeholder="Search by participant..."
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="bg-white shadow overflow-hidden sm:rounded-md">
                            {allPOCs.length === 0 ? (
                                <div className="px-6 py-8 text-center text-gray-500">
                                    No POCs found matching the filters.
                                </div>
                            ) : (
                                <ul className="divide-y divide-gray-200">
                                    {allPOCs.map((poc) => (
                                        <li key={poc.id} className="px-6 py-4 hover:bg-gray-50">
                                            <Link href={`/pocs/${poc.id}`} className="block">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex-1">
                                                        <div className="flex items-center justify-between">
                                                            <h3 className="text-lg font-medium text-gray-900">{poc.title}</h3>
                                                            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeClass(poc.status)}`}>
                                                                {poc.status}
                                                            </span>
                                                        </div>
                                                        <p className="text-sm text-gray-500 mt-1">Customer: {poc.customer_company_name}</p>
                                                        <p className="text-sm text-gray-400 mt-1">
                                                            {new Date(poc.start_date).toLocaleDateString()} - {new Date(poc.end_date).toLocaleDateString()}
                                                        </p>
                                                    </div>
                                                </div>
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </div>
                </>
            )}
        </div>
    )
}
