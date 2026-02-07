import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

interface User {
    id: number
    email: string
    full_name: string
    role: string
    is_active: boolean
    tenant_id: number | null
    created_at: string
    last_login: string | null
}

interface InviteFormData {
    email: string
    full_name: string
    role: string
}

export default function Users() {
    const { user: currentUser } = useAuthStore()
    const [users, setUsers] = useState<User[]>([])
    const [loading, setLoading] = useState(true)
    const [showInviteForm, setShowInviteForm] = useState(false)
    const [formData, setFormData] = useState<InviteFormData>({
        email: '',
        full_name: '',
        role: 'sales_engineer',
    })
    const [submitting, setSubmitting] = useState(false)

    useEffect(() => {
        fetchUsers()
    }, [])

    const fetchUsers = async () => {
        try {
            const response = await api.get('/users/')
            setUsers(response.data)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to fetch users')
        } finally {
            setLoading(false)
        }
    }

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: value
        }))
    }

    const handleInvite = async (e: React.FormEvent) => {
        e.preventDefault()
        setSubmitting(true)

        try {
            const response = await api.post('/users/invite', formData)
            toast.success(`User invited successfully! Temporary password: ${response.data.temporary_password}`)
            setShowInviteForm(false)
            setFormData({
                email: '',
                full_name: '',
                role: 'sales_engineer',
            })
            fetchUsers()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to invite user')
        } finally {
            setSubmitting(false)
        }
    }

    const toggleUserStatus = async (userId: number, currentStatus: boolean) => {
        try {
            if (currentStatus) {
                // Deactivate user - use DELETE endpoint
                await api.delete(`/users/${userId}`)
            } else {
                // Activate user - use POST reactivate endpoint
                await api.post(`/users/${userId}/reactivate`)
            }
            toast.success(`User ${!currentStatus ? 'activated' : 'deactivated'}`)
            fetchUsers()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to update user')
        }
    }

    const getRoleBadgeColor = (role: string) => {
        switch (role) {
            case 'platform_admin':
                return 'bg-purple-100 text-purple-800'
            case 'tenant_admin':
                return 'bg-blue-100 text-blue-800'
            case 'administrator':
                return 'bg-indigo-100 text-indigo-800'
            case 'sales_engineer':
                return 'bg-green-100 text-green-800'
            case 'customer':
                return 'bg-gray-100 text-gray-800'
            default:
                return 'bg-gray-100 text-gray-800'
        }
    }

    const getRoleDisplay = (role: string) => {
        return role.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
    }

    const getAvailableRoles = () => {
        if (currentUser?.role === 'platform_admin') {
            return [
                { value: 'platform_admin', label: 'Platform Admin' },
                { value: 'tenant_admin', label: 'Tenant Admin' },
                { value: 'administrator', label: 'Administrator' },
                { value: 'sales_engineer', label: 'Sales Engineer' },
                { value: 'customer', label: 'Customer' },
            ]
        } else if (currentUser?.role === 'tenant_admin') {
            return [
                { value: 'tenant_admin', label: 'Tenant Admin' },
                { value: 'administrator', label: 'Administrator' },
                { value: 'sales_engineer', label: 'Sales Engineer' },
                { value: 'customer', label: 'Customer' },
            ]
        } else if (currentUser?.role === 'administrator') {
            return [
                { value: 'sales_engineer', label: 'Sales Engineer' },
                { value: 'customer', label: 'Customer' },
            ]
        }
        return []
    }

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="text-gray-500">Loading users...</div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Team Members</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Manage users and invite new team members
                    </p>
                </div>
                <button
                    onClick={() => setShowInviteForm(!showInviteForm)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                    {showInviteForm ? 'Cancel' : '+ Invite User'}
                </button>
            </div>

            {showInviteForm && (
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h2 className="text-xl font-semibold mb-4">Invite New User</h2>
                    <form onSubmit={handleInvite} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Full Name *
                                </label>
                                <input
                                    type="text"
                                    name="full_name"
                                    required
                                    value={formData.full_name}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="John Doe"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Email Address *
                                </label>
                                <input
                                    type="email"
                                    name="email"
                                    required
                                    value={formData.email}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="john.doe@example.com"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Role *
                                </label>
                                <select
                                    name="role"
                                    required
                                    value={formData.role}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                >
                                    {getAvailableRoles().map((role) => (
                                        <option key={role.value} value={role.value}>
                                            {role.label}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                            <div className="flex">
                                <div className="flex-shrink-0">
                                    <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                    </svg>
                                </div>
                                <div className="ml-3">
                                    <h3 className="text-sm font-medium text-yellow-800">
                                        Temporary Password
                                    </h3>
                                    <div className="mt-2 text-sm text-yellow-700">
                                        <p>
                                            The invited user will receive a temporary password: <code className="font-mono font-bold">ChangeMe123!</code>
                                        </p>
                                        <p className="mt-1">They should change it immediately after first login.</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-end gap-3">
                            <button
                                type="button"
                                onClick={() => setShowInviteForm(false)}
                                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                                disabled={submitting}
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={submitting}
                                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-blue-400"
                            >
                                {submitting ? 'Sending Invite...' : 'Send Invite'}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Users List */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                User
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Role
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Status
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Last Login
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Joined
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {users.length === 0 ? (
                            <tr>
                                <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                                    No users found. Invite your first team member!
                                </td>
                            </tr>
                        ) : (
                            users.map((user) => (
                                <tr key={user.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
                                                {user.full_name.charAt(0).toUpperCase()}
                                            </div>
                                            <div className="ml-4">
                                                <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                                                <div className="text-sm text-gray-500">{user.email}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span
                                            className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getRoleBadgeColor(user.role)}`}
                                        >
                                            {getRoleDisplay(user.role)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span
                                            className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${user.is_active
                                                ? 'bg-green-100 text-green-800'
                                                : 'bg-red-100 text-red-800'
                                                }`}
                                        >
                                            {user.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {user.last_login
                                            ? new Date(user.last_login).toLocaleDateString()
                                            : 'Never'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {new Date(user.created_at).toLocaleDateString()}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        {user.id !== currentUser?.id && (
                                            <button
                                                onClick={() => toggleUserStatus(user.id, user.is_active)}
                                                className={`${user.is_active
                                                    ? 'text-red-600 hover:text-red-900'
                                                    : 'text-green-600 hover:text-green-900'
                                                    }`}
                                            >
                                                {user.is_active ? 'Deactivate' : 'Activate'}
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Statistics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white p-4 rounded-lg shadow">
                    <div className="text-sm text-gray-500">Total Users</div>
                    <div className="text-2xl font-bold text-gray-900">{users.length}</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                    <div className="text-sm text-gray-500">Active Users</div>
                    <div className="text-2xl font-bold text-green-600">
                        {users.filter(u => u.is_active).length}
                    </div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                    <div className="text-sm text-gray-500">Sales Engineers</div>
                    <div className="text-2xl font-bold text-blue-600">
                        {users.filter(u => u.role === 'sales_engineer').length}
                    </div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                    <div className="text-sm text-gray-500">Customers</div>
                    <div className="text-2xl font-bold text-purple-600">
                        {users.filter(u => u.role === 'customer').length}
                    </div>
                </div>
            </div>
        </div>
    )
}
