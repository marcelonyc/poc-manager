import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import toast from 'react-hot-toast'

interface Tenant {
    id: number
    name: string
    slug: string
    logo_url?: string
    primary_color: string
    secondary_color: string
    contact_email?: string
    contact_phone?: string
    is_active: boolean
    created_at: string
    tenant_admin_limit: number
    administrator_limit: number
    sales_engineer_limit: number
    account_executive_limit: number
    customer_limit: number
}

interface TenantFormData {
    name: string
    slug: string
    primary_color: string
    secondary_color: string
    contact_email: string
    contact_phone: string
    initial_admin_email: string
    initial_admin_name: string
    initial_admin_password: string
    tenant_admin_limit: number
    administrator_limit: number
    sales_engineer_limit: number
    account_executive_limit: number
    customer_limit: number
}

interface TenantUpdateData {
    name: string
    primary_color: string
    secondary_color: string
    contact_email: string
    contact_phone: string
    tenant_admin_limit: number
    administrator_limit: number
    sales_engineer_limit: number
    account_executive_limit: number
    customer_limit: number
}

export default function Tenants() {
    const [tenants, setTenants] = useState<Tenant[]>([])
    const [loading, setLoading] = useState(true)
    const [showCreateForm, setShowCreateForm] = useState(false)
    const [editingTenant, setEditingTenant] = useState<Tenant | null>(null)
    const [updateData, setUpdateData] = useState<TenantUpdateData | null>(null)
    const [formData, setFormData] = useState<TenantFormData>({
        name: '',
        slug: '',
        primary_color: '#0066cc',
        secondary_color: '#333333',
        contact_email: '',
        contact_phone: '',
        initial_admin_email: '',
        initial_admin_name: '',
        initial_admin_password: '',
        tenant_admin_limit: 5,
        administrator_limit: 10,
        sales_engineer_limit: 50,
        account_executive_limit: 50,
        customer_limit: 500,
    })
    const [submitting, setSubmitting] = useState(false)

    useEffect(() => {
        fetchTenants()
    }, [])

    const fetchTenants = async () => {
        try {
            const response = await api.get('/tenants/')
            setTenants(response.data)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to fetch tenants')
        } finally {
            setLoading(false)
        }
    }

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, type } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: type === 'number' ? parseInt(value) || 0 : value
        }))

        // Auto-generate slug from name
        if (name === 'name') {
            const slug = value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
            setFormData(prev => ({ ...prev, slug }))
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setSubmitting(true)

        try {
            await api.post('/tenants/', formData)
            toast.success('Tenant created successfully!')
            setShowCreateForm(false)
            setFormData({
                name: '',
                slug: '',
                primary_color: '#0066cc',
                secondary_color: '#333333',
                contact_email: '',
                contact_phone: '',
                initial_admin_email: '',
                initial_admin_name: '',
                initial_admin_password: '',
                tenant_admin_limit: 5,
                administrator_limit: 10,
                sales_engineer_limit: 50,
                account_executive_limit: 50,
                customer_limit: 500,
            })
            fetchTenants()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to create tenant')
        } finally {
            setSubmitting(false)
        }
    }

    const toggleTenantStatus = async (tenantId: number, currentStatus: boolean) => {
        try {
            await api.put(`/tenants/${tenantId}`, { is_active: !currentStatus })
            toast.success(`Tenant ${!currentStatus ? 'activated' : 'deactivated'}`)
            fetchTenants()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to update tenant')
        }
    }

    const handleEdit = (tenant: Tenant) => {
        setEditingTenant(tenant)
        setUpdateData({
            name: tenant.name,
            primary_color: tenant.primary_color,
            secondary_color: tenant.secondary_color,
            contact_email: tenant.contact_email || '',
            contact_phone: tenant.contact_phone || '',
            tenant_admin_limit: tenant.tenant_admin_limit,
            administrator_limit: tenant.administrator_limit,
            sales_engineer_limit: tenant.sales_engineer_limit,
            account_executive_limit: tenant.account_executive_limit,
            customer_limit: tenant.customer_limit,
        })
    }

    const handleUpdateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, type } = e.target
        setUpdateData(prev => prev ? {
            ...prev,
            [name]: type === 'number' ? parseInt(value) || 0 : value
        } : null)
    }

    const handleUpdate = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!editingTenant || !updateData) return

        setSubmitting(true)
        try {
            await api.put(`/tenants/${editingTenant.id}`, updateData)
            toast.success('Tenant updated successfully!')
            setEditingTenant(null)
            setUpdateData(null)
            fetchTenants()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to update tenant')
        } finally {
            setSubmitting(false)
        }
    }

    const closeEditModal = () => {
        setEditingTenant(null)
        setUpdateData(null)
    }

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="text-gray-500">Loading tenants...</div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-900">Tenants</h1>
                <button
                    onClick={() => setShowCreateForm(!showCreateForm)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                    {showCreateForm ? 'Cancel' : '+ New Tenant'}
                </button>
            </div>

            {showCreateForm && (
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h2 className="text-xl font-semibold mb-4">Create New Tenant</h2>
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Basic Information */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Company Name *
                                </label>
                                <input
                                    type="text"
                                    name="name"
                                    required
                                    value={formData.name}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="Acme Corporation"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Slug *
                                </label>
                                <input
                                    type="text"
                                    name="slug"
                                    required
                                    value={formData.slug}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="acme-corporation"
                                />
                                <p className="text-xs text-gray-500 mt-1">URL-friendly identifier (auto-generated)</p>
                            </div>
                        </div>

                        {/* Contact Information */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Contact Email
                                </label>
                                <input
                                    type="email"
                                    name="contact_email"
                                    value={formData.contact_email}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="contact@acme.com"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Contact Phone
                                </label>
                                <input
                                    type="tel"
                                    name="contact_phone"
                                    value={formData.contact_phone}
                                    onChange={handleInputChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="+1 (555) 123-4567"
                                />
                            </div>
                        </div>

                        {/* Branding */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Primary Color
                                </label>
                                <div className="flex gap-2">
                                    <input
                                        type="color"
                                        name="primary_color"
                                        value={formData.primary_color}
                                        onChange={handleInputChange}
                                        className="h-10 w-20 border border-gray-300 rounded cursor-pointer"
                                    />
                                    <input
                                        type="text"
                                        value={formData.primary_color}
                                        onChange={(e) => setFormData(prev => ({ ...prev, primary_color: e.target.value }))}
                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Secondary Color
                                </label>
                                <div className="flex gap-2">
                                    <input
                                        type="color"
                                        name="secondary_color"
                                        value={formData.secondary_color}
                                        onChange={handleInputChange}
                                        className="h-10 w-20 border border-gray-300 rounded cursor-pointer"
                                    />
                                    <input
                                        type="text"
                                        value={formData.secondary_color}
                                        onChange={(e) => setFormData(prev => ({ ...prev, secondary_color: e.target.value }))}
                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Initial Admin */}
                        <div className="border-t pt-4">
                            <h3 className="text-lg font-medium text-gray-900 mb-3">Initial Tenant Admin</h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Admin Name *
                                    </label>
                                    <input
                                        type="text"
                                        name="initial_admin_name"
                                        required
                                        value={formData.initial_admin_name}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="John Doe"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Admin Email *
                                    </label>
                                    <input
                                        type="email"
                                        name="initial_admin_email"
                                        required
                                        value={formData.initial_admin_email}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="admin@acme.com"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Initial Password *
                                    </label>
                                    <input
                                        type="password"
                                        name="initial_admin_password"
                                        required
                                        value={formData.initial_admin_password}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="••••••••"
                                        minLength={8}
                                    />
                                </div>
                            </div>
                        </div>

                        {/* User Limits */}
                        <div className="border-t pt-4">
                            <h3 className="text-lg font-medium text-gray-900 mb-3">User Limits</h3>
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Tenant Admins
                                    </label>
                                    <input
                                        type="number"
                                        name="tenant_admin_limit"
                                        min="1"
                                        value={formData.tenant_admin_limit}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Administrators
                                    </label>
                                    <input
                                        type="number"
                                        name="administrator_limit"
                                        min="1"
                                        value={formData.administrator_limit}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Sales Engineers
                                    </label>
                                    <input
                                        type="number"
                                        name="sales_engineer_limit"
                                        min="1"
                                        value={formData.sales_engineer_limit}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Account Executives
                                    </label>
                                    <input
                                        type="number"
                                        name="account_executive_limit"
                                        min="1"
                                        value={formData.account_executive_limit}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Customers
                                    </label>
                                    <input
                                        type="number"
                                        name="customer_limit"
                                        min="1"
                                        value={formData.customer_limit}
                                        onChange={handleInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-end gap-3">
                            <button
                                type="button"
                                onClick={() => setShowCreateForm(false)}
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
                                {submitting ? 'Creating...' : 'Create Tenant'}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Tenants List */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Tenant
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Contact
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                User Limits
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Status
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Created
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {tenants.length === 0 ? (
                            <tr>
                                <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                                    No tenants found. Create your first tenant!
                                </td>
                            </tr>
                        ) : (
                            tenants.map((tenant) => (
                                <tr key={tenant.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <div
                                                className="h-10 w-10 rounded-lg flex items-center justify-center text-white font-bold"
                                                style={{ backgroundColor: tenant.primary_color }}
                                            >
                                                {tenant.name.charAt(0)}
                                            </div>
                                            <div className="ml-4">
                                                <div className="text-sm font-medium text-gray-900">{tenant.name}</div>
                                                <div className="text-sm text-gray-500">{tenant.slug}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-900">{tenant.contact_email || '-'}</div>
                                        <div className="text-sm text-gray-500">{tenant.contact_phone || '-'}</div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        <div>Admins: {tenant.tenant_admin_limit}</div>
                                        <div>Managers: {tenant.administrator_limit}</div>
                                        <div>Sales: {tenant.sales_engineer_limit}</div>
                                        <div>AE: {tenant.account_executive_limit}</div>
                                        <div>Customers: {tenant.customer_limit}</div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span
                                            className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${tenant.is_active
                                                ? 'bg-green-100 text-green-800'
                                                : 'bg-red-100 text-red-800'
                                                }`}
                                        >
                                            {tenant.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {new Date(tenant.created_at).toLocaleDateString()}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <button
                                            onClick={() => handleEdit(tenant)}
                                            className="text-blue-600 hover:text-blue-900 mr-4"
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={() => toggleTenantStatus(tenant.id, tenant.is_active)}
                                            className={`${tenant.is_active
                                                ? 'text-red-600 hover:text-red-900'
                                                : 'text-green-600 hover:text-green-900'
                                                }`}
                                        >
                                            {tenant.is_active ? 'Deactivate' : 'Activate'}
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Edit Modal */}
            {editingTenant && updateData && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
                    <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
                            <h2 className="text-2xl font-bold text-gray-900">Edit Tenant: {editingTenant.name}</h2>
                            <button
                                onClick={closeEditModal}
                                className="text-gray-400 hover:text-gray-500"
                            >
                                <span className="text-2xl">&times;</span>
                            </button>
                        </div>

                        <form onSubmit={handleUpdate} className="p-6 space-y-6">
                            {/* Basic Information */}
                            <div>
                                <h3 className="text-lg font-medium text-gray-900 mb-3">Basic Information</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Company Name *
                                        </label>
                                        <input
                                            type="text"
                                            name="name"
                                            required
                                            value={updateData.name}
                                            onChange={handleUpdateChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Slug (read-only)
                                        </label>
                                        <input
                                            type="text"
                                            value={editingTenant.slug}
                                            disabled
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-500"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Contact Information */}
                            <div>
                                <h3 className="text-lg font-medium text-gray-900 mb-3">Contact Information</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Contact Email
                                        </label>
                                        <input
                                            type="email"
                                            name="contact_email"
                                            value={updateData.contact_email}
                                            onChange={handleUpdateChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Contact Phone
                                        </label>
                                        <input
                                            type="tel"
                                            name="contact_phone"
                                            value={updateData.contact_phone}
                                            onChange={handleUpdateChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Branding */}
                            <div>
                                <h3 className="text-lg font-medium text-gray-900 mb-3">Branding</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Primary Color
                                        </label>
                                        <div className="flex gap-2">
                                            <input
                                                type="color"
                                                name="primary_color"
                                                value={updateData.primary_color}
                                                onChange={handleUpdateChange}
                                                className="h-10 w-20 border border-gray-300 rounded cursor-pointer"
                                            />
                                            <input
                                                type="text"
                                                value={updateData.primary_color}
                                                onChange={(e) => setUpdateData({ ...updateData, primary_color: e.target.value })}
                                                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                            />
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Secondary Color
                                        </label>
                                        <div className="flex gap-2">
                                            <input
                                                type="color"
                                                name="secondary_color"
                                                value={updateData.secondary_color}
                                                onChange={handleUpdateChange}
                                                className="h-10 w-20 border border-gray-300 rounded cursor-pointer"
                                            />
                                            <input
                                                type="text"
                                                value={updateData.secondary_color}
                                                onChange={(e) => setUpdateData({ ...updateData, secondary_color: e.target.value })}
                                                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* User Limits */}
                            <div>
                                <h3 className="text-lg font-medium text-gray-900 mb-3">User Limits</h3>
                                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Tenant Admins
                                        </label>
                                        <input
                                            type="number"
                                            name="tenant_admin_limit"
                                            min="1"
                                            value={updateData.tenant_admin_limit}
                                            onChange={handleUpdateChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Administrators
                                        </label>
                                        <input
                                            type="number"
                                            name="administrator_limit"
                                            min="1"
                                            value={updateData.administrator_limit}
                                            onChange={handleUpdateChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Sales Engineers
                                        </label>
                                        <input
                                            type="number"
                                            name="sales_engineer_limit"
                                            min="1"
                                            value={updateData.sales_engineer_limit}
                                            onChange={handleUpdateChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Account Executives
                                        </label>
                                        <input
                                            type="number"
                                            name="account_executive_limit"
                                            min="1"
                                            value={updateData.account_executive_limit}
                                            onChange={handleUpdateChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Customers
                                        </label>
                                        <input
                                            type="number"
                                            name="customer_limit"
                                            min="1"
                                            value={updateData.customer_limit}
                                            onChange={handleUpdateChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="flex justify-end gap-3 pt-4 border-t">
                                <button
                                    type="button"
                                    onClick={closeEditModal}
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
                                    {submitting ? 'Updating...' : 'Update Tenant'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    )
}
