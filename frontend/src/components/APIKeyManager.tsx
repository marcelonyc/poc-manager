import { useState, useEffect, useCallback } from 'react'
import { api } from '../lib/api'
import toast from 'react-hot-toast'

interface APIKey {
    id: number
    name: string
    key_prefix: string
    expires_at: string
    is_active: boolean
    created_at: string
    last_used_at: string | null
}

const EXPIRATION_OPTIONS = [
    { value: '6_months', label: '6 Months' },
    { value: '1_year', label: '1 Year' },
    { value: '2_years', label: '2 Years' },
]

export default function APIKeyManager() {
    const [keys, setKeys] = useState<APIKey[]>([])
    const [loading, setLoading] = useState(true)
    const [creating, setCreating] = useState(false)
    const [showCreateForm, setShowCreateForm] = useState(false)
    const [newKeyName, setNewKeyName] = useState('')
    const [newKeyExpiration, setNewKeyExpiration] = useState('1_year')
    const [createdKey, setCreatedKey] = useState<string | null>(null)
    const [extendingKeyId, setExtendingKeyId] = useState<number | null>(null)
    const [extendExpiration, setExtendExpiration] = useState('6_months')

    const fetchKeys = useCallback(async () => {
        try {
            const response = await api.get('/api-keys/')
            setKeys(response.data)
        } catch (err: any) {
            toast.error(err.response?.data?.detail || 'Failed to load API keys')
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        fetchKeys()
    }, [fetchKeys])

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!newKeyName.trim()) {
            toast.error('Please enter a name for the API key')
            return
        }
        setCreating(true)
        try {
            const response = await api.post('/api-keys/', {
                name: newKeyName.trim(),
                expiration: newKeyExpiration,
            })
            setCreatedKey(response.data.api_key)
            setNewKeyName('')
            setNewKeyExpiration('1_year')
            setShowCreateForm(false)
            fetchKeys()
            toast.success('API key created successfully')
        } catch (err: any) {
            toast.error(err.response?.data?.detail || 'Failed to create API key')
        } finally {
            setCreating(false)
        }
    }

    const handleDelete = async (keyId: number, keyName: string) => {
        if (!window.confirm(`Are you sure you want to delete the API key "${keyName}"? This action cannot be undone.`)) {
            return
        }
        try {
            await api.delete(`/api-keys/${keyId}`)
            fetchKeys()
            toast.success('API key deleted')
        } catch (err: any) {
            toast.error(err.response?.data?.detail || 'Failed to delete API key')
        }
    }

    const handleExtend = async (keyId: number) => {
        try {
            await api.post(`/api-keys/${keyId}/extend`, {
                expiration: extendExpiration,
            })
            setExtendingKeyId(null)
            fetchKeys()
            toast.success('API key expiration extended')
        } catch (err: any) {
            toast.error(err.response?.data?.detail || 'Failed to extend API key')
        }
    }

    const copyToClipboard = async (text: string) => {
        try {
            await navigator.clipboard.writeText(text)
            toast.success('Copied to clipboard')
        } catch {
            toast.error('Failed to copy — please select and copy manually')
        }
    }

    const isExpired = (expiresAt: string) => new Date(expiresAt) < new Date()
    const activeKeys = keys.filter(k => k.is_active)

    if (loading) {
        return (
            <div className="animate-pulse space-y-3">
                <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                <div className="h-10 bg-gray-200 rounded"></div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-xl font-semibold text-gray-900">API Keys</h2>
                    <p className="text-sm text-gray-500 mt-1">
                        Generate long-lived API keys to interact with the POC Manager API programmatically.
                        You can have up to 3 active keys.
                    </p>
                </div>
                {activeKeys.length < 3 && !showCreateForm && !createdKey && (
                    <button
                        onClick={() => setShowCreateForm(true)}
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                    >
                        + New API Key
                    </button>
                )}
            </div>

            {/* Created key banner — shown only once after creation */}
            {createdKey && (
                <div className="rounded-md bg-yellow-50 border border-yellow-300 p-4">
                    <div className="flex">
                        <div className="flex-shrink-0 text-yellow-600 text-xl">⚠️</div>
                        <div className="ml-3 flex-1">
                            <h3 className="text-sm font-bold text-yellow-800">
                                Save your API key now — it won't be shown again!
                            </h3>
                            <p className="mt-1 text-sm text-yellow-700">
                                Store it in a secure vault such as <strong>Dashlane</strong>, <strong>1Password</strong>, or <strong>HashiCorp Vault</strong>.
                                This key cannot be recovered once you dismiss this message.
                            </p>
                            <div className="mt-3 flex items-center gap-2">
                                <code className="flex-1 block bg-yellow-100 border border-yellow-300 rounded px-3 py-2 text-xs font-mono text-yellow-900 break-all select-all">
                                    {createdKey}
                                </code>
                                <button
                                    onClick={() => copyToClipboard(createdKey)}
                                    className="px-3 py-2 text-sm font-medium rounded-md border border-yellow-400 text-yellow-800 bg-yellow-100 hover:bg-yellow-200"
                                >
                                    Copy
                                </button>
                            </div>
                            <button
                                onClick={() => setCreatedKey(null)}
                                className="mt-3 text-sm font-medium text-yellow-800 underline hover:text-yellow-900"
                            >
                                I've saved the key — dismiss
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Create form */}
            {showCreateForm && (
                <form onSubmit={handleCreate} className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-4">
                    <h3 className="text-sm font-semibold text-gray-700">Create New API Key</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                            <input
                                type="text"
                                value={newKeyName}
                                onChange={e => setNewKeyName(e.target.value)}
                                placeholder="e.g. CI/CD Pipeline"
                                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                                maxLength={100}
                                autoFocus
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Expiration</label>
                            <select
                                value={newKeyExpiration}
                                onChange={e => setNewKeyExpiration(e.target.value)}
                                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                            >
                                {EXPIRATION_OPTIONS.map(opt => (
                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                    <div className="flex gap-2 justify-end">
                        <button
                            type="button"
                            onClick={() => setShowCreateForm(false)}
                            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={creating}
                            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
                        >
                            {creating ? 'Creating…' : 'Create Key'}
                        </button>
                    </div>
                </form>
            )}

            {/* Keys list */}
            {keys.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                    <p className="text-lg">No API keys yet</p>
                    <p className="text-sm mt-1">Create your first API key to get started with programmatic access.</p>
                </div>
            ) : (
                <div className="overflow-hidden border border-gray-200 rounded-lg">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Key Prefix</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Expires</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Used</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {keys.map(key => {
                                const expired = isExpired(key.expires_at)
                                return (
                                    <tr key={key.id} className={expired ? 'bg-red-50' : ''}>
                                        <td className="px-4 py-3 text-sm font-medium text-gray-900">{key.name}</td>
                                        <td className="px-4 py-3 text-sm text-gray-500 font-mono">{key.key_prefix}…</td>
                                        <td className="px-4 py-3 text-sm text-gray-500">
                                            {new Date(key.created_at).toLocaleDateString()}
                                        </td>
                                        <td className="px-4 py-3 text-sm text-gray-500">
                                            {new Date(key.expires_at).toLocaleDateString()}
                                        </td>
                                        <td className="px-4 py-3 text-sm text-gray-500">
                                            {key.last_used_at ? new Date(key.last_used_at).toLocaleDateString() : 'Never'}
                                        </td>
                                        <td className="px-4 py-3 text-sm">
                                            {expired ? (
                                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">Expired</span>
                                            ) : key.is_active ? (
                                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Active</span>
                                            ) : (
                                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">Inactive</span>
                                            )}
                                        </td>
                                        <td className="px-4 py-3 text-sm text-right space-x-2">
                                            {key.is_active && (
                                                <>
                                                    {extendingKeyId === key.id ? (
                                                        <span className="inline-flex items-center gap-1">
                                                            <select
                                                                value={extendExpiration}
                                                                onChange={e => setExtendExpiration(e.target.value)}
                                                                className="border border-gray-300 rounded text-xs px-1 py-1"
                                                            >
                                                                {EXPIRATION_OPTIONS.map(opt => (
                                                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                                                ))}
                                                            </select>
                                                            <button
                                                                onClick={() => handleExtend(key.id)}
                                                                className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                                                            >
                                                                Confirm
                                                            </button>
                                                            <button
                                                                onClick={() => setExtendingKeyId(null)}
                                                                className="text-xs text-gray-500 hover:text-gray-700"
                                                            >
                                                                Cancel
                                                            </button>
                                                        </span>
                                                    ) : (
                                                        <button
                                                            onClick={() => { setExtendingKeyId(key.id); setExtendExpiration('6_months') }}
                                                            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                                                        >
                                                            Extend
                                                        </button>
                                                    )}
                                                </>
                                            )}
                                            <button
                                                onClick={() => handleDelete(key.id, key.name)}
                                                className="text-sm text-red-600 hover:text-red-800 font-medium"
                                            >
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    )
}
