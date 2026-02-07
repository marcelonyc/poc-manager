import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import toast from 'react-hot-toast'
import CommentsModal from './CommentsModal'

interface POCTask {
    id?: number
    title: string
    description: string | null
    status?: string
}

interface POCTaskGroup {
    id?: number
    title: string
    description: string | null
    status?: string
    tasks?: POCTask[]
}

interface CustomerPOCViewProps {
    pocId: number
}

export default function CustomerPOCView({ pocId }: CustomerPOCViewProps) {
    const [loading, setLoading] = useState(true)
    const [formData, setFormData] = useState<any>({})
    const [pocTasks, setPocTasks] = useState<POCTask[]>([])
    const [pocTaskGroups, setPocTaskGroups] = useState<POCTaskGroup[]>([])
    const [expandedGroups, setExpandedGroups] = useState<Set<number>>(new Set())
    const [resources, setResources] = useState<any[]>([])
    const [successCriteria, setSuccessCriteria] = useState<any[]>([])
    const [activeTab, setActiveTab] = useState<'dashboard' | 'basic' | 'tasks' | 'resources'>('dashboard')
    const [showCommentsModal, setShowCommentsModal] = useState(false)
    const [commentsModalTaskId, setCommentsModalTaskId] = useState<number | undefined>()
    const [commentsModalTaskGroupId, setCommentsModalTaskGroupId] = useState<number | undefined>()
    const [showDocumentModal, setShowDocumentModal] = useState(false)
    const [generatingDocument, setGeneratingDocument] = useState(false)

    useEffect(() => {
        fetchPOCData()
    }, [pocId])

    const fetchPOCData = async () => {
        try {
            setLoading(true)
            const [pocResponse, criteriaResponse, tasksResponse, taskGroupsResponse, resourcesResponse] = await Promise.all([
                api.get(`/pocs/${pocId}`),
                api.get(`/pocs/${pocId}/success-criteria`),
                api.get(`/tasks/pocs/${pocId}/tasks`),
                api.get(`/tasks/pocs/${pocId}/task-groups`),
                api.get(`/pocs/${pocId}/resources`)
            ])

            const poc = pocResponse.data
            setFormData({
                title: poc.title || '',
                description: poc.description || '',
                customer_company_name: poc.customer_company_name || '',
                executive_summary: poc.executive_summary || '',
                objectives: poc.objectives || '',
                start_date: poc.start_date || '',
                end_date: poc.end_date || '',
                product_ids: poc.products?.map((p: any) => p.id) || []
            })
            setSuccessCriteria(criteriaResponse.data || [])
            setPocTasks(tasksResponse.data || [])
            setPocTaskGroups(taskGroupsResponse.data || [])
            setResources(resourcesResponse.data || [])
        } catch (error: any) {
            toast.error('Failed to fetch POC data')
        } finally {
            setLoading(false)
        }
    }

    const getStatusColor = (status: string | undefined) => {
        switch (status) {
            case 'completed': return 'bg-green-100 text-green-800'
            case 'in_progress': return 'bg-blue-100 text-blue-800'
            case 'blocked': return 'bg-red-100 text-red-800'
            default: return 'bg-gray-100 text-gray-800'
        }
    }

    const toggleGroupExpansion = async (groupId: number) => {
        const newExpanded = new Set(expandedGroups)

        if (expandedGroups.has(groupId)) {
            newExpanded.delete(groupId)
        } else {
            newExpanded.add(groupId)

            // Fetch tasks for this group if not already loaded
            const group = pocTaskGroups.find(g => g.id === groupId)
            if (group && !group.tasks) {
                try {
                    const response = await api.get(`/tasks/pocs/${pocId}/task-groups/${groupId}/tasks`)
                    setPocTaskGroups(pocTaskGroups.map(g =>
                        g.id === groupId ? { ...g, tasks: response.data } : g
                    ))
                } catch (error: any) {
                    toast.error('Failed to fetch group tasks')
                }
            }
        }

        setExpandedGroups(newExpanded)
    }

    const handleGenerateDocument = async (format: 'pdf' | 'markdown') => {
        setGeneratingDocument(true)
        try {
            const response = await api.get(`/pocs/${pocId}/generate-document?format=${format}`, {
                responseType: 'blob'
            })

            const blob = new Blob([response.data], {
                type: format === 'pdf' ? 'application/pdf' : 'text/markdown'
            })

            const link = document.createElement('a')
            link.href = window.URL.createObjectURL(blob)
            link.download = `${formData.title}_${new Date().toISOString().split('T')[0]}.${format === 'pdf' ? 'pdf' : 'md'}`
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            window.URL.revokeObjectURL(link.href)

            setShowDocumentModal(false)
            toast.success(`Document generated successfully!`)
        } catch (error: any) {
            toast.error('Failed to generate document')
        } finally {
            setGeneratingDocument(false)
        }
    }

    const getStatusLabel = (status: string | undefined) => {
        switch (status) {
            case 'not_started': return 'Not Started'
            case 'in_progress': return 'In Progress'
            case 'completed': return 'Completed'
            case 'blocked': return 'Blocked'
            default: return 'Not Started'
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center p-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        )
    }

    return (
        <div className="bg-white rounded-lg shadow-md max-w-7xl mx-auto">
            {/* Header */}
            <div className="border-b border-gray-200 px-6 py-4 flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">{formData.title}</h1>
                    <p className="text-gray-600 mt-1">{formData.customer_company_name}</p>
                </div>
                <button
                    onClick={() => setShowDocumentModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Generate Document
                </button>
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200">
                <nav className="flex -mb-px px-6">
                    <button
                        onClick={() => setActiveTab('dashboard')}
                        className={`py-4 px-4 border-b-2 font-medium text-sm ${activeTab === 'dashboard'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        📊 Dashboard
                    </button>
                    <button
                        onClick={() => setActiveTab('basic')}
                        className={`py-4 px-4 border-b-2 font-medium text-sm ${activeTab === 'basic'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        Basic Info
                    </button>
                    <button
                        onClick={() => setActiveTab('tasks')}
                        className={`py-4 px-4 border-b-2 font-medium text-sm ${activeTab === 'tasks'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        Tasks & Groups ({pocTasks.length + pocTaskGroups.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('resources')}
                        className={`py-4 px-4 border-b-2 font-medium text-sm ${activeTab === 'resources'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        📚 Resources ({resources.length})
                    </button>
                </nav>
            </div>

            {/* Content */}
            <div className="p-6 max-h-[calc(100vh-300px)] overflow-y-auto">
                {/* Dashboard Tab */}
                {activeTab === 'dashboard' && (
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold text-gray-900">POC Dashboard</h2>

                        {/* Key Metrics */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <div className="bg-white border border-gray-200 rounded-lg p-4">
                                <div className="text-sm font-medium text-gray-500 mb-1">Days in Progress</div>
                                <div className="text-3xl font-bold text-blue-600">
                                    {formData.start_date ? Math.floor((new Date().getTime() - new Date(formData.start_date).getTime()) / (1000 * 60 * 60 * 24)) : 0}
                                </div>
                                {formData.start_date && formData.end_date && (
                                    <div className="text-xs text-gray-500 mt-1">
                                        of {Math.floor((new Date(formData.end_date).getTime() - new Date(formData.start_date).getTime()) / (1000 * 60 * 60 * 24))} days total
                                    </div>
                                )}
                            </div>

                            <div className="bg-white border border-gray-200 rounded-lg p-4">
                                <div className="text-sm font-medium text-gray-500 mb-1">Total Tasks</div>
                                <div className="text-3xl font-bold text-green-600">{pocTasks.length}</div>
                            </div>

                            <div className="bg-white border border-gray-200 rounded-lg p-4">
                                <div className="text-sm font-medium text-gray-500 mb-1">Total Task Groups</div>
                                <div className="text-3xl font-bold text-purple-600">{pocTaskGroups.length}</div>
                            </div>

                            <div className="bg-white border border-gray-200 rounded-lg p-4">
                                <div className="text-sm font-medium text-gray-500 mb-1">Success Criteria</div>
                                <div className="text-3xl font-bold text-indigo-600">{successCriteria.length}</div>
                            </div>
                        </div>

                        {/* Progress Summary */}
                        <div className="bg-white border border-gray-200 rounded-lg p-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Overall Progress</h3>
                            <div className="space-y-4">
                                <div>
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="text-sm font-medium text-gray-700">Tasks Completed</span>
                                        <span className="text-sm font-semibold text-gray-900">
                                            {pocTasks.filter(t => t.status === 'completed').length} / {pocTasks.length}
                                        </span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-3">
                                        <div
                                            className="bg-green-500 h-3 rounded-full transition-all duration-300"
                                            style={{ width: `${pocTasks.length > 0 ? (pocTasks.filter(t => t.status === 'completed').length / pocTasks.length * 100) : 0}%` }}
                                        ></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="text-sm font-medium text-gray-700">Task Groups Completed</span>
                                        <span className="text-sm font-semibold text-gray-900">
                                            {pocTaskGroups.filter(g => g.status === 'completed').length} / {pocTaskGroups.length}
                                        </span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-3">
                                        <div
                                            className="bg-purple-500 h-3 rounded-full transition-all duration-300"
                                            style={{ width: `${pocTaskGroups.length > 0 ? (pocTaskGroups.filter(g => g.status === 'completed').length / pocTaskGroups.length * 100) : 0}%` }}
                                        ></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Basic Info Tab */}
                {activeTab === 'basic' && (
                    <div className="space-y-6">
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                                    <p className="text-gray-900 whitespace-pre-wrap">{formData.description || 'No description provided'}</p>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                                        <p className="text-gray-900">{formData.start_date ? new Date(formData.start_date).toLocaleDateString() : 'Not set'}</p>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                                        <p className="text-gray-900">{formData.end_date ? new Date(formData.end_date).toLocaleDateString() : 'Not set'}</p>
                                    </div>
                                </div>
                                {formData.executive_summary && (
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Executive Summary</label>
                                        <p className="text-gray-900 whitespace-pre-wrap">{formData.executive_summary}</p>
                                    </div>
                                )}
                                {formData.objectives && (
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Objectives</label>
                                        <p className="text-gray-900 whitespace-pre-wrap">{formData.objectives}</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {/* Tasks Tab */}
                {activeTab === 'tasks' && (
                    <div className="space-y-6">
                        {/* Tasks */}
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Tasks</h3>
                            <div className="space-y-2">
                                {pocTasks.length === 0 ? (
                                    <p className="text-center text-gray-500 py-4">No tasks added yet</p>
                                ) : (
                                    pocTasks.map((task) => (
                                        <div key={task.id} className="border border-gray-200 rounded-lg p-4 bg-white">
                                            <div className="flex justify-between items-start gap-3">
                                                <div className="flex-1">
                                                    <h4 className="font-medium text-gray-900">{task.title}</h4>
                                                    {task.description && (
                                                        <p className="text-sm text-gray-600 mt-1">{task.description}</p>
                                                    )}
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                                                        {getStatusLabel(task.status)}
                                                    </span>
                                                    <button
                                                        onClick={() => {
                                                            setCommentsModalTaskId(task.id)
                                                            setCommentsModalTaskGroupId(undefined)
                                                            setShowCommentsModal(true)
                                                        }}
                                                        className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm"
                                                    >
                                                        💬 Comments
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>

                        {/* Task Groups */}
                        <div className="pt-6 border-t border-gray-200">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Task Groups</h3>
                            <div className="space-y-2">
                                {pocTaskGroups.length === 0 ? (
                                    <p className="text-center text-gray-500 py-4">No task groups added yet</p>
                                ) : (
                                    pocTaskGroups.map((group) => (
                                        <div key={group.id} className="border border-gray-200 rounded-lg bg-white">
                                            <div className="p-4">
                                                <div className="flex justify-between items-start gap-3">
                                                    <div className="flex-1 flex items-start gap-2">
                                                        <button
                                                            onClick={() => toggleGroupExpansion(group.id!)}
                                                            className="mt-1 text-gray-500 hover:text-gray-700 focus:outline-none"
                                                        >
                                                            <svg
                                                                className={`w-4 h-4 transition-transform ${expandedGroups.has(group.id!) ? 'rotate-90' : ''}`}
                                                                fill="none"
                                                                stroke="currentColor"
                                                                viewBox="0 0 24 24"
                                                            >
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                            </svg>
                                                        </button>
                                                        <div className="flex-1">
                                                            <div className="flex items-center gap-2 mb-1">
                                                                <span className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded text-xs font-medium">
                                                                    GROUP
                                                                </span>
                                                                <h4 className="font-medium text-gray-900">{group.title}</h4>
                                                            </div>
                                                            {group.description && (
                                                                <p className="text-sm text-gray-600 mt-1">{group.description}</p>
                                                            )}
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(group.status)}`}>
                                                            {getStatusLabel(group.status)}
                                                        </span>
                                                        <button
                                                            onClick={() => {
                                                                setCommentsModalTaskId(undefined)
                                                                setCommentsModalTaskGroupId(group.id)
                                                                setShowCommentsModal(true)
                                                            }}
                                                            className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm"
                                                        >
                                                            💬 Comments
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Expanded Tasks */}
                                            {expandedGroups.has(group.id!) && group.tasks && (
                                                <div className="border-t border-gray-200 bg-gray-50">
                                                    {group.tasks.length === 0 ? (
                                                        <div className="px-4 py-3 text-sm text-gray-500 italic">
                                                            No tasks in this group
                                                        </div>
                                                    ) : (
                                                        <div className="space-y-0">
                                                            {group.tasks.map((task) => (
                                                                <div key={task.id} className="px-4 py-3 border-b border-gray-200 last:border-b-0 hover:bg-gray-100">
                                                                    <div className="flex justify-between items-start gap-3 ml-6">
                                                                        <div className="flex-1">
                                                                            <h5 className="font-medium text-gray-800 text-sm">{task.title}</h5>
                                                                            {task.description && (
                                                                                <p className="text-sm text-gray-600 mt-1">{task.description}</p>
                                                                            )}
                                                                        </div>
                                                                        <div className="flex items-center gap-2">
                                                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                                                                                {getStatusLabel(task.status)}
                                                                            </span>
                                                                            <button
                                                                                onClick={() => {
                                                                                    setCommentsModalTaskId(task.id)
                                                                                    setCommentsModalTaskGroupId(undefined)
                                                                                    setShowCommentsModal(true)
                                                                                }}
                                                                                className="px-2 py-1 bg-white text-gray-700 rounded hover:bg-gray-200 text-xs"
                                                                            >
                                                                                💬
                                                                            </button>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {/* Resources Tab */}
                {activeTab === 'resources' && (
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Resources</h3>
                        <div className="space-y-3">
                            {resources.length === 0 ? (
                                <div className="text-center py-8 text-gray-600 bg-white border-2 border-dashed border-gray-300 rounded-lg">
                                    No resources available yet
                                </div>
                            ) : (
                                resources.map((resource) => (
                                    <div key={resource.id} className="bg-white border border-gray-300 p-4 rounded-lg hover:border-gray-400 transition-colors">
                                        <div className="flex justify-between items-start mb-2">
                                            <div className="flex items-center gap-2">
                                                <span className={`px-2 py-1 text-xs font-medium rounded ${resource.resource_type === 'LINK' ? 'bg-blue-100 text-blue-800' :
                                                    resource.resource_type === 'CODE' ? 'bg-purple-100 text-purple-800' :
                                                        resource.resource_type === 'TEXT' ? 'bg-green-100 text-green-800' :
                                                            'bg-orange-100 text-orange-800'
                                                    }`}>
                                                    {resource.resource_type}
                                                </span>
                                                <h4 className="font-medium text-gray-900">{resource.title}</h4>
                                            </div>
                                        </div>
                                        {resource.description && (
                                            <p className="text-sm text-gray-700 mb-2">{resource.description}</p>
                                        )}
                                        <div className={`text-sm ${resource.resource_type === 'LINK' ? 'text-blue-600 underline' : 'text-gray-900'
                                            } bg-gray-50 p-3 rounded border border-gray-300 font-mono overflow-x-auto`}>
                                            {resource.resource_type === 'LINK' ? (
                                                <a href={resource.content} target="_blank" rel="noopener noreferrer">
                                                    {resource.content}
                                                </a>
                                            ) : (
                                                <pre className="whitespace-pre-wrap">{resource.content}</pre>
                                            )}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* Comments Modal */}
            {showCommentsModal && (
                <CommentsModal
                    pocId={pocId}
                    taskId={commentsModalTaskId}
                    taskGroupId={commentsModalTaskGroupId}
                    onClose={() => {
                        setShowCommentsModal(false)
                        setCommentsModalTaskId(undefined)
                        setCommentsModalTaskGroupId(undefined)
                    }}
                />
            )}

            {/* Document Generation Modal */}
            {showDocumentModal && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
                    <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                        <h3 className="text-lg font-medium text-gray-900">Generate POC Document</h3>
                        <p className="text-sm text-gray-600 mt-2">Choose a format for your document:</p>

                        <div className="mt-6 space-y-3">
                            <button
                                onClick={() => handleGenerateDocument('pdf')}
                                disabled={generatingDocument}
                                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-red-50 hover:bg-red-100 text-red-700 rounded-md border border-red-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {generatingDocument ? (
                                    <>
                                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-700"></div>
                                        Generating...
                                    </>
                                ) : (
                                    <>
                                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                            <path d="M5.5 13a3.5 3.5 0 01-.369-6.98 4 4 0 117.753-1.3A4.5 4.5 0 1113.5 13H11V9.413l1.293 1.293a1 1 0 001.414-1.414l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13H5.5z" />
                                        </svg>
                                        Download as PDF
                                    </>
                                )}
                            </button>

                            <button
                                onClick={() => handleGenerateDocument('markdown')}
                                disabled={generatingDocument}
                                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-md border border-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {generatingDocument ? (
                                    <>
                                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-700"></div>
                                        Generating...
                                    </>
                                ) : (
                                    <>
                                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                            <path d="M5.5 13a3.5 3.5 0 01-.369-6.98 4 4 0 117.753-1.3A4.5 4.5 0 1113.5 13H11V9.413l1.293 1.293a1 1 0 001.414-1.414l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13H5.5z" />
                                        </svg>
                                        Download as Markdown
                                    </>
                                )}
                            </button>
                        </div>

                        <div className="mt-6 flex justify-end">
                            <button
                                onClick={() => setShowDocumentModal(false)}
                                disabled={generatingDocument}
                                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
