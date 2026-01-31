import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import toast from 'react-hot-toast'
import DemoLimitsBanner from '../components/DemoLimitsBanner'

interface Task {
    id: number
    title: string
    description: string | null
    tenant_id: number
    created_by: number
    is_template: boolean
    created_at: string
}

interface TaskGroup {
    id: number
    title: string
    description: string | null
    tenant_id: number
    created_by: number
    is_template: boolean
    created_at: string
    tasks: Task[]
}

interface TaskFormData {
    title: string
    description: string
}

type ResourceType = 'LINK' | 'CODE' | 'TEXT' | 'FILE'

interface TaskResource {
    id: number
    task_id: number
    title: string
    description: string | null
    resource_type: ResourceType
    content: string
    sort_order: number | null
    created_at: string
    updated_at: string | null
}

interface ResourceFormData {
    title: string
    description: string
    resource_type: ResourceType
    content: string
}

export default function TaskTemplates() {
    const [activeTab, setActiveTab] = useState<'tasks' | 'groups'>('tasks')
    const [tasks, setTasks] = useState<Task[]>([])
    const [taskGroups, setTaskGroups] = useState<TaskGroup[]>([])
    const [loading, setLoading] = useState(true)
    const [showTaskForm, setShowTaskForm] = useState(false)
    const [showGroupForm, setShowGroupForm] = useState(false)
    const [editingTask, setEditingTask] = useState<Task | null>(null)
    const [editingGroup, setEditingGroup] = useState<TaskGroup | null>(null)

    const [taskFormData, setTaskFormData] = useState<TaskFormData>({
        title: '',
        description: '',
    })

    const [groupFormData, setGroupFormData] = useState<TaskFormData>({
        title: '',
        description: '',
    })

    const [submitting, setSubmitting] = useState(false)

    // Resource management state
    const [resources, setResources] = useState<TaskResource[]>([])
    const [showResourceForm, setShowResourceForm] = useState(false)
    const [editingResource, setEditingResource] = useState<TaskResource | null>(null)
    const [resourceFormData, setResourceFormData] = useState<ResourceFormData>({
        title: '',
        description: '',
        resource_type: 'LINK',
        content: '',
    })

    // Drag and drop state
    const [draggedTask, setDraggedTask] = useState<Task | null>(null)

    // Task selection for groups
    const [selectedTaskIds, setSelectedTaskIds] = useState<number[]>([])

    // Task group resource management state
    const [groupResources, setGroupResources] = useState<TaskResource[]>([])
    const [showGroupResourceForm, setShowGroupResourceForm] = useState(false)
    const [editingGroupResource, setEditingGroupResource] = useState<TaskResource | null>(null)
    const [groupResourceFormData, setGroupResourceFormData] = useState<ResourceFormData>({
        title: '',
        description: '',
        resource_type: 'LINK',
        content: '',
    })

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            const [tasksRes, groupsRes] = await Promise.all([
                api.get('/tasks/templates'),
                api.get('/tasks/groups/templates'),
            ])
            setTasks(tasksRes.data)
            setTaskGroups(groupsRes.data)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to fetch templates')
        } finally {
            setLoading(false)
        }
    }

    const handleTaskInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target
        setTaskFormData(prev => ({ ...prev, [name]: value }))
    }

    const handleGroupInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target
        setGroupFormData(prev => ({ ...prev, [name]: value }))
    }

    const handleCreateTask = async (e: React.FormEvent) => {
        e.preventDefault()
        setSubmitting(true)

        try {
            await api.post('/tasks/templates', taskFormData)
            toast.success('Task template created successfully!')
            setShowTaskForm(false)
            setTaskFormData({ title: '', description: '' })
            fetchData()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to create task template')
        } finally {
            setSubmitting(false)
        }
    }

    const handleUpdateTask = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!editingTask) return

        setSubmitting(true)
        try {
            await api.put(`/tasks/templates/${editingTask.id}`, taskFormData)
            toast.success('Task template updated successfully!')
            setEditingTask(null)
            setTaskFormData({ title: '', description: '' })
            fetchData()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to update task template')
        } finally {
            setSubmitting(false)
        }
    }

    const handleCreateGroup = async (e: React.FormEvent) => {
        e.preventDefault()
        setSubmitting(true)

        try {
            if (editingGroup) {
                // Update group details
                await api.put(`/tasks/groups/templates/${editingGroup.id}`, groupFormData)

                // Update tasks in group
                const existingTaskIds = editingGroup.tasks?.map(t => t.id) || []
                const tasksToAdd = selectedTaskIds.filter(id => !existingTaskIds.includes(id))
                const tasksToRemove = existingTaskIds.filter(id => !selectedTaskIds.includes(id))

                // Add new tasks
                for (const taskId of tasksToAdd) {
                    await api.post(`/tasks/groups/${editingGroup.id}/tasks/${taskId}`)
                }

                // Remove tasks
                for (const taskId of tasksToRemove) {
                    await api.delete(`/tasks/groups/${editingGroup.id}/tasks/${taskId}`)
                }

                toast.success('Task group template updated successfully')
                setEditingGroup(null)
            } else {
                // Create group
                const response = await api.post('/tasks/groups/templates', groupFormData)
                const newGroupId = response.data.id

                // Add selected tasks to the new group
                for (const taskId of selectedTaskIds) {
                    await api.post(`/tasks/groups/${newGroupId}/tasks/${taskId}`)
                }

                toast.success('Task group template created successfully')
                setShowGroupForm(false)
            }
            setGroupFormData({ title: '', description: '' })
            setSelectedTaskIds([])
            fetchData()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to save task group template')
        } finally {
            setSubmitting(false)
        }
    }

    const handleEditTask = (task: Task) => {
        setEditingTask(task)
        setTaskFormData({
            title: task.title,
            description: task.description || '',
        })
        fetchTaskResources(task.id)
    }

    const fetchTaskResources = async (taskId: number) => {
        try {
            const response = await api.get(`/tasks/templates/${taskId}/resources`)
            setResources(response.data)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to fetch resources')
        }
    }

    const fetchGroupResources = async (groupId: number) => {
        try {
            const response = await api.get(`/tasks/groups/templates/${groupId}/resources`)
            setGroupResources(response.data)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to fetch group resources')
        }
    }

    const handleResourceInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target
        setResourceFormData(prev => ({ ...prev, [name]: value }))
    }

    const handleAddResource = () => {
        setShowResourceForm(true)
        setEditingResource(null)
        setResourceFormData({
            title: '',
            description: '',
            resource_type: 'LINK',
            content: '',
        })
    }

    const handleEditResource = (resource: TaskResource) => {
        setEditingResource(resource)
        setShowResourceForm(true)
        setResourceFormData({
            title: resource.title,
            description: resource.description || '',
            resource_type: resource.resource_type,
            content: resource.content,
        })
    }

    const handleSaveResource = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!editingTask) return

        setSubmitting(true)
        try {
            if (editingResource) {
                await api.put(`/tasks/templates/${editingTask.id}/resources/${editingResource.id}`, resourceFormData)
                toast.success('Resource updated successfully!')
            } else {
                await api.post(`/tasks/templates/${editingTask.id}/resources`, resourceFormData)
                toast.success('Resource added successfully!')
            }
            setShowResourceForm(false)
            setEditingResource(null)
            setResourceFormData({ title: '', description: '', resource_type: 'LINK', content: '' })
            fetchTaskResources(editingTask.id)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to save resource')
        } finally {
            setSubmitting(false)
        }
    }

    const handleDeleteResource = async (resourceId: number) => {
        if (!editingTask) return
        if (!confirm('Are you sure you want to delete this resource?')) return

        try {
            await api.delete(`/tasks/templates/${editingTask.id}/resources/${resourceId}`)
            toast.success('Resource deleted successfully!')
            fetchTaskResources(editingTask.id)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to delete resource')
        }
    }

    // Group Resource handlers
    const handleGroupResourceInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target
        setGroupResourceFormData(prev => ({ ...prev, [name]: value }))
    }

    const handleSaveGroupResource = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!editingGroup) return

        setSubmitting(true)
        try {
            if (editingGroupResource) {
                await api.put(`/tasks/groups/templates/${editingGroup.id}/resources/${editingGroupResource.id}`, groupResourceFormData)
                toast.success('Resource updated successfully!')
            } else {
                await api.post(`/tasks/groups/templates/${editingGroup.id}/resources`, groupResourceFormData)
                toast.success('Resource added successfully!')
            }
            setShowGroupResourceForm(false)
            setEditingGroupResource(null)
            setGroupResourceFormData({ title: '', description: '', resource_type: 'LINK', content: '' })
            fetchGroupResources(editingGroup.id)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to save resource')
        } finally {
            setSubmitting(false)
        }
    }

    const handleDeleteGroupResource = async (resourceId: number) => {
        if (!editingGroup) return
        if (!confirm('Are you sure you want to delete this resource?')) return

        try {
            await api.delete(`/tasks/groups/templates/${editingGroup.id}/resources/${resourceId}`)
            toast.success('Resource deleted successfully!')
            fetchGroupResources(editingGroup.id)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to delete resource')
        }
    }

    const handleEditGroup = (group: TaskGroup) => {
        setEditingGroup(group)
        setGroupFormData({
            title: group.title,
            description: group.description || '',
        })
        setSelectedTaskIds(group.tasks?.map(t => t.id) || [])
        fetchGroupResources(group.id)
    }

    const cancelTaskEdit = () => {
        setEditingTask(null)
        setTaskFormData({ title: '', description: '' })
        setResources([])
        setShowResourceForm(false)
        setEditingResource(null)
    }

    const cancelResourceForm = () => {
        setShowResourceForm(false)
        setEditingResource(null)
        setResourceFormData({ title: '', description: '', resource_type: 'LINK', content: '' })
    }

    const cancelGroupEdit = () => {
        setEditingGroup(null)
        setGroupFormData({ title: '', description: '' })
        setSelectedTaskIds([])
        setGroupResources([])
        setShowGroupResourceForm(false)
        setEditingGroupResource(null)
    }

    // Drag and drop handlers
    const handleDragStart = (task: Task) => (e: React.DragEvent) => {
        setDraggedTask(task)
        e.dataTransfer.effectAllowed = 'copy'
    }

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault()
        e.dataTransfer.dropEffect = 'copy'
    }

    const handleDrop = async (group: TaskGroup) => async (e: React.DragEvent) => {
        e.preventDefault()
        if (!draggedTask) return

        try {
            await api.post(`/tasks/groups/${group.id}/tasks/${draggedTask.id}`)
            toast.success(`"${draggedTask.title}" added to "${group.title}"`)
            fetchData()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to add task to group')
        } finally {
            setDraggedTask(null)
        }
    }

    const handleRemoveTaskFromGroup = async (groupId: number, taskId: number, taskTitle: string) => {
        if (!confirm(`Remove "${taskTitle}" from this group?`)) return

        try {
            await api.delete(`/tasks/groups/${groupId}/tasks/${taskId}`)
            toast.success('Task removed from group')
            fetchData()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to remove task from group')
        }
    }

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="text-gray-500">Loading templates...</div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <DemoLimitsBanner />

            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Task Templates</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Create reusable task and task group templates for POCs
                    </p>
                </div>
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                    <button
                        onClick={() => setActiveTab('tasks')}
                        className={`${activeTab === 'tasks'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                    >
                        Task Templates ({tasks.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('groups')}
                        className={`${activeTab === 'groups'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                    >
                        Task Group Templates ({taskGroups.length})
                    </button>
                </nav>
            </div>

            {/* Task Templates Tab */}
            {activeTab === 'tasks' && (
                <div className="space-y-6">
                    <div className="flex justify-end">
                        <button
                            onClick={() => setShowTaskForm(!showTaskForm)}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            {showTaskForm ? 'Cancel' : '+ New Task Template'}
                        </button>
                    </div>

                    {showTaskForm && (
                        <div className="bg-white rounded-lg shadow-md p-6">
                            <h2 className="text-xl font-semibold mb-4">Create Task Template</h2>
                            <form onSubmit={handleCreateTask} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Task Title *
                                    </label>
                                    <input
                                        type="text"
                                        name="title"
                                        required
                                        value={taskFormData.title}
                                        onChange={handleTaskInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="e.g., Setup Development Environment"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Description
                                    </label>
                                    <textarea
                                        name="description"
                                        rows={4}
                                        value={taskFormData.description}
                                        onChange={handleTaskInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="Detailed description of the task..."
                                    />
                                </div>
                                <div className="flex justify-end gap-3">
                                    <button
                                        type="button"
                                        onClick={() => setShowTaskForm(false)}
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
                                        {submitting ? 'Creating...' : 'Create Template'}
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}

                    {/* Tasks List */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {tasks.length === 0 ? (
                            <div className="col-span-full text-center py-12 bg-white rounded-lg shadow">
                                <svg
                                    className="mx-auto h-12 w-12 text-gray-400"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                                    />
                                </svg>
                                <h3 className="mt-2 text-sm font-medium text-gray-900">No task templates</h3>
                                <p className="mt-1 text-sm text-gray-500">
                                    Get started by creating a new task template.
                                </p>
                            </div>
                        ) : (
                            tasks.map((task) => (
                                <div
                                    key={task.id}
                                    draggable
                                    onDragStart={handleDragStart(task)}
                                    className="bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-shadow cursor-move border-2 border-transparent hover:border-blue-300"
                                >
                                    <div className="flex justify-between items-start mb-3">
                                        <div className="flex items-center gap-2 flex-1">
                                            <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" />
                                            </svg>
                                            <h3 className="text-lg font-semibold text-gray-900">
                                                {task.title}
                                            </h3>
                                        </div>
                                        <button
                                            onClick={() => handleEditTask(task)}
                                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                                        >
                                            Edit
                                        </button>
                                    </div>
                                    {task.description && (
                                        <p className="text-sm text-gray-600 mb-3 line-clamp-3">
                                            {task.description}
                                        </p>
                                    )}
                                    <div className="text-xs text-gray-500">
                                        Created {new Date(task.created_at).toLocaleDateString()}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}

            {/* Task Group Templates Tab */}
            {activeTab === 'groups' && (
                <div className="space-y-6">
                    <div className="flex justify-end">
                        <button
                            onClick={() => setShowGroupForm(!showGroupForm)}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            {showGroupForm ? 'Cancel' : '+ New Task Group Template'}
                        </button>
                    </div>

                    {showGroupForm && (
                        <div className="bg-white rounded-lg shadow-md p-6">
                            <h2 className="text-xl font-semibold mb-4">Create Task Group Template</h2>
                            <form onSubmit={handleCreateGroup} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Group Title *
                                    </label>
                                    <input
                                        type="text"
                                        name="title"
                                        required
                                        value={groupFormData.title}
                                        onChange={handleGroupInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="e.g., Initial Setup"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Description
                                    </label>
                                    <textarea
                                        name="description"
                                        rows={4}
                                        value={groupFormData.description}
                                        onChange={handleGroupInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="Description of this task group..."
                                    />
                                </div>

                                {/* Task Selection */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Select Tasks (optional)
                                    </label>
                                    <div className="border border-gray-300 rounded-lg p-3 max-h-60 overflow-y-auto space-y-2">
                                        {tasks.length === 0 ? (
                                            <p className="text-sm text-gray-500 text-center py-4">No task templates available</p>
                                        ) : (
                                            tasks.map((task) => (
                                                <label
                                                    key={task.id}
                                                    className="flex items-start gap-3 p-2 hover:bg-gray-50 rounded cursor-pointer"
                                                >
                                                    <input
                                                        type="checkbox"
                                                        checked={selectedTaskIds.includes(task.id)}
                                                        onChange={(e) => {
                                                            if (e.target.checked) {
                                                                setSelectedTaskIds([...selectedTaskIds, task.id])
                                                            } else {
                                                                setSelectedTaskIds(selectedTaskIds.filter(id => id !== task.id))
                                                            }
                                                        }}
                                                        className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                                    />
                                                    <div className="flex-1">
                                                        <div className="text-sm font-medium text-gray-900">{task.title}</div>
                                                        {task.description && (
                                                            <div className="text-xs text-gray-500 mt-1 line-clamp-2">{task.description}</div>
                                                        )}
                                                    </div>
                                                </label>
                                            ))
                                        )}
                                    </div>
                                    {selectedTaskIds.length > 0 && (
                                        <p className="text-xs text-gray-600 mt-2">
                                            {selectedTaskIds.length} task{selectedTaskIds.length !== 1 ? 's' : ''} selected
                                        </p>
                                    )}
                                </div>

                                <div className="flex justify-end gap-3">
                                    <button
                                        type="button"
                                        onClick={() => setShowGroupForm(false)}
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
                                        {submitting ? 'Creating...' : 'Create Template'}
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}

                    {/* Task Groups List */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {taskGroups.length === 0 ? (
                            <div className="col-span-full text-center py-12 bg-white rounded-lg shadow">
                                <svg
                                    className="mx-auto h-12 w-12 text-gray-400"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                                    />
                                </svg>
                                <h3 className="mt-2 text-sm font-medium text-gray-900">No task group templates</h3>
                                <p className="mt-1 text-sm text-gray-500">
                                    Get started by creating a new task group template.
                                </p>
                            </div>
                        ) : (
                            taskGroups.map((group) => (
                                <div
                                    key={group.id}
                                    className={`bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-all border-2 ${draggedTask ? 'border-dashed border-blue-400' : 'border-transparent'
                                        }`}
                                    onDragOver={handleDragOver}
                                    onDrop={(e) => handleDrop(e, group)}
                                >
                                    <div className="flex justify-between items-start mb-3">
                                        <h3 className="text-lg font-semibold text-gray-900 flex-1">
                                            {group.title}
                                        </h3>
                                        <button
                                            onClick={() => handleEditGroup(group)}
                                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                                        >
                                            Edit
                                        </button>
                                    </div>
                                    {group.description && (
                                        <p className="text-sm text-gray-600 mb-3 line-clamp-3">
                                            {group.description}
                                        </p>
                                    )}

                                    {/* Tasks in this group */}
                                    {group.tasks && group.tasks.length > 0 && (
                                        <div className="mt-4 pt-4 border-t border-gray-200">
                                            <h4 className="text-sm font-medium text-gray-700 mb-2">
                                                Tasks ({group.tasks.length})
                                            </h4>
                                            <div className="space-y-2">
                                                {group.tasks.map((task) => (
                                                    <div
                                                        key={task.id}
                                                        className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded text-sm"
                                                    >
                                                        <span className="text-gray-700 flex-1 truncate">
                                                            {task.title}
                                                        </span>
                                                        <button
                                                            onClick={() => handleRemoveTaskFromGroup(group.id, task.id)}
                                                            className="text-red-600 hover:text-red-800 ml-2 flex-shrink-0"
                                                            title="Remove task from group"
                                                        >
                                                            <svg
                                                                className="w-4 h-4"
                                                                fill="none"
                                                                stroke="currentColor"
                                                                viewBox="0 0 24 24"
                                                            >
                                                                <path
                                                                    strokeLinecap="round"
                                                                    strokeLinejoin="round"
                                                                    strokeWidth={2}
                                                                    d="M6 18L18 6M6 6l12 12"
                                                                />
                                                            </svg>
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Drop zone hint when dragging */}
                                    {draggedTask && (!group.tasks || group.tasks.length === 0) && (
                                        <div className="mt-4 pt-4 border-t border-gray-200 text-center text-sm text-gray-500 italic">
                                            Drop task here
                                        </div>
                                    )}

                                    <div className="text-xs text-gray-500 mt-3">
                                        Created {new Date(group.created_at).toLocaleDateString()}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}

            {/* Edit Task Modal */}
            {editingTask && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
                    <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                        <div className="border-b px-6 py-4 flex justify-between items-center sticky top-0 bg-white z-10">
                            <h2 className="text-xl font-bold text-gray-900">Edit Task Template</h2>
                            <button
                                onClick={cancelTaskEdit}
                                className="text-gray-400 hover:text-gray-500"
                            >
                                <span className="text-2xl">&times;</span>
                            </button>
                        </div>
                        <div className="p-6 space-y-6">
                            {/* Task Details Form */}
                            <form onSubmit={handleUpdateTask} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Task Title *
                                    </label>
                                    <input
                                        type="text"
                                        name="title"
                                        required
                                        value={taskFormData.title}
                                        onChange={handleTaskInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Description
                                    </label>
                                    <textarea
                                        name="description"
                                        rows={4}
                                        value={taskFormData.description}
                                        onChange={handleTaskInputChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    />
                                </div>
                                <div className="flex justify-end gap-3 pt-4 border-t">
                                    <button
                                        type="submit"
                                        disabled={submitting}
                                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-blue-400"
                                    >
                                        {submitting ? 'Updating...' : 'Update Template'}
                                    </button>
                                </div>
                            </form>

                            {/* Resources Section */}
                            <div className="border-t pt-6">
                                <div className="flex justify-between items-center mb-4">
                                    <h3 className="text-lg font-semibold text-gray-900">Resources</h3>
                                    <button
                                        onClick={handleAddResource}
                                        className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
                                    >
                                        + Add Resource
                                    </button>
                                </div>

                                {/* Resource Form */}
                                {showResourceForm && (
                                    <div className="bg-white border-2 border-blue-200 p-4 rounded-lg mb-4">
                                        <h4 className="font-medium text-gray-900 mb-3">
                                            {editingResource ? 'Edit Resource' : 'New Resource'}
                                        </h4>
                                        <form onSubmit={handleSaveResource} className="space-y-3">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Resource Type *
                                                </label>
                                                <select
                                                    name="resource_type"
                                                    value={resourceFormData.resource_type}
                                                    onChange={handleResourceInputChange}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                >
                                                    <option value="LINK">Link</option>
                                                    <option value="CODE">Code Snippet</option>
                                                    <option value="TEXT">Text Note</option>
                                                    <option value="FILE">File Reference</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Title *
                                                </label>
                                                <input
                                                    type="text"
                                                    name="title"
                                                    required
                                                    value={resourceFormData.title}
                                                    onChange={handleResourceInputChange}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                    placeholder="e.g., Setup Guide, Sample Code, Documentation Link"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Description
                                                </label>
                                                <input
                                                    type="text"
                                                    name="description"
                                                    value={resourceFormData.description}
                                                    onChange={handleResourceInputChange}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                    placeholder="Brief description of the resource"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    {resourceFormData.resource_type === 'LINK' ? 'URL *' :
                                                        resourceFormData.resource_type === 'CODE' ? 'Code *' :
                                                            resourceFormData.resource_type === 'TEXT' ? 'Text Content *' :
                                                                'File Path *'}
                                                </label>
                                                <textarea
                                                    name="content"
                                                    required
                                                    rows={resourceFormData.resource_type === 'LINK' ? 2 : 6}
                                                    value={resourceFormData.content}
                                                    onChange={handleResourceInputChange}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                                                    placeholder={
                                                        resourceFormData.resource_type === 'LINK' ? 'https://example.com/documentation' :
                                                            resourceFormData.resource_type === 'CODE' ? '// Enter code snippet here' :
                                                                resourceFormData.resource_type === 'TEXT' ? 'Enter your text content...' :
                                                                    '/path/to/file.pdf'
                                                    }
                                                />
                                            </div>
                                            <div className="flex justify-end gap-2">
                                                <button
                                                    type="button"
                                                    onClick={cancelResourceForm}
                                                    className="px-4 py-2 border border-gray-300 text-gray-700 text-sm rounded-lg hover:bg-gray-50 transition-colors"
                                                    disabled={submitting}
                                                >
                                                    Cancel
                                                </button>
                                                <button
                                                    type="submit"
                                                    disabled={submitting}
                                                    className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors disabled:bg-blue-400"
                                                >
                                                    {submitting ? 'Saving...' : editingResource ? 'Update' : 'Add'}
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                )}

                                {/* Resources List */}
                                <div className="space-y-3">
                                    {resources.length === 0 ? (
                                        <div className="text-center py-8 text-gray-600 bg-white border-2 border-dashed border-gray-300 rounded-lg">
                                            No resources added yet
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
                                                    <div className="flex gap-2">
                                                        <button
                                                            onClick={() => handleEditResource(resource)}
                                                            className="text-blue-600 hover:text-blue-800 text-sm"
                                                        >
                                                            Edit
                                                        </button>
                                                        <button
                                                            onClick={() => handleDeleteResource(resource.id)}
                                                            className="text-red-600 hover:text-red-800 text-sm"
                                                        >
                                                            Delete
                                                        </button>
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
                        </div>
                    </div>
                </div>
            )}

            {/* Edit Group Modal */}
            {editingGroup && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-start justify-center py-8">
                    <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[calc(100vh-4rem)] overflow-y-auto">
                        <div className="border-b px-6 py-4 flex justify-between items-center sticky top-0 bg-white z-10">
                            <h2 className="text-xl font-bold text-gray-900">Edit Task Group Template</h2>
                            <button
                                onClick={cancelGroupEdit}
                                className="text-gray-400 hover:text-gray-500"
                            >
                                <span className="text-2xl">&times;</span>
                            </button>
                        </div>
                        <form onSubmit={handleCreateGroup} className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Group Title *
                                </label>
                                <input
                                    type="text"
                                    name="title"
                                    required
                                    value={groupFormData.title}
                                    onChange={handleGroupInputChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Description
                                </label>
                                <textarea
                                    name="description"
                                    rows={4}
                                    value={groupFormData.description}
                                    onChange={handleGroupInputChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                            </div>

                            {/* Task Selection */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Select Tasks
                                </label>
                                <div className="border border-gray-300 rounded-lg p-3 max-h-60 overflow-y-auto space-y-2">
                                    {tasks.length === 0 ? (
                                        <p className="text-sm text-gray-500 text-center py-4">No task templates available</p>
                                    ) : (
                                        tasks.map((task) => (
                                            <label
                                                key={task.id}
                                                className="flex items-start gap-3 p-2 hover:bg-gray-50 rounded cursor-pointer"
                                            >
                                                <input
                                                    type="checkbox"
                                                    checked={selectedTaskIds.includes(task.id)}
                                                    onChange={(e) => {
                                                        if (e.target.checked) {
                                                            setSelectedTaskIds([...selectedTaskIds, task.id])
                                                        } else {
                                                            setSelectedTaskIds(selectedTaskIds.filter(id => id !== task.id))
                                                        }
                                                    }}
                                                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                                />
                                                <div className="flex-1">
                                                    <div className="text-sm font-medium text-gray-900">{task.title}</div>
                                                    {task.description && (
                                                        <div className="text-xs text-gray-500 mt-1 line-clamp-2">{task.description}</div>
                                                    )}
                                                </div>
                                            </label>
                                        ))
                                    )}
                                </div>
                                {selectedTaskIds.length > 0 && (
                                    <p className="text-xs text-gray-600 mt-2">
                                        {selectedTaskIds.length} task{selectedTaskIds.length !== 1 ? 's' : ''} selected
                                    </p>
                                )}
                            </div>

                            {/* Resources Section */}
                            <div className="border-t pt-4">
                                <div className="flex justify-between items-center mb-3">
                                    <h3 className="text-lg font-semibold text-gray-900">Resources</h3>
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setShowGroupResourceForm(true)
                                            setEditingGroupResource(null)
                                            setGroupResourceFormData({ title: '', description: '', resource_type: 'LINK', content: '' })
                                        }}
                                        className="px-3 py-1 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                                    >
                                        + Add Resource
                                    </button>
                                </div>

                                {/* Resource Form */}
                                {showGroupResourceForm && (
                                    <div className="bg-gray-50 p-4 rounded-lg mb-4 space-y-3">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Resource Type *
                                            </label>
                                            <select
                                                name="resource_type"
                                                required
                                                value={groupResourceFormData.resource_type}
                                                onChange={handleGroupResourceInputChange}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                            >
                                                <option value="LINK">Link</option>
                                                <option value="CODE">Code</option>
                                                <option value="TEXT">Text</option>
                                                <option value="FILE">File</option>
                                            </select>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Title *
                                            </label>
                                            <input
                                                type="text"
                                                name="title"
                                                required
                                                value={groupResourceFormData.title}
                                                onChange={handleGroupResourceInputChange}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Description
                                            </label>
                                            <textarea
                                                name="description"
                                                rows={2}
                                                value={groupResourceFormData.description}
                                                onChange={handleGroupResourceInputChange}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Content *
                                            </label>
                                            <textarea
                                                name="content"
                                                rows={3}
                                                required
                                                value={groupResourceFormData.content}
                                                onChange={handleGroupResourceInputChange}
                                                placeholder={
                                                    groupResourceFormData.resource_type === 'LINK' ? 'https://example.com' :
                                                        groupResourceFormData.resource_type === 'CODE' ? 'Code snippet here...' :
                                                            'Content here...'
                                                }
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                                            />
                                        </div>
                                        <div className="flex gap-2">
                                            <button
                                                type="button"
                                                onClick={(e) => {
                                                    e.preventDefault()
                                                    handleSaveGroupResource(e as any)
                                                }}
                                                disabled={submitting || !groupResourceFormData.title || !groupResourceFormData.content}
                                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                                            >
                                                {submitting ? 'Saving...' : editingGroupResource ? 'Update' : 'Add'}
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    setShowGroupResourceForm(false)
                                                    setEditingGroupResource(null)
                                                    setGroupResourceFormData({ title: '', description: '', resource_type: 'LINK', content: '' })
                                                }}
                                                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </div>
                                )}

                                {/* Resources List */}
                                <div className="space-y-2">
                                    {groupResources.length === 0 ? (
                                        <p className="text-sm text-gray-500 text-center py-4 bg-gray-50 rounded-lg">
                                            No resources added yet
                                        </p>
                                    ) : (
                                        groupResources.map((resource) => (
                                            <div key={resource.id} className="bg-white border border-gray-200 rounded-lg p-3">
                                                <div className="flex justify-between items-start">
                                                    <div className="flex-1">
                                                        <div className="flex items-center gap-2 mb-1">
                                                            <span className="inline-block px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                                                                {resource.resource_type}
                                                            </span>
                                                            <h4 className="font-medium text-gray-900">{resource.title}</h4>
                                                        </div>
                                                        {resource.description && (
                                                            <p className="text-sm text-gray-600 mb-2">{resource.description}</p>
                                                        )}
                                                        <div className="text-sm text-gray-700 bg-gray-50 p-2 rounded font-mono break-all">
                                                            {resource.resource_type === 'LINK' ? (
                                                                <a href={resource.content} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                                                    {resource.content}
                                                                </a>
                                                            ) : (
                                                                resource.content
                                                            )}
                                                        </div>
                                                    </div>
                                                    <div className="flex gap-2 ml-3">
                                                        <button
                                                            type="button"
                                                            onClick={() => {
                                                                setEditingGroupResource(resource)
                                                                setGroupResourceFormData(resource)
                                                                setShowGroupResourceForm(true)
                                                            }}
                                                            className="text-blue-600 hover:text-blue-800 text-sm"
                                                        >
                                                            Edit
                                                        </button>
                                                        <button
                                                            type="button"
                                                            onClick={() => handleDeleteGroupResource(resource.id)}
                                                            className="text-red-600 hover:text-red-800 text-sm"
                                                        >
                                                            Delete
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>

                            <div className="flex justify-end gap-3 pt-4 border-t">
                                <button
                                    type="button"
                                    onClick={cancelGroupEdit}
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
                                    {submitting ? 'Updating...' : 'Update Template'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    )
}
