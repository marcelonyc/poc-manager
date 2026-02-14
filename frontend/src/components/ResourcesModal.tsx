import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import toast from 'react-hot-toast'
import { useAuthStore } from '../store/authStore'

interface Resource {
    id: number
    title: string
    description: string | null
    resource_type: 'link' | 'code' | 'text' | 'file'
    content: string
    sort_order: number
    created_at: string
}

interface ResourcesModalProps {
    pocId: number
    taskId?: number
    taskGroupId?: number
    taskTitle: string
    isPublicAccess?: boolean
    publicAccessToken?: string
    onClose: () => void
}

const RESOURCE_TYPES = [
    { value: 'link', label: '🔗 Link', icon: 'bg-blue-100 text-blue-800' },
    { value: 'code', label: '💻 Code', icon: 'bg-purple-100 text-purple-800' },
    { value: 'text', label: '📝 Text', icon: 'bg-green-100 text-green-800' },
    { value: 'file', label: '📁 File', icon: 'bg-orange-100 text-orange-800' },
]

export default function ResourcesModal({
    pocId,
    taskId,
    taskGroupId,
    taskTitle,
    isPublicAccess = false,
    publicAccessToken,
    onClose,
}: ResourcesModalProps) {
    const { user } = useAuthStore()
    const [resources, setResources] = useState<Resource[]>([])
    const [loading, setLoading] = useState(true)
    const [isAdding, setIsAdding] = useState(false)
    const [editingId, setEditingId] = useState<number | null>(null)
    const [deleting, setDeleting] = useState<number | null>(null)

    // Form state
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        resource_type: 'link' as 'link' | 'code' | 'text' | 'file',
        content: '',
    })

    const canEdit = !isPublicAccess && (user?.role === 'sales_engineer' || user?.role === 'account_executive' || user?.role === 'administrator' || user?.role === 'tenant_admin')

    const getBaseUrl = () => {
        if (isPublicAccess && publicAccessToken) {
            if (taskId) {
                return `/public/pocs/${publicAccessToken}/tasks/${taskId}/resources`
            } else {
                return `/public/pocs/${publicAccessToken}/task-groups/${taskGroupId}/resources`
            }
        } else {
            if (taskId) {
                return `/pocs/${pocId}/tasks/${taskId}/resources`
            } else {
                return `/pocs/${pocId}/task-groups/${taskGroupId}/resources`
            }
        }
    }

    const baseUrl = getBaseUrl()

    useEffect(() => {
        fetchResources()
    }, [])

    const fetchResources = async () => {
        try {
            setLoading(true)
            const response = await api.get(baseUrl)
            setResources(response.data || [])
        } catch (error: any) {
            toast.error('Failed to fetch resources')
        } finally {
            setLoading(false)
        }
    }

    const resetForm = () => {
        setFormData({
            title: '',
            description: '',
            resource_type: 'link',
            content: '',
        })
        setIsAdding(false)
        setEditingId(null)
    }

    const handleSubmit = async () => {
        if (!formData.title.trim() || !formData.content.trim()) {
            toast.error('Please fill in title and content')
            return
        }

        try {
            if (editingId) {
                // Update existing resource
                await api.put(`${baseUrl}/${editingId}`, formData)
                toast.success('Resource updated successfully')
            } else {
                // Create new resource
                await api.post(baseUrl, {
                    ...formData,
                    sort_order: resources.length,
                })
                toast.success('Resource added successfully')
            }
            resetForm()
            await fetchResources()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to save resource')
        }
    }

    const handleDelete = async (id: number) => {
        if (!window.confirm('Are you sure you want to delete this resource?')) {
            return
        }

        try {
            setDeleting(id)
            await api.delete(`${baseUrl}/${id}`)
            toast.success('Resource deleted successfully')
            await fetchResources()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to delete resource')
        } finally {
            setDeleting(null)
        }
    }

    const handleEdit = (resource: Resource) => {
        setFormData({
            title: resource.title,
            description: resource.description || '',
            resource_type: resource.resource_type,
            content: resource.content,
        })
        setEditingId(resource.id)
        setIsAdding(true)
    }

    const getResourceTypeColor = (type: string) => {
        const resourceType = RESOURCE_TYPES.find(rt => rt.value === type)
        return resourceType?.icon || 'bg-gray-100 text-gray-800'
    }

    const getResourceTypeLabel = (type: string) => {
        const resourceType = RESOURCE_TYPES.find(rt => rt.value === type)
        return resourceType?.label || type.toUpperCase()
    }

    const renderContent = (type: string, content: string) => {
        if (type === 'link') {
            return (
                <a href={content} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline hover:text-blue-800">
                    {content}
                </a>
            )
        }
        return <pre className="whitespace-pre-wrap break-words">{content}</pre>
    }

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="border-b border-gray-200 px-6 py-4 flex justify-between items-center bg-gradient-to-r from-blue-50 to-indigo-50">
                    <div>
                        <h2 className="text-xl font-bold text-gray-900">📚 Resources</h2>
                        <p className="text-sm text-gray-600 mt-1">{taskTitle}</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-500 hover:text-gray-700 focus:outline-none"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    {loading ? (
                        <div className="flex items-center justify-center py-12">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {/* Add/Edit Form */}
                            {isAdding && canEdit && (
                                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-4">
                                    <div className="flex justify-between items-center">
                                        <h3 className="font-semibold text-gray-900">
                                            {editingId ? 'Edit Resource' : 'Add New Resource'}
                                        </h3>
                                        <button
                                            onClick={resetForm}
                                            className="text-gray-500 hover:text-gray-700"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                            </svg>
                                        </button>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Resource Type
                                        </label>
                                        <select
                                            value={formData.resource_type}
                                            onChange={(e) => setFormData({ ...formData, resource_type: e.target.value as any })}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                        >
                                            {RESOURCE_TYPES.map((type) => (
                                                <option key={type.value} value={type.value}>
                                                    {type.label}
                                                </option>
                                            ))}
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Title *
                                        </label>
                                        <input
                                            type="text"
                                            value={formData.title}
                                            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                            placeholder="e.g., API Documentation"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Description
                                        </label>
                                        <input
                                            type="text"
                                            value={formData.description}
                                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                            placeholder="Optional description"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Content *
                                        </label>
                                        {formData.resource_type === 'link' ? (
                                            <input
                                                type="url"
                                                value={formData.content}
                                                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                                placeholder="https://example.com"
                                            />
                                        ) : (
                                            <textarea
                                                value={formData.content}
                                                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                                                rows={6}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                                                placeholder="Paste your content here..."
                                            />
                                        )}
                                    </div>

                                    <div className="flex gap-2">
                                        <button
                                            onClick={handleSubmit}
                                            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
                                        >
                                            {editingId ? 'Update Resource' : 'Add Resource'}
                                        </button>
                                        <button
                                            onClick={resetForm}
                                            className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* Resources List */}
                            {resources.length === 0 ? (
                                <div className="text-center py-8">
                                    <p className="text-gray-500">No resources yet</p>
                                    {canEdit && !isAdding && (
                                        <button
                                            onClick={() => setIsAdding(true)}
                                            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                                        >
                                            + Add First Resource
                                        </button>
                                    )}
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {resources.map((resource) => (
                                        <div
                                            key={resource.id}
                                            className="bg-white border border-gray-300 rounded-lg p-4 hover:border-gray-400 hover:shadow-md transition-all"
                                        >
                                            <div className="flex justify-between items-start gap-3 mb-3">
                                                <div className="flex items-start gap-2 flex-1">
                                                    <span
                                                        className={`px-2 py-1 text-xs font-medium rounded whitespace-nowrap ${getResourceTypeColor(
                                                            resource.resource_type
                                                        )}`}
                                                    >
                                                        {getResourceTypeLabel(resource.resource_type)}
                                                    </span>
                                                    <div className="flex-1 min-w-0">
                                                        <h3 className="font-medium text-gray-900 break-words">
                                                            {resource.title}
                                                        </h3>
                                                        {resource.description && (
                                                            <p className="text-sm text-gray-600 mt-1">
                                                                {resource.description}
                                                            </p>
                                                        )}
                                                    </div>
                                                </div>
                                                {canEdit && (
                                                    <div className="flex gap-2 flex-shrink-0">
                                                        <button
                                                            onClick={() => handleEdit(resource)}
                                                            className="p-2 text-blue-600 hover:bg-blue-50 rounded hover:text-blue-800 transition-colors"
                                                            title="Edit"
                                                        >
                                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                                            </svg>
                                                        </button>
                                                        <button
                                                            onClick={() => handleDelete(resource.id)}
                                                            disabled={deleting === resource.id}
                                                            className="p-2 text-red-600 hover:bg-red-50 rounded hover:text-red-800 transition-colors disabled:opacity-50"
                                                            title="Delete"
                                                        >
                                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                            </svg>
                                                        </button>
                                                    </div>
                                                )}
                                            </div>

                                            <div className="mt-3 bg-gray-50 rounded-md p-3 border border-gray-200 font-mono text-sm text-gray-700 overflow-x-auto">
                                                {renderContent(resource.resource_type, resource.content)}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="border-t border-gray-200 px-6 py-4 flex gap-3 justify-between items-center bg-gray-50">
                    {!isAdding && canEdit && (
                        <button
                            onClick={() => setIsAdding(true)}
                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
                        >
                            + Add Resource
                        </button>
                    )}
                    <button
                        onClick={onClose}
                        className="ml-auto px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors font-medium"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    )
}
