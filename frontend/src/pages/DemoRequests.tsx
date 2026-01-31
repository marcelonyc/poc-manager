import { useEffect, useState } from 'react'
import { demoUsersApi } from '../lib/api'

interface DemoUser {
    id: number
    name: string
    email: string
    company_name: string
    sales_engineers_count: number
    pocs_per_quarter: number
    is_verified: boolean
    is_completed: boolean
    tenant_id: number | null
    user_id: number | null
    tenant_name: string | null
    created_at: string
    verified_at: string | null
    completed_at: string | null
}

interface DemoUserList {
    total: number
    users: DemoUser[]
}

export default function DemoRequests() {
    const [users, setUsers] = useState<DemoUser[]>([])
    const [loading, setLoading] = useState(true)
    const [actionLoading, setActionLoading] = useState<number | null>(null)
    const [error, setError] = useState<string | null>(null)

    const fetchDemoUsers = async () => {
        try {
            setLoading(true)
            console.log('Fetching demo users...')
            const response = await demoUsersApi.list()
            console.log('Demo users response:', response)
            const data: DemoUserList = response.data
            console.log('Demo users data:', data)
            setUsers(data.users)
            setError(null)
        } catch (err: any) {
            console.error('Error fetching demo users:', err)
            console.error('Error response:', err.response)
            setError(err.response?.data?.detail || 'Failed to load demo users')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchDemoUsers()
    }, [])

    const handleBlock = async (userId: number, currentlyBlocked: boolean) => {
        if (!confirm(currentlyBlocked ? 'Unblock this user?' : 'Block this user?')) {
            return
        }

        try {
            setActionLoading(userId)
            await demoUsersApi.block(userId, !currentlyBlocked)
            await fetchDemoUsers()
        } catch (err: any) {
            alert(err.response?.data?.detail || 'Failed to update user status')
        } finally {
            setActionLoading(null)
        }
    }

    const handleUpgrade = async (userId: number) => {
        if (!confirm('Upgrade this demo account to a real account? This cannot be undone.')) {
            return
        }

        try {
            setActionLoading(userId)
            await demoUsersApi.upgrade(userId)
            await fetchDemoUsers()
            alert('Account upgraded successfully')
        } catch (err: any) {
            alert(err.response?.data?.detail || 'Failed to upgrade account')
        } finally {
            setActionLoading(null)
        }
    }

    const handleResendEmail = async (userId: number) => {
        try {
            setActionLoading(userId)
            await demoUsersApi.resendEmail(userId)
            alert('Email sent successfully')
        } catch (err: any) {
            alert(err.response?.data?.detail || 'Failed to send email')
        } finally {
            setActionLoading(null)
        }
    }

    const formatDate = (dateString: string | null) => {
        if (!dateString) return 'Never'
        return new Date(dateString).toLocaleString()
    }

    const getStatusBadge = (user: DemoUser) => {
        if (!user.is_verified) {
            return <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">Pending Verification</span>
        }
        if (!user.is_completed) {
            return <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">Verified - Setup Pending</span>
        }
        return <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Completed</span>
    }

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="text-gray-600">Loading demo users...</div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="space-y-4">
                <h1 className="text-3xl font-bold text-gray-900">Demo Requests</h1>
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800 font-semibold">Error loading demo users:</p>
                    <p className="text-red-600 mt-2">{error}</p>
                    <button
                        onClick={fetchDemoUsers}
                        className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                        Retry
                    </button>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold text-gray-900">Demo Requests</h1>
                <div className="text-sm text-gray-600">
                    Total: {users.length}
                </div>
            </div>

            {users.length === 0 ? (
                <div className="bg-white shadow rounded-lg p-8 text-center">
                    <p className="text-gray-600">No demo users found</p>
                    <button
                        onClick={fetchDemoUsers}
                        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                        Refresh
                    </button>
                    <div className="mt-4 text-xs text-gray-400">
                        <p>Check browser console for debug information</p>
                    </div>
                </div>
            ) : (
                <div className="bg-white shadow overflow-hidden rounded-lg">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Contact
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Company
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Status
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Requested
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Completed
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {users.map((user) => (
                                <tr key={user.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex flex-col">
                                            <div className="text-sm font-medium text-gray-900">
                                                {user.name}
                                            </div>
                                            <div className="text-sm text-gray-500">
                                                {user.email}
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        {user.company_name}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        {getStatusBadge(user)}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {formatDate(user.created_at)}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {formatDate(user.completed_at)}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <div className="flex space-x-2">
                                            {user.is_completed && (
                                                <button
                                                    onClick={() => handleUpgrade(user.id)}
                                                    disabled={actionLoading === user.id}
                                                    className="text-green-600 hover:text-green-900 disabled:opacity-50"
                                                    title="Upgrade to real account"
                                                >
                                                    Upgrade
                                                </button>
                                            )}
                                            <button
                                                onClick={() => handleResendEmail(user.id)}
                                                disabled={actionLoading === user.id}
                                                className="text-blue-600 hover:text-blue-900 disabled:opacity-50"
                                                title="Resend email"
                                            >
                                                Resend Email
                                            </button>
                                            {user.is_completed && (
                                                <button
                                                    onClick={() => handleBlock(user.id, false)}
                                                    disabled={actionLoading === user.id}
                                                    className="text-red-600 hover:text-red-900 disabled:opacity-50"
                                                    title="Block user"
                                                >
                                                    Block
                                                </button>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    )
}
