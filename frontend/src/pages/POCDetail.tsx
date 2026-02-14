import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../lib/api'
import toast from 'react-hot-toast'
import { useAuthStore } from '../store/authStore'
import POCForm from '../components/POCForm'
import CustomerPOCView from '../components/CustomerPOCView'

interface PublicLink {
    id: number
    poc_id: number
    access_token: string
    access_url: string
    created_at: string
    created_by: number
}

export default function POCDetail() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const { user } = useAuthStore()
    const [poc, setPoc] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [isEditing, setIsEditing] = useState(false)
    const [publicLink, setPublicLink] = useState<PublicLink | null>(null)
    const [showPublicLinkModal, setShowPublicLinkModal] = useState(false)
    const [publicLinkAgreement, setPublicLinkAgreement] = useState('')
    const [generatingLink, setGeneratingLink] = useState(false)
    const [deletingLink, setDeletingLink] = useState(false)

    const isTenantAdmin = user?.role === 'tenant_admin'
    const canEditPoc = user?.role === 'administrator' || user?.role === 'sales_engineer' || user?.role === 'account_executive' || user?.role === 'tenant_admin'

    useEffect(() => {
        if (id) {
            fetchPOC()
            if (isTenantAdmin) {
                fetchPublicLink()
            }
        }
    }, [id, isTenantAdmin])

    const fetchPOC = async () => {
        try {
            const response = await api.get(`/pocs/${id}`)
            setPoc(response.data)
        } catch (error: any) {
            toast.error('Failed to fetch POC details')
        } finally {
            setLoading(false)
        }
    }

    const fetchPublicLink = async () => {
        try {
            const response = await api.get(`/pocs/${id}/public-link`)
            setPublicLink(response.data)
        } catch (error: any) {
            // No link exists yet, that's fine
            setPublicLink(null)
        }
    }

    const createPublicLink = async () => {
        setGeneratingLink(true)
        try {
            const response = await api.post(`/pocs/${id}/public-link`)
            setPublicLink(response.data)
            setPublicLinkAgreement('')
            toast.success('Public link created successfully!')
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to create public link')
        } finally {
            setGeneratingLink(false)
        }
    }

    const deletePublicLink = async () => {
        if (!window.confirm('Are you sure you want to delete this public link? Anyone with the link will no longer be able to access the POC.')) {
            return
        }

        setDeletingLink(true)
        try {
            await api.delete(`/pocs/${id}/public-link`)
            setPublicLink(null)
            toast.success('Public link deleted successfully!')
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to delete public link')
        } finally {
            setDeletingLink(false)
        }
    }

    const copyLinkToClipboard = () => {
        if (publicLink?.access_url) {
            navigator.clipboard.writeText(publicLink.access_url)
            toast.success('Link copied to clipboard!')
        }
    }

    if (loading) {
        return (
            <div className="p-6">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading POC...</p>
                </div>
            </div>
        )
    }

    if (!poc) {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800">POC not found</p>
                </div>
            </div>
        )
    }

    // Show comprehensive POC view for all authenticated users
    if (!isEditing) {
        return (
            <div className="p-6">
                <div className="mb-4 flex items-center justify-between gap-3">
                    <button
                        onClick={() => navigate('/pocs')}
                        className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                    >
                        ← Back to List
                    </button>
                    {canEditPoc && (
                        <button
                            onClick={() => setIsEditing(true)}
                            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                        >
                            Edit POC
                        </button>
                    )}
                </div>
                <CustomerPOCView pocId={parseInt(id!)} />
            </div>
        )
    }

    // isEditing is true
    return (
        <div className="p-6">
            {isTenantAdmin && (
                <div className="mb-4 flex items-center justify-end">
                    <button
                        onClick={() => setShowPublicLinkModal(true)}
                        className="px-4 py-2 border border-indigo-600 text-indigo-700 rounded-lg hover:bg-indigo-50"
                    >
                        {publicLink ? 'View Public Link' : 'Generate Public Link'}
                    </button>
                </div>
            )}
            <POCForm
                pocId={parseInt(id!)}
                initialData={poc}
                onClose={() => {
                    setIsEditing(false)
                    fetchPOC()
                }}
            />
            {showPublicLinkModal && (
                <div className="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg shadow-lg w-full max-w-xl mx-4">
                        <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900">Public Share Link</h3>
                                <p className="text-sm text-gray-600">Share this POC without requiring login.</p>
                            </div>
                            <button
                                onClick={() => {
                                    setShowPublicLinkModal(false)
                                    setPublicLinkAgreement('')
                                }}
                                className="text-gray-500 hover:text-gray-700"
                                aria-label="Close"
                            >
                                ✕
                            </button>
                        </div>
                        <div className="px-6 py-5 space-y-4">
                            {publicLink ? (
                                <>
                                    <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
                                        <div className="text-xs font-semibold text-gray-500 uppercase">Share URL</div>
                                        <div className="mt-1 break-all text-sm text-gray-900">
                                            {publicLink.access_url}
                                        </div>
                                    </div>
                                    <div className="flex flex-wrap items-center gap-2">
                                        <button
                                            onClick={copyLinkToClipboard}
                                            className="px-3 py-2 bg-gray-100 text-gray-800 rounded-md hover:bg-gray-200"
                                        >
                                            Copy Link
                                        </button>
                                        <button
                                            onClick={deletePublicLink}
                                            disabled={deletingLink}
                                            className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-60"
                                        >
                                            {deletingLink ? 'Deleting...' : 'Delete Link'}
                                        </button>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <div className="rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
                                        Anyone with this link can view the POC. Type "Agree" to confirm you understand.
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Type Agree to continue</label>
                                        <input
                                            value={publicLinkAgreement}
                                            onChange={(event) => setPublicLinkAgreement(event.target.value)}
                                            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                                            placeholder="Agree"
                                        />
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={createPublicLink}
                                            disabled={generatingLink || publicLinkAgreement.trim() !== 'Agree'}
                                            className="px-3 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-60"
                                        >
                                            {generatingLink ? 'Generating...' : 'Generate Link'}
                                        </button>
                                        <button
                                            onClick={() => {
                                                setShowPublicLinkModal(false)
                                                setPublicLinkAgreement('')
                                            }}
                                            className="px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
