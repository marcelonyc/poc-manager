import { useState, useEffect } from 'react'
import { api, API_URL } from '../lib/api'
import { useAuthStore } from '../store/authStore'

interface Tenant {
    id: number
    name: string
    slug: string
    primary_color: string
    secondary_color: string
    contact_email: string | null
    contact_phone: string | null
    has_custom_mail_config: boolean
    custom_mail_server: string | null
    custom_mail_port: number | null
    custom_mail_from: string | null
    custom_mail_tls: boolean | null
    logo_url: string | null
    is_demo: boolean
}

export default function TenantSettings() {
    const { user } = useAuthStore()
    const [tenant, setTenant] = useState<Tenant | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')
    const [saving, setSaving] = useState(false)

    // Email config form
    const [mailServer, setMailServer] = useState('')
    const [mailPort, setMailPort] = useState('587')
    const [mailUsername, setMailUsername] = useState('')
    const [mailPassword, setMailPassword] = useState('')
    const [mailFrom, setMailFrom] = useState('')
    const [mailTls, setMailTls] = useState(true)

    // Logo upload
    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)
    const [uploading, setUploading] = useState(false)

    // Branding colors
    const [primaryColor, setPrimaryColor] = useState('#0066cc')
    const [secondaryColor, setSecondaryColor] = useState('#333333')
    const [savingBranding, setSavingBranding] = useState(false)

    // Demo conversion
    const [conversionReason, setConversionReason] = useState('')
    const [requestingConversion, setRequestingConversion] = useState(false)

    // Test email
    const [testEmailAddress, setTestEmailAddress] = useState('')
    const [sendingTestEmail, setSendingTestEmail] = useState(false)

    useEffect(() => {
        if (user?.tenant_id) {
            fetchTenantSettings()
        }
    }, [user])

    const fetchTenantSettings = async () => {
        try {
            setLoading(true)
            const response = await api.get(`/tenants/${user?.tenant_id}`)
            const tenantData = response.data
            setTenant(tenantData)

            // Populate form if config exists
            if (tenantData.custom_mail_server) {
                setMailServer(tenantData.custom_mail_server)
                setMailPort(tenantData.custom_mail_port?.toString() || '587')
                setMailFrom(tenantData.custom_mail_from || '')
                setMailTls(tenantData.custom_mail_tls ?? true)
            }

            // Set branding colors
            setPrimaryColor(tenantData.primary_color || '#0066cc')
            setSecondaryColor(tenantData.secondary_color || '#333333')

            setError('')
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load tenant settings')
        } finally {
            setLoading(false)
        }
    }

    const handleSaveEmailConfig = async (e: React.FormEvent) => {
        e.preventDefault()
        setSaving(true)
        setError('')
        setSuccess('')

        try {
            await api.put(`/tenants/${user?.tenant_id}/email-config`, {
                custom_mail_server: mailServer,
                custom_mail_port: parseInt(mailPort),
                custom_mail_username: mailUsername,
                custom_mail_password: mailPassword || undefined,
                custom_mail_from: mailFrom,
                custom_mail_tls: mailTls,
            })
            setSuccess('Email configuration saved successfully')
            setMailPassword('') // Clear password field after save
            fetchTenantSettings()
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to save email configuration')
        } finally {
            setSaving(false)
        }
    }

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        // Validate file size (2MB max)
        if (file.size > 2 * 1024 * 1024) {
            setError('File size must be less than 2MB')
            return
        }

        // Validate file type
        const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if (!validTypes.includes(file.type)) {
            setError('File must be JPEG, PNG, GIF, or WebP')
            return
        }

        setSelectedFile(file)
        setError('')

        // Create preview
        const reader = new FileReader()
        reader.onloadend = () => {
            setPreviewUrl(reader.result as string)
        }
        reader.readAsDataURL(file)
    }

    const handleUploadLogo = async () => {
        if (!selectedFile) return

        setUploading(true)
        setError('')
        setSuccess('')

        try {
            const formData = new FormData()
            formData.append('logo', selectedFile)

            await api.post(`/tenants/${user?.tenant_id}/logo`, formData)

            setSuccess('Logo uploaded successfully')
            setSelectedFile(null)
            setPreviewUrl(null)
            fetchTenantSettings()
        } catch (err: any) {
            console.error('Logo upload error:', err.response?.data)
            // Handle FastAPI validation errors
            if (err.response?.data?.detail) {
                if (Array.isArray(err.response.data.detail)) {
                    const errorMsg = err.response.data.detail.map((e: any) => e.msg).join(', ')
                    setError(errorMsg)
                } else {
                    setError(err.response.data.detail)
                }
            } else {
                setError('Failed to upload logo')
            }
        } finally {
            setUploading(false)
        }
    }

    const handleDeleteLogo = async () => {
        if (!confirm('Are you sure you want to delete the logo?')) return

        setError('')
        setSuccess('')

        try {
            await api.delete(`/tenants/${user?.tenant_id}/logo`)
            setSuccess('Logo deleted successfully')
            fetchTenantSettings()
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to delete logo')
        }
    }

    const handleSaveBranding = async (e: React.FormEvent) => {
        e.preventDefault()
        setSavingBranding(true)
        setError('')
        setSuccess('')

        try {
            await api.put(`/tenants/${user?.tenant_id}`, {
                primary_color: primaryColor,
                secondary_color: secondaryColor,
            })
            setSuccess('Branding colors updated successfully')
            fetchTenantSettings()
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to update branding colors')
        } finally {
            setSavingBranding(false)
        }
    }

    const handleRequestConversion = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!confirm('Are you sure you want to request conversion from demo to full account?')) {
            return
        }

        setRequestingConversion(true)
        setError('')
        setSuccess('')

        try {
            await api.post('/demo/request-conversion', {
                reason: conversionReason || null
            })
            setSuccess('Conversion request submitted successfully! A platform administrator will review it.')
            setConversionReason('')
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to submit conversion request')
        } finally {
            setRequestingConversion(false)
        }
    }

    const handleSendTestEmail = async (e: React.FormEvent) => {
        e.preventDefault()
        setSendingTestEmail(true)
        setError('')
        setSuccess('')

        try {
            const response = await api.post(`/tenants/${user?.tenant_id}/test-email`, {
                recipient_email: testEmailAddress
            })
            setSuccess(response.data.message || 'Test email sent successfully!')
            setTestEmailAddress('')
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to send test email')
        } finally {
            setSendingTestEmail(false)
        }
    }

    if (user?.role === 'platform_admin') {
        return (
            <div className="p-6">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-yellow-800">
                        Platform Admins don't have tenant-specific settings. Use the Tenants page to manage tenants.
                    </p>
                </div>
            </div>
        )
    }

    if (user?.role !== 'tenant_admin') {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800">Access denied. Only Tenant Admins can access these settings.</p>
                </div>
            </div>
        )
    }

    if (loading) {
        return (
            <div className="p-6">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading tenant settings...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="p-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">Tenant Settings</h1>

            {error && (
                <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800">{error}</p>
                </div>
            )}

            {success && (
                <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-green-800">{success}</p>
                </div>
            )}

            {tenant && (
                <div className="space-y-6">
                    {/* Tenant Info */}
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <h2 className="text-xl font-semibold mb-4">Tenant Information</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Name</label>
                                <p className="mt-1 text-gray-900">{tenant.name}</p>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Slug</label>
                                <p className="mt-1 text-gray-900">{tenant.slug}</p>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Contact Email</label>
                                <p className="mt-1 text-gray-900">{tenant.contact_email || 'Not set'}</p>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Contact Phone</label>
                                <p className="mt-1 text-gray-900">{tenant.contact_phone || 'Not set'}</p>
                            </div>
                        </div>
                    </div>

                    {/* Branding Colors */}
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <h2 className="text-xl font-semibold mb-4">Branding Colors</h2>
                        <p className="text-sm text-gray-600 mb-4">
                            Customize your tenant's theme colors. These colors will be applied throughout the application.
                        </p>
                        <form onSubmit={handleSaveBranding} className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Primary Color
                                    </label>
                                    <div className="flex items-center gap-3">
                                        <input
                                            type="color"
                                            value={primaryColor}
                                            onChange={(e) => setPrimaryColor(e.target.value)}
                                            className="h-12 w-20 border border-gray-300 rounded cursor-pointer"
                                        />
                                        <input
                                            type="text"
                                            value={primaryColor}
                                            onChange={(e) => setPrimaryColor(e.target.value)}
                                            pattern="^#[0-9A-Fa-f]{6}$"
                                            placeholder="#0066cc"
                                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
                                        />
                                    </div>
                                    <p className="text-xs text-gray-500 mt-1">Used for buttons, links, and accents</p>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Secondary Color
                                    </label>
                                    <div className="flex items-center gap-3">
                                        <input
                                            type="color"
                                            value={secondaryColor}
                                            onChange={(e) => setSecondaryColor(e.target.value)}
                                            className="h-12 w-20 border border-gray-300 rounded cursor-pointer"
                                        />
                                        <input
                                            type="text"
                                            value={secondaryColor}
                                            onChange={(e) => setSecondaryColor(e.target.value)}
                                            pattern="^#[0-9A-Fa-f]{6}$"
                                            placeholder="#333333"
                                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
                                        />
                                    </div>
                                    <p className="text-xs text-gray-500 mt-1">Used for text and secondary elements</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-4 pt-4">
                                <button
                                    type="submit"
                                    disabled={savingBranding}
                                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                                    style={{ backgroundColor: primaryColor }}
                                >
                                    {savingBranding ? 'Saving...' : 'Save Branding'}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => {
                                        setPrimaryColor('#0066cc')
                                        setSecondaryColor('#333333')
                                    }}
                                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                >
                                    Reset to Default
                                </button>
                            </div>
                        </form>
                    </div>

                    {/* Logo Upload */}
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <h2 className="text-xl font-semibold mb-4">Tenant Logo</h2>
                        <p className="text-gray-600 mb-6">
                            Upload a logo to personalize your tenant. The logo will appear in the navigation bar.
                            Maximum file size: 2MB. Supported formats: JPEG, PNG, GIF, WebP.
                        </p>

                        <div className="space-y-4">
                            {/* Current Logo */}
                            {tenant.logo_url && !previewUrl && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Current Logo
                                    </label>
                                    <div className="flex items-center gap-4">
                                        <img
                                            src={`${API_URL}${tenant.logo_url}`}
                                            alt="Tenant logo"
                                            className="h-16 w-auto object-contain border border-gray-200 rounded p-2"
                                        />
                                        <button
                                            onClick={handleDeleteLogo}
                                            className="text-red-600 hover:text-red-700 text-sm font-medium"
                                        >
                                            Delete Logo
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* File Input */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    {tenant.logo_url ? 'Upload New Logo' : 'Upload Logo'}
                                </label>
                                <input
                                    type="file"
                                    accept="image/jpeg,image/png,image/gif,image/webp"
                                    onChange={handleFileSelect}
                                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                                />
                            </div>

                            {/* Preview */}
                            {previewUrl && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Preview
                                    </label>
                                    <div className="flex items-center gap-4">
                                        <img
                                            src={previewUrl}
                                            alt="Logo preview"
                                            className="h-16 w-auto object-contain border border-gray-200 rounded p-2"
                                        />
                                        <button
                                            onClick={handleUploadLogo}
                                            disabled={uploading}
                                            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400"
                                        >
                                            {uploading ? 'Uploading...' : 'Upload'}
                                        </button>
                                        <button
                                            onClick={() => {
                                                setSelectedFile(null)
                                                setPreviewUrl(null)
                                            }}
                                            className="text-gray-600 hover:text-gray-700 text-sm"
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Email Configuration */}
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-semibold">Email Configuration</h2>
                            {tenant.has_custom_mail_config && (
                                <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                                    Configured
                                </span>
                            )}
                        </div>

                        <p className="text-gray-600 mb-6">
                            Configure your tenant's email server for sending notifications and invitations.
                            This is required for your tenant to send emails.
                        </p>

                        <form onSubmit={handleSaveEmailConfig} className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        SMTP Server *
                                    </label>
                                    <input
                                        type="text"
                                        value={mailServer}
                                        onChange={(e) => setMailServer(e.target.value)}
                                        required
                                        placeholder="smtp.gmail.com"
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Port *
                                    </label>
                                    <input
                                        type="number"
                                        value={mailPort}
                                        onChange={(e) => setMailPort(e.target.value)}
                                        required
                                        placeholder="587"
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Username *
                                </label>
                                <input
                                    type="text"
                                    value={mailUsername}
                                    onChange={(e) => setMailUsername(e.target.value)}
                                    required
                                    placeholder="your-email@example.com"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Password {tenant.has_custom_mail_config && '(Leave blank to keep existing)'}
                                </label>
                                <input
                                    type="password"
                                    value={mailPassword}
                                    onChange={(e) => setMailPassword(e.target.value)}
                                    required={!tenant.has_custom_mail_config}
                                    placeholder="••••••••"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    From Email *
                                </label>
                                <input
                                    type="email"
                                    value={mailFrom}
                                    onChange={(e) => setMailFrom(e.target.value)}
                                    required
                                    placeholder="noreply@yourdomain.com"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                />
                            </div>

                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    id="mailTls"
                                    checked={mailTls}
                                    onChange={(e) => setMailTls(e.target.checked)}
                                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                                />
                                <label htmlFor="mailTls" className="ml-2 block text-sm text-gray-700">
                                    Use TLS/STARTTLS (Recommended)
                                </label>
                            </div>

                            <div className="pt-4 border-t">
                                <button
                                    type="submit"
                                    disabled={saving}
                                    className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400"
                                >
                                    {saving ? 'Saving...' : 'Save Email Configuration'}
                                </button>
                            </div>
                        </form>

                        {/* Test Email Section */}
                        {tenant.has_custom_mail_config && (
                            <div className="mt-6 pt-6 border-t">
                                <h3 className="text-lg font-semibold mb-4">Test Email Configuration</h3>
                                <p className="text-sm text-gray-600 mb-4">
                                    Send a test email to verify your SMTP configuration is working correctly.
                                </p>
                                <form onSubmit={handleSendTestEmail} className="flex items-end gap-4">
                                    <div className="flex-1">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Recipient Email
                                        </label>
                                        <input
                                            type="email"
                                            value={testEmailAddress}
                                            onChange={(e) => setTestEmailAddress(e.target.value)}
                                            required
                                            placeholder="test@example.com"
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                        />
                                    </div>
                                    <button
                                        type="submit"
                                        disabled={sendingTestEmail}
                                        className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 whitespace-nowrap"
                                    >
                                        {sendingTestEmail ? 'Sending...' : 'Send Test Email'}
                                    </button>
                                </form>
                            </div>
                        )}
                    </div>

                    {/* Demo Account Conversion Section */}
                    {tenant?.is_demo && (
                        <div className="bg-white rounded-lg shadow p-6 mb-6">
                            <h2 className="text-2xl font-bold text-gray-900 mb-6">Upgrade Demo Account</h2>

                            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                                <div className="flex">
                                    <svg className="h-5 w-5 text-yellow-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                    </svg>
                                    <div>
                                        <h3 className="text-sm font-medium text-yellow-800">This is a Demo Account</h3>
                                        <p className="text-sm text-yellow-700 mt-1">
                                            Your account has the following limits: 2 POCs, 20 tasks, 20 task groups, and 10 resources.
                                            Request a conversion to remove these limits and access the full platform.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <form onSubmit={handleRequestConversion}>
                                <div className="mb-4">
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Reason for Conversion (Optional)
                                    </label>
                                    <textarea
                                        value={conversionReason}
                                        onChange={(e) => setConversionReason(e.target.value)}
                                        rows={4}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                        placeholder="Tell us why you'd like to upgrade to a full account..."
                                    />
                                </div>

                                <button
                                    type="submit"
                                    disabled={requestingConversion}
                                    className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400"
                                >
                                    {requestingConversion ? 'Submitting...' : 'Request Full Account'}
                                </button>
                            </form>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
