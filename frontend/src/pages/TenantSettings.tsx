import { useState, useEffect } from 'react'
import { api, API_URL } from '../lib/api'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'
import APIKeyManager from '../components/APIKeyManager'

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
    ai_assistant_enabled: boolean
    has_ollama_api_key: boolean
    ollama_model: string | null
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
    const [showUpgradeModal, setShowUpgradeModal] = useState(false)

    // Test email
    const [testEmailAddress, setTestEmailAddress] = useState('')
    const [sendingTestEmail, setSendingTestEmail] = useState(false)

    // AI Assistant
    const [aiEnabled, setAiEnabled] = useState(false)
    const [ollamaApiKey, setOllamaApiKey] = useState('')
    const [savingAi, setSavingAi] = useState(false)
    const [showAiWarning, setShowAiWarning] = useState(false)

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

            // Set AI Assistant state
            setAiEnabled(tenantData.ai_assistant_enabled || false)

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

    const handleRequestConversion = async () => {
        setRequestingConversion(true)
        setError('')
        setSuccess('')

        try {
            await api.post('/demo/request-conversion', {
                reason: conversionReason || null
            })
            setShowUpgradeModal(false)
            setConversionReason('')
            toast.success(
                'Your upgrade request has been submitted! The platform administrator has been notified and you will receive an email with further details.',
                { duration: 6000 }
            )
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to submit conversion request')
            setShowUpgradeModal(false)
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

    const handleSaveAiAssistant = async (e: React.FormEvent) => {
        e.preventDefault()
        setSavingAi(true)
        setError('')
        setSuccess('')

        try {
            const updateData: Record<string, any> = {
                ai_assistant_enabled: aiEnabled,
            }
            if (ollamaApiKey) {
                updateData.ollama_api_key = ollamaApiKey
            }

            await api.put(`/tenants/${user?.tenant_id}`, updateData)
            setSuccess('AI Assistant settings saved successfully')
            setOllamaApiKey('')
            fetchTenantSettings()
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to save AI Assistant settings')
        } finally {
            setSavingAi(false)
        }
    }

    const handleToggleAi = (enabled: boolean) => {
        if (enabled && !aiEnabled) {
            setShowAiWarning(true)
        } else {
            setAiEnabled(enabled)
        }
    }

    const confirmEnableAi = () => {
        setAiEnabled(true)
        setShowAiWarning(false)
    }

    if (user?.role === 'platform_admin') {
        return (
            <div className="p-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-6">Settings</h1>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                    <p className="text-yellow-800">
                        Platform Admins don't have tenant-specific settings. Use the Tenants page to manage tenants.
                    </p>
                </div>
                <div className="bg-white rounded-lg shadow-md p-6">
                    <APIKeyManager />
                </div>
            </div>
        )
    }

    if (user?.role !== 'tenant_admin') {
        return (
            <div className="p-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-6">Settings</h1>
                <div className="bg-white rounded-lg shadow-md p-6">
                    <APIKeyManager />
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

                    {/* AI Assistant Configuration */}
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center">
                                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                                    </svg>
                                </div>
                                <h2 className="text-xl font-semibold">AI Assistant</h2>
                            </div>
                            {tenant.ai_assistant_enabled && tenant.has_ollama_api_key && (
                                <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                                    Active
                                </span>
                            )}
                        </div>

                        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
                            <div className="flex">
                                <svg className="h-5 w-5 text-amber-500 mr-3 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                </svg>
                                <div>
                                    <h3 className="text-sm font-medium text-amber-800">Bring Your Own Model</h3>
                                    <p className="text-sm text-amber-700 mt-1">
                                        This is a <strong>bring-your-own-model</strong> feature that requires access to  <strong>Ollama Cloud Models</strong>.
                                        You must provide a valid Ollama API key. The AI Assistant uses your
                                        Ollama API to power conversations — your data is sent to your Ollama Cloud Account.
                                        <br />
                                        <a href="https://ollama.com/pricing" target="_blank" rel="noopener noreferrer" className="text-amber-800 underline hover:text-amber-900">
                                            Learn more about Ollama pricing
                                        </a>
                                    </p>
                                </div>
                            </div>
                        </div>

                        {tenant?.ollama_model && (
                            <div className="flex items-start gap-3 mb-6 px-4 py-3 bg-indigo-50 border border-indigo-200 rounded-lg">
                                <svg className="h-5 w-5 text-indigo-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                </svg>
                                <p className="text-sm text-indigo-800">
                                    <span className="font-medium">Ollama model in use:</span>{' '}
                                    <code className="px-1.5 py-0.5 bg-indigo-100 rounded text-indigo-900 font-mono text-xs">{tenant.ollama_model}</code>
                                </p>
                            </div>
                        )}

                        <form onSubmit={handleSaveAiAssistant} className="space-y-4">
                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                <div>
                                    <label className="text-sm font-medium text-gray-900">Enable AI Assistant</label>
                                    <p className="text-xs text-gray-500 mt-0.5">Allow users in this tenant to use the AI chat assistant</p>
                                </div>
                                <button
                                    type="button"
                                    onClick={() => handleToggleAi(!aiEnabled)}
                                    className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${aiEnabled ? 'bg-indigo-600' : 'bg-gray-200'
                                        }`}
                                >
                                    <span
                                        className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${aiEnabled ? 'translate-x-5' : 'translate-x-0'
                                            }`}
                                    />
                                </button>
                            </div>

                            {aiEnabled && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Ollama API Key {tenant.has_ollama_api_key ? '(Leave blank to keep existing)' : '*'}
                                    </label>
                                    <input
                                        type="password"
                                        value={ollamaApiKey}
                                        onChange={(e) => setOllamaApiKey(e.target.value)}
                                        required={!tenant.has_ollama_api_key}
                                        placeholder={tenant.has_ollama_api_key ? '••••••••' : 'Enter your Ollama API key'}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                    />
                                    <p className="text-xs text-gray-500 mt-1">
                                        Your API key is encrypted and stored securely. It is only used for AI Assistant sessions within this tenant.
                                    </p>
                                </div>
                            )}

                            <div className="pt-4 border-t">
                                <button
                                    type="submit"
                                    disabled={savingAi}
                                    className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400"
                                >
                                    {savingAi ? 'Saving...' : 'Save AI Assistant Settings'}
                                </button>
                            </div>
                        </form>
                    </div>

                    {/* AI Enable Warning Modal */}
                    {showAiWarning && (
                        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                            <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="flex-shrink-0 h-10 w-10 rounded-full bg-amber-100 flex items-center justify-center">
                                        <svg className="h-6 w-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                                        </svg>
                                    </div>
                                    <h3 className="text-lg font-semibold text-gray-900">Enable AI Assistant?</h3>
                                </div>

                                <p className="text-sm text-gray-600 mb-3">
                                    This is a <strong>bring-your-own-model</strong> feature. Before enabling, please ensure:
                                </p>
                                <ul className="text-sm text-gray-600 mb-4 list-disc list-inside space-y-1">
                                    <li>You have access to an <strong>Ollama API</strong> instance</li>
                                    <li>You have a valid Ollama API key to provide</li>
                                    <li>You understand that chat messages will be sent to your Ollama endpoint</li>
                                </ul>

                                <div className="flex justify-end gap-3">
                                    <button
                                        onClick={() => setShowAiWarning(false)}
                                        className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={confirmEnableAi}
                                        className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                                    >
                                        I Understand, Enable
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Demo Account Upgrade Section */}
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
                                            Request an upgrade to remove these limits and access the full platform.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <button
                                onClick={() => setShowUpgradeModal(true)}
                                className="inline-flex items-center gap-2 bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 font-semibold shadow-sm transition-colors"
                            >
                                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                                </svg>
                                Request Upgrade to Full Account
                            </button>
                        </div>
                    )}

                    {/* Upgrade Request Modal */}
                    {showUpgradeModal && (
                        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                            <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="flex-shrink-0 h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                                        <svg className="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                                        </svg>
                                    </div>
                                    <h3 className="text-lg font-semibold text-gray-900">Request Account Upgrade</h3>
                                </div>

                                <p className="text-sm text-gray-600 mb-4">
                                    This will send an upgrade request to the platform administrators. You will receive an email with further details once your request has been reviewed.
                                </p>

                                <div className="mb-4">
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Reason for Upgrade (Optional)
                                    </label>
                                    <textarea
                                        value={conversionReason}
                                        onChange={(e) => setConversionReason(e.target.value)}
                                        rows={3}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                        placeholder="Tell us why you'd like to upgrade to a full account..."
                                    />
                                </div>

                                <div className="flex justify-end gap-3">
                                    <button
                                        onClick={() => { setShowUpgradeModal(false); setConversionReason('') }}
                                        disabled={requestingConversion}
                                        className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={handleRequestConversion}
                                        disabled={requestingConversion}
                                        className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 transition-colors"
                                    >
                                        {requestingConversion ? 'Submitting...' : 'Submit Upgrade Request'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* API Key Management — available for all tenant admins */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <APIKeyManager />
            </div>
        </div>
    )
}
