import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import toast from 'react-hot-toast'
import { useAuthStore } from '../store/authStore'
import { useNavigate } from 'react-router-dom'
import CommentsModal from './CommentsModal'
import LogoUpload from './LogoUpload'
import ResourcesModal from './ResourcesModal'
import TaskAssignmentModal from './TaskAssignmentModal'

interface Product {
    id: number
    name: string
}

interface POCFormData {
    title: string
    description: string
    customer_company_name: string
    executive_summary: string
    objectives: string
    start_date: string
    end_date: string
    product_ids: number[]
}

interface SuccessCriteria {
    id?: number
    title: string
    description: string | null
    target_value: string | null
    importance_level: number
    sort_order: number
}

interface Participant {
    id?: number
    user_id?: number
    email?: string
    full_name?: string
    is_sales_engineer: boolean
    is_customer: boolean
    joined_at?: string
    status?: string
    invitation_id?: number
    invited_at?: string
    expires_at?: string
    resend_count?: number
}

interface TaskAssignee {
    id: number
    participant_id: number
    participant_name: string
    participant_email: string
    assigned_at: string
}

interface POCTask {
    id?: number
    title: string
    description: string | null
    task_id?: number
    success_criteria_ids: number[]
    sort_order: number
    status?: string
    start_date?: string
    due_date?: string
    assignees?: TaskAssignee[]
}

interface POCTaskGroup {
    id?: number
    title: string
    description: string | null
    task_group_id?: number
    success_criteria_ids: number[]
    sort_order: number
    status?: string
    start_date?: string
    due_date?: string
    tasks?: POCTask[]
}

interface POCFormProps {
    pocId?: number
    initialData?: any
    onClose?: () => void
}

export default function POCForm({ pocId, initialData, onClose }: POCFormProps) {
    const { user } = useAuthStore()
    const navigate = useNavigate()
    const [loading, setLoading] = useState(false)
    const [products, setProducts] = useState<Product[]>([])
    const [users, setUsers] = useState<any[]>([])
    const [taskTemplates, setTaskTemplates] = useState<any[]>([])
    const [taskGroupTemplates, setTaskGroupTemplates] = useState<any[]>([])
    const [activeTab, setActiveTab] = useState<'dashboard' | 'basic' | 'criteria' | 'tasks' | 'participants' | 'resources'>(pocId ? 'dashboard' : 'basic')

    // Basic Info
    const [formData, setFormData] = useState<POCFormData>({
        title: '',
        description: '',
        customer_company_name: '',
        executive_summary: '',
        objectives: '',
        start_date: '',
        end_date: '',
        product_ids: []
    })

    // Customer Logo
    const [customerLogoUrl, setCustomerLogoUrl] = useState<string | null>(null)

    // Success Criteria
    const [successCriteria, setSuccessCriteria] = useState<SuccessCriteria[]>([])
    const [newCriteria, setNewCriteria] = useState<SuccessCriteria>({
        title: '',
        description: '',
        target_value: '',
        importance_level: 3,
        sort_order: 0
    })

    // Participants
    const [participants, setParticipants] = useState<Participant[]>([])
    const [newParticipant, setNewParticipant] = useState<Participant>({
        email: '',
        full_name: '',
        is_sales_engineer: false,
        is_customer: false
    })

    // Resources
    const [resources, setResources] = useState<any[]>([])
    const [showResourceModal, setShowResourceModal] = useState(false)
    const [newResource, setNewResource] = useState({
        title: '',
        description: '',
        resource_type: 'LINK' as 'LINK' | 'CODE' | 'TEXT' | 'FILE',
        content: '',
        success_criteria_id: null as number | null,
        sort_order: 0
    })

    // Document Generation
    const [showDocumentModal, setShowDocumentModal] = useState(false)
    const [generatingDocument, setGeneratingDocument] = useState(false)

    // Tasks and Task Groups
    const [pocTasks, setPocTasks] = useState<POCTask[]>([])
    const [pocTaskGroups, setPocTaskGroups] = useState<POCTaskGroup[]>([])
    const [expandedGroups, setExpandedGroups] = useState<Set<number>>(new Set())
    const [newTask, setNewTask] = useState<POCTask>({
        title: '',
        description: '',
        success_criteria_ids: [],
        sort_order: 0,
        start_date: '',
        due_date: formData.end_date || ''
    })
    const [newTaskGroup, setNewTaskGroup] = useState<POCTaskGroup>({
        title: '',
        description: '',
        success_criteria_ids: [],
        sort_order: 0,
        start_date: '',
        due_date: formData.end_date || ''
    })
    const [showTaskForm, setShowTaskForm] = useState(false)
    const [showTaskGroupForm, setShowTaskGroupForm] = useState(false)

    // Comments Modal
    const [showCommentsModal, setShowCommentsModal] = useState(false)
    const [commentsModalTaskId, setCommentsModalTaskId] = useState<number | undefined>()
    const [commentsModalTaskGroupId, setCommentsModalTaskGroupId] = useState<number | undefined>()

    // Task Resources Modal
    const [showResourcesModal, setShowResourcesModal] = useState(false)
    const [resourcesModalTaskId, setResourcesModalTaskId] = useState<number | undefined>()
    const [resourcesModalTaskGroupId, setResourcesModalTaskGroupId] = useState<number | undefined>()
    const [resourcesModalTitle, setResourcesModalTitle] = useState('')

    // Task Assignment Modal
    const [showAssignmentModal, setShowAssignmentModal] = useState(false)
    const [assignmentModalTask, setAssignmentModalTask] = useState<POCTask | null>(null)

    // Status Comment Modal (for Partially Satisfied / Not Satisfied)
    const [showStatusCommentModal, setShowStatusCommentModal] = useState(false)
    const [statusCommentText, setStatusCommentText] = useState('')
    const [pendingStatusChange, setPendingStatusChange] = useState<{ type: 'task' | 'taskGroup'; id: number; status: string } | null>(null)

    // Criteria Edit Modal
    const [showCriteriaEditModal, setShowCriteriaEditModal] = useState(false)
    const [criteriaEditTaskId, setCriteriaEditTaskId] = useState<number | null>(null)
    const [criteriaEditSelectedIds, setCriteriaEditSelectedIds] = useState<number[]>([])

    // Criteria Task List Modal
    const [showCriteriaTaskListModal, setShowCriteriaTaskListModal] = useState(false)
    const [criteriaTaskListTitle, setCriteriaTaskListTitle] = useState('')
    const [criteriaTaskListNames, setCriteriaTaskListNames] = useState<string[]>([])

    // Helper function to format API errors
    const formatErrorMessage = (error: any, defaultMessage: string): string => {
        if (!error.response?.data) return defaultMessage

        const detail = error.response.data.detail

        // If detail is a string, return it
        if (typeof detail === 'string') return detail

        // If detail is an array of validation errors
        if (Array.isArray(detail)) {
            return detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ')
        }

        // If detail is an object, try to extract message
        if (typeof detail === 'object' && detail.msg) {
            return detail.msg
        }

        return defaultMessage
    }

    useEffect(() => {
        fetchProducts()
        fetchUsers()
        fetchTaskTemplates()
        fetchTaskGroupTemplates()
        if (pocId) {
            fetchPOCData()
        }
        if (initialData) {
            setFormData({
                ...formData,
                ...initialData
            })
        }
    }, [pocId])

    const fetchProducts = async () => {
        try {
            const response = await api.get('/products/')
            setProducts(response.data)
        } catch (error) {
            console.error('Failed to fetch products:', error)
        }
    }

    const fetchUsers = async () => {
        try {
            const response = await api.get('/users/')
            setUsers(response.data)
        } catch (error) {
            console.error('Failed to fetch users:', error)
        }
    }

    const fetchTaskTemplates = async () => {
        try {
            const response = await api.get('/tasks/templates')
            setTaskTemplates(response.data)
        } catch (error) {
            console.error('Failed to fetch task templates:', error)
        }
    }

    const fetchTaskGroupTemplates = async () => {
        try {
            const response = await api.get('/tasks/groups/templates')
            setTaskGroupTemplates(response.data)
        } catch (error) {
            console.error('Failed to fetch task group templates:', error)
        }
    }

    const fetchPOCData = async () => {
        if (!pocId) return
        try {
            const [pocResponse, criteriaResponse, participantsResponse, resourcesResponse] = await Promise.all([
                api.get(`/pocs/${pocId}`),
                api.get(`/pocs/${pocId}/success-criteria`),
                api.get(`/pocs/${pocId}/participants`),
                api.get(`/pocs/${pocId}/resources`),
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
            setCustomerLogoUrl(poc.customer_logo_url || null)
            setSuccessCriteria(criteriaResponse.data || [])
            setParticipants(participantsResponse.data || [])
            setResources(resourcesResponse.data || [])

            // Fetch tasks and task groups separately to avoid breaking the entire load
            try {
                const tasksResponse = await api.get(`/tasks/pocs/${pocId}/tasks`)
                const tasks = tasksResponse.data || []
                console.log('Tasks loaded:', tasks)
                setPocTasks(tasks)
            } catch (taskError: any) {
                console.error('Failed to fetch tasks:', taskError)
                setPocTasks([])
            }

            try {
                const taskGroupsResponse = await api.get(`/tasks/pocs/${pocId}/task-groups`)
                const taskGroups = taskGroupsResponse.data || []
                console.log('Task Groups loaded:', taskGroups)
                setPocTaskGroups(taskGroups)
            } catch (groupError: any) {
                console.error('Failed to fetch task groups:', groupError)
                setPocTaskGroups([])
            }
        } catch (error: any) {
            toast.error('Failed to fetch POC data')
        }
    }

    const handleInputChange = (field: keyof POCFormData, value: any) => {
        setFormData({ ...formData, [field]: value })
    }

    const handleProductToggle = (productId: number) => {
        const newProductIds = formData.product_ids.includes(productId)
            ? formData.product_ids.filter(id => id !== productId)
            : [...formData.product_ids, productId]
        setFormData({ ...formData, product_ids: newProductIds })
    }

    const handleSubmitBasicInfo = async () => {
        if (!formData.title || !formData.customer_company_name) {
            toast.error('Please fill in required fields')
            return
        }

        setLoading(true)
        try {
            if (pocId) {
                await api.put(`/pocs/${pocId}`, formData)
                toast.success('POC updated successfully')
            } else {
                const response = await api.post('/pocs/', formData)
                toast.success('POC created successfully')
                navigate(`/pocs/${response.data.id}`)
            }
        } catch (error: any) {
            toast.error(formatErrorMessage(error, 'Failed to save POC'))
        } finally {
            setLoading(false)
        }
    }

    const handleAddCriteria = async () => {
        if (!newCriteria.title) {
            toast.error('Please enter a title for the success criteria')
            return
        }

        if (!pocId) {
            // Add to local state if POC not created yet
            setSuccessCriteria([...successCriteria, { ...newCriteria, id: Date.now() }])
            setNewCriteria({ title: '', description: '', target_value: '', importance_level: 3, sort_order: successCriteria.length })
            return
        }

        try {
            const response = await api.post(`/pocs/${pocId}/success-criteria`, {
                ...newCriteria,
                poc_id: pocId
            })
            setSuccessCriteria([...successCriteria, response.data])
            setNewCriteria({ title: '', description: '', target_value: '', importance_level: 3, sort_order: successCriteria.length })
            toast.success('Success criteria added')
        } catch (error: any) {
            toast.error('Failed to add success criteria')
        }
    }

    const handleDeleteCriteria = async (criteriaId: number) => {
        if (!pocId) {
            setSuccessCriteria(successCriteria.filter(c => c.id !== criteriaId))
            return
        }

        try {
            await api.delete(`/pocs/${pocId}/success-criteria/${criteriaId}`)
            setSuccessCriteria(successCriteria.filter(c => c.id !== criteriaId))
            toast.success('Success criteria deleted')
        } catch (error: any) {
            toast.error('Failed to delete success criteria')
        }
    }

    const handleAddParticipant = async () => {
        if (!newParticipant.user_id && !newParticipant.email) {
            toast.error('Please select a user or enter an email')
            return
        }

        if (!pocId) {
            setParticipants([...participants, { ...newParticipant }])
            setNewParticipant({ email: '', full_name: '', is_sales_engineer: false, is_customer: false })
            return
        }

        try {
            const response = await api.post(`/pocs/${pocId}/participants`, newParticipant)
            toast.success('Participant added')
            fetchPOCData()
            setNewParticipant({ email: '', full_name: '', is_sales_engineer: false, is_customer: false })
        } catch (error: any) {
            toast.error(formatErrorMessage(error, 'Failed to add participant'))
        }
    }

    const handleAddTaskFromTemplate = async (templateId: number) => {
        const template = taskTemplates.find(t => t.id === templateId)
        if (!template) return

        setNewTask({
            ...newTask,
            task_id: templateId,
            title: template.title,
            description: template.description || ''
        })
        setShowTaskForm(true)
    }

    const handleAddTask = async () => {
        if (!newTask.title) {
            toast.error('Please enter a task title')
            return
        }

        if (!pocId) {
            setPocTasks([...pocTasks, { ...newTask, id: Date.now(), sort_order: pocTasks.length }])
            setNewTask({ title: '', description: '', success_criteria_ids: [], sort_order: 0, start_date: '', due_date: formData.end_date || '' })
            setShowTaskForm(false)
            return
        }

        try {
            const payload = {
                ...newTask,
                start_date: newTask.start_date || null,
                due_date: newTask.due_date || null,
            }
            const response = await api.post(`/tasks/pocs/${pocId}/tasks`, payload)
            setPocTasks([...pocTasks, response.data])
            setNewTask({ title: '', description: '', success_criteria_ids: [], sort_order: 0, start_date: '', due_date: formData.end_date || '' })
            setShowTaskForm(false)
            toast.success('Task added')
        } catch (error: any) {
            toast.error('Failed to add task')
        }
    }

    const handleDeleteTask = async (taskId: number) => {
        if (!pocId) {
            setPocTasks(pocTasks.filter(t => t.id !== taskId))
            return
        }

        try {
            await api.delete(`/tasks/pocs/${pocId}/tasks/${taskId}`)
            setPocTasks(pocTasks.filter(t => t.id !== taskId))
            toast.success('Task deleted')
        } catch (error: any) {
            toast.error('Failed to delete task')
        }
    }

    const handleAddTaskGroupFromTemplate = async (templateId: number) => {
        const template = taskGroupTemplates.find(t => t.id === templateId)
        if (!template) return

        setNewTaskGroup({
            ...newTaskGroup,
            task_group_id: templateId,
            title: template.title,
            description: template.description || ''
        })
        setShowTaskGroupForm(true)
    }

    const handleAddTaskGroup = async () => {
        if (!newTaskGroup.title) {
            toast.error('Please enter a task group title')
            return
        }

        if (!pocId) {
            setPocTaskGroups([...pocTaskGroups, { ...newTaskGroup, id: Date.now(), sort_order: pocTaskGroups.length }])
            setNewTaskGroup({ title: '', description: '', success_criteria_ids: [], sort_order: 0, start_date: '', due_date: formData.end_date || '' })
            setShowTaskGroupForm(false)
            return
        }

        try {
            const payload = {
                ...newTaskGroup,
                start_date: newTaskGroup.start_date || null,
                due_date: newTaskGroup.due_date || null,
            }
            const response = await api.post(`/tasks/pocs/${pocId}/task-groups`, payload)
            setPocTaskGroups([...pocTaskGroups, response.data])
            setNewTaskGroup({ title: '', description: '', success_criteria_ids: [], sort_order: 0, start_date: '', due_date: formData.end_date || '' })
            setShowTaskGroupForm(false)
            toast.success('Task group added')
        } catch (error: any) {
            toast.error('Failed to add task group')
        }
    }

    const handleUpdateTaskStatus = async (taskId: number, newStatus: string) => {
        if (!pocId) return

        // If status requires a mandatory comment, show the modal
        if (newStatus === 'partially_satisfied' || newStatus === 'not_satisfied') {
            setPendingStatusChange({ type: 'task', id: taskId, status: newStatus })
            setStatusCommentText('')
            setShowStatusCommentModal(true)
            return
        }

        await applyTaskStatusChange(taskId, newStatus)
    }

    const applyTaskStatusChange = async (taskId: number, newStatus: string) => {
        if (!pocId) return

        try {
            await api.put(`/tasks/pocs/${pocId}/tasks/${taskId}`, { status: newStatus })

            // Update task in the main pocTasks array
            setPocTasks(pocTasks.map(t => t.id === taskId ? { ...t, status: newStatus } : t))

            // Also update task if it's nested in a task group
            setPocTaskGroups(pocTaskGroups.map(g => {
                if (g.tasks) {
                    return {
                        ...g,
                        tasks: g.tasks.map(t => t.id === taskId ? { ...t, status: newStatus } : t)
                    }
                }
                return g
            }))

            toast.success('Task status updated')
        } catch (error: any) {
            toast.error(formatErrorMessage(error, 'Failed to update task status'))
        }
    }

    const handleUpdateTaskDates = async (taskId: number, field: 'start_date' | 'due_date', value: string) => {
        if (!pocId) return
        try {
            const payload: any = { [field]: value || null }
            await api.put(`/tasks/pocs/${pocId}/tasks/${taskId}`, payload)
            const updated = { [field]: value || undefined }
            setPocTasks(pocTasks.map(t => t.id === taskId ? { ...t, ...updated } : t))
            setPocTaskGroups(pocTaskGroups.map(g => ({
                ...g,
                tasks: g.tasks?.map(t => t.id === taskId ? { ...t, ...updated } : t)
            })))
        } catch (error: any) {
            toast.error(formatErrorMessage(error, 'Failed to update task date'))
        }
    }

    const handleUpdateTaskGroupDates = async (groupId: number, field: 'start_date' | 'due_date', value: string) => {
        if (!pocId) return
        try {
            const payload: any = { [field]: value || null }
            await api.put(`/tasks/pocs/${pocId}/task-groups/${groupId}`, payload)
            const updated = { [field]: value || undefined }
            setPocTaskGroups(pocTaskGroups.map(g => g.id === groupId ? { ...g, ...updated } : g))
        } catch (error: any) {
            toast.error(formatErrorMessage(error, 'Failed to update task group date'))
        }
    }

    const handleOpenAssignmentModal = (task: POCTask) => {
        setAssignmentModalTask(task)
        setShowAssignmentModal(true)
    }

    const handleAssignmentComplete = async () => {
        // Refresh task data to get updated assignees
        if (pocId) {
            try {
                const response = await api.get(`/tasks/pocs/${pocId}/tasks`)
                setPocTasks(response.data || [])
            } catch (error: any) {
                toast.error('Failed to refresh task data')
            }
        }
    }

    const handleOpenCriteriaEdit = (task: POCTask) => {
        setCriteriaEditTaskId(task.id!)
        setCriteriaEditSelectedIds(task.success_criteria_ids || [])
        setShowCriteriaEditModal(true)
    }

    const handleSaveCriteriaEdit = async () => {
        if (!pocId || !criteriaEditTaskId) return
        try {
            await api.put(`/tasks/pocs/${pocId}/tasks/${criteriaEditTaskId}`, {
                success_criteria_ids: criteriaEditSelectedIds
            })
            setPocTasks(pocTasks.map(t =>
                t.id === criteriaEditTaskId
                    ? { ...t, success_criteria_ids: criteriaEditSelectedIds }
                    : t
            ))
            // Also update tasks inside groups
            setPocTaskGroups(pocTaskGroups.map(g => ({
                ...g,
                tasks: g.tasks?.map(t =>
                    t.id === criteriaEditTaskId
                        ? { ...t, success_criteria_ids: criteriaEditSelectedIds }
                        : t
                )
            })))
            setShowCriteriaEditModal(false)
            setCriteriaEditTaskId(null)
            toast.success('Success criteria updated')
        } catch (error: any) {
            toast.error(formatErrorMessage(error, 'Failed to update criteria'))
        }
    }

    const handleUpdateTaskGroupStatus = async (groupId: number, newStatus: string) => {
        if (!pocId) return

        // If status requires a mandatory comment, show the modal
        if (newStatus === 'partially_satisfied' || newStatus === 'not_satisfied') {
            setPendingStatusChange({ type: 'taskGroup', id: groupId, status: newStatus })
            setStatusCommentText('')
            setShowStatusCommentModal(true)
            return
        }

        await applyTaskGroupStatusChange(groupId, newStatus)
    }

    const applyTaskGroupStatusChange = async (groupId: number, newStatus: string) => {
        if (!pocId) return

        try {
            await api.put(`/tasks/pocs/${pocId}/task-groups/${groupId}`, { status: newStatus })
            setPocTaskGroups(pocTaskGroups.map(g => g.id === groupId ? { ...g, status: newStatus } : g))
        } catch (error: any) {
            alert(formatErrorMessage(error))
        }
    }

    const handleStatusCommentSubmit = async () => {
        if (!pocId || !pendingStatusChange || !statusCommentText.trim()) return

        try {
            const statusLabel = pendingStatusChange.status === 'partially_satisfied' ? 'Partially Satisfied' : 'Not Satisfied'
            const commentPayload: any = {
                subject: `Status changed to ${statusLabel}`,
                content: statusCommentText.trim(),
                is_internal: false,
            }

            if (pendingStatusChange.type === 'task') {
                commentPayload.poc_task_id = pendingStatusChange.id
                await applyTaskStatusChange(pendingStatusChange.id, pendingStatusChange.status)
            } else {
                commentPayload.poc_task_group_id = pendingStatusChange.id
                await applyTaskGroupStatusChange(pendingStatusChange.id, pendingStatusChange.status)
            }

            const queryParam = pendingStatusChange.type === 'task'
                ? `?task_id=${pendingStatusChange.id}`
                : `?task_group_id=${pendingStatusChange.id}`
            await api.post(`/pocs/${pocId}/comments${queryParam}`, commentPayload)

            setShowStatusCommentModal(false)
            setPendingStatusChange(null)
            setStatusCommentText('')
        } catch (error: any) {
            toast.error(formatErrorMessage(error, 'Failed to update status'))
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
            if (group && !group.tasks && pocId) {
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

    const handleDeleteTaskGroup = async (groupId: number) => {
        if (!pocId) {
            setPocTaskGroups(pocTaskGroups.filter(g => g.id !== groupId))
            return
        }

        try {
            await api.delete(`/tasks/pocs/${pocId}/task-groups/${groupId}`)
            setPocTaskGroups(pocTaskGroups.filter(g => g.id !== groupId))
            toast.success('Task group deleted')
        } catch (error: any) {
            toast.error('Failed to delete task group')
        }
    }

    const handleAddResource = async () => {
        if (!pocId) {
            toast.error('Please save the POC first before adding resources')
            return
        }

        if (!newResource.title.trim()) {
            toast.error('Resource title is required')
            return
        }

        if (!newResource.content.trim()) {
            toast.error('Resource content is required')
            return
        }

        try {
            const response = await api.post(`/pocs/${pocId}/resources`, newResource)
            setResources([...resources, response.data])
            setNewResource({
                title: '',
                description: '',
                resource_type: 'LINK',
                content: '',
                success_criteria_id: null,
                sort_order: 0
            })
            setShowResourceModal(false)
            toast.success('Resource added successfully')
        } catch (error: any) {
            toast.error('Failed to add resource')
        }
    }

    const handleDeleteResource = async (resourceId: number) => {
        try {
            await api.delete(`/pocs/${pocId}/resources/${resourceId}`)
            setResources(resources.filter(r => r.id !== resourceId))
            toast.success('Resource deleted')
        } catch (error: any) {
            toast.error('Failed to delete diagram')
        }
    }

    const handleGenerateDocument = async (format: 'pdf' | 'markdown') => {
        if (!pocId) {
            toast.error('Please save the POC first')
            return
        }

        setGeneratingDocument(true)
        try {
            const response = await api.get(`/pocs/${pocId}/generate-document?format=${format}`, {
                responseType: 'blob'
            })

            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `${formData.title || 'POC'}.${format === 'pdf' ? 'pdf' : 'md'}`)
            document.body.appendChild(link)
            link.click()
            link.remove()
            window.URL.revokeObjectURL(url)

            toast.success(`${format.toUpperCase()} document generated successfully`)
            setShowDocumentModal(false)
        } catch (error: any) {
            toast.error(`Failed to generate ${format.toUpperCase()} document`)
        } finally {
            setGeneratingDocument(false)
        }
    }

    const handleActivate = async () => {
        if (!pocId) return
        try {
            await api.put(`/pocs/${pocId}`, { status: 'active' })
            toast.success('POC activated')
            fetchPOCData()
        } catch (error: any) {
            toast.error('Failed to activate POC')
        }
    }

    const handleDeactivate = async () => {
        if (!pocId) return
        try {
            await api.put(`/pocs/${pocId}`, { status: 'archived' })
            toast.success('POC deactivated')
            fetchPOCData()
        } catch (error: any) {
            toast.error('Failed to deactivate POC')
        }
    }

    return (
        <div className="bg-white rounded-lg shadow-md">
            {/* Header */}
            <div className="border-b border-gray-200 px-6 py-4">
                <div className="flex justify-between items-center">
                    <h2 className="text-2xl font-bold text-gray-900">
                        {pocId ? 'Edit POC' : 'Create New POC'}
                    </h2>
                    <div className="flex gap-2">
                        {pocId && (
                            <>
                                <button
                                    onClick={() => setShowDocumentModal(true)}
                                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                    Generate Document
                                </button>
                                <button
                                    onClick={handleActivate}
                                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                                >
                                    Activate
                                </button>
                                <button
                                    onClick={handleDeactivate}
                                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                                >
                                    Deactivate
                                </button>
                            </>
                        )}
                        {onClose && (
                            <button
                                onClick={onClose}
                                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                            >
                                Close
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200">
                <nav className="flex -mb-px px-6">
                    {pocId && (
                        <button
                            onClick={() => setActiveTab('dashboard')}
                            className={`py-4 px-4 border-b-2 font-medium text-sm ${activeTab === 'dashboard'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                } `}
                        >
                            📊 Dashboard
                        </button>
                    )}
                    <button
                        onClick={() => setActiveTab('basic')}
                        className={`py-4 px-4 border-b-2 font-medium text-sm ${activeTab === 'basic'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            } `}
                    >
                        Basic Info
                    </button>
                    <button
                        onClick={() => setActiveTab('criteria')}
                        className={`py-4 px-4 border-b-2 font-medium text-sm ${activeTab === 'criteria'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            } `}
                    >
                        Success Criteria ({successCriteria.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('tasks')}
                        className={`py-4 px-4 border-b-2 font-medium text-sm ${activeTab === 'tasks'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            } `}
                    >
                        Tasks & Groups ({pocTasks.length + pocTaskGroups.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('participants')}
                        className={`py-4 px-4 border-b-2 font-medium text-sm ${activeTab === 'participants'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            } `}
                    >
                        Participants ({participants.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('resources')}
                        className={`py-4 px-4 border-b-2 font-medium text-sm ${activeTab === 'resources'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            } `}
                    >
                        Resources ({resources.length})
                    </button>
                </nav>
            </div>

            {/* Content */}
            <div className="p-6 max-h-[calc(100vh-300px)] overflow-y-auto">
                {/* Dashboard Tab */}
                {activeTab === 'dashboard' && pocId && (
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold text-gray-900">POC Dashboard</h2>

                        {/* Key Metrics */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {/* Days in Progress */}
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

                            {/* Total Tasks */}
                            <div className="bg-white border border-gray-200 rounded-lg p-4">
                                <div className="text-sm font-medium text-gray-500 mb-1">Total Tasks</div>
                                <div className="text-3xl font-bold text-green-600">{pocTasks.length}</div>
                            </div>

                            {/* Total Task Groups */}
                            <div className="bg-white border border-gray-200 rounded-lg p-4">
                                <div className="text-sm font-medium text-gray-500 mb-1">Total Task Groups</div>
                                <div className="text-3xl font-bold text-purple-600">{pocTaskGroups.length}</div>
                            </div>

                            {/* Success Criteria */}
                            <div className="bg-white border border-gray-200 rounded-lg p-4">
                                <div className="text-sm font-medium text-gray-500 mb-1">Success Criteria</div>
                                <div className="text-3xl font-bold text-indigo-600">{successCriteria.length}</div>
                            </div>
                        </div>

                        {/* Task Status Breakdown */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Tasks Status */}
                            <div className="bg-white border border-gray-200 rounded-lg p-6">
                                <h3 className="text-lg font-semibold text-gray-900 mb-4">Tasks by Status</h3>
                                <div className="space-y-3">
                                    {[
                                        { status: 'not_started', label: 'Not Started', color: 'gray' },
                                        { status: 'in_progress', label: 'In Progress', color: 'blue' },
                                        { status: 'completed', label: 'Completed', color: 'green' },
                                        { status: 'blocked', label: 'Blocked', color: 'red' },
                                        { status: 'satisfied', label: 'Satisfied', color: 'emerald' },
                                        { status: 'partially_satisfied', label: 'Partially Satisfied', color: 'yellow' },
                                        { status: 'not_satisfied', label: 'Not Satisfied', color: 'orange' }
                                    ].map(({ status, label, color }) => {
                                        const count = pocTasks.filter(t => t.status === status).length
                                        const percentage = pocTasks.length > 0 ? (count / pocTasks.length * 100).toFixed(0) : 0
                                        return (
                                            <div key={status} className="flex items-center justify-between">
                                                <div className="flex items-center gap-2">
                                                    <div className={`w-3 h-3 rounded-full bg-${color}-500`}></div>
                                                    <span className="text-sm text-gray-700">{label}</span>
                                                </div>
                                                <div className="flex items-center gap-3">
                                                    <div className="w-32 bg-gray-200 rounded-full h-2">
                                                        <div className={`bg-${color}-500 h-2 rounded-full`} style={{ width: `${percentage}%` }}></div>
                                                    </div>
                                                    <span className="text-sm font-semibold text-gray-900 w-12 text-right">{count} ({percentage}%)</span>
                                                </div>
                                            </div>
                                        )
                                    })}
                                </div>
                            </div>

                            {/* Task Groups Status */}
                            <div className="bg-white border border-gray-200 rounded-lg p-6">
                                <h3 className="text-lg font-semibold text-gray-900 mb-4">Task Groups by Status</h3>
                                <div className="space-y-3">
                                    {[
                                        { status: 'not_started', label: 'Not Started', color: 'gray' },
                                        { status: 'in_progress', label: 'In Progress', color: 'blue' },
                                        { status: 'completed', label: 'Completed', color: 'green' },
                                        { status: 'blocked', label: 'Blocked', color: 'red' },
                                        { status: 'satisfied', label: 'Satisfied', color: 'emerald' },
                                        { status: 'partially_satisfied', label: 'Partially Satisfied', color: 'yellow' },
                                        { status: 'not_satisfied', label: 'Not Satisfied', color: 'orange' }
                                    ].map(({ status, label, color }) => {
                                        const count = pocTaskGroups.filter(g => g.status === status).length
                                        const percentage = pocTaskGroups.length > 0 ? (count / pocTaskGroups.length * 100).toFixed(0) : 0
                                        return (
                                            <div key={status} className="flex items-center justify-between">
                                                <div className="flex items-center gap-2">
                                                    <div className={`w-3 h-3 rounded-full bg-${color}-500`}></div>
                                                    <span className="text-sm text-gray-700">{label}</span>
                                                </div>
                                                <div className="flex items-center gap-3">
                                                    <div className="w-32 bg-gray-200 rounded-full h-2">
                                                        <div className={`bg-${color}-500 h-2 rounded-full`} style={{ width: `${percentage}%` }}></div>
                                                    </div>
                                                    <span className="text-sm font-semibold text-gray-900 w-12 text-right">{count} ({percentage}%)</span>
                                                </div>
                                            </div>
                                        )
                                    })}
                                </div>
                            </div>
                        </div>

                        {/* Success Criteria Status Table */}
                        {successCriteria.length > 0 && (
                            <div className="bg-white border border-gray-200 rounded-lg p-6">
                                <h3 className="text-lg font-semibold text-gray-900 mb-4">Success Criteria Task Status</h3>
                                <div className="overflow-x-auto">
                                    <table className="min-w-full divide-y divide-gray-200">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Criteria
                                                </th>
                                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Not Started
                                                </th>
                                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    In Progress
                                                </th>
                                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Completed
                                                </th>
                                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Blocked
                                                </th>
                                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Satisfied
                                                </th>
                                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Partially Satisfied
                                                </th>
                                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Not Satisfied
                                                </th>
                                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Total
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white divide-y divide-gray-200">
                                            {successCriteria.map((criteria) => {
                                                // Get all tasks from both standalone tasks and tasks within groups
                                                // Deduplicate tasks: pocTasks includes all tasks (even those in groups),
                                                // so use a Map to avoid counting group tasks twice
                                                const taskMap = new Map<number, POCTask>()
                                                pocTasks.forEach(t => { if (t.id) taskMap.set(t.id, t) })
                                                pocTaskGroups.forEach(group => {
                                                    (group.tasks || []).forEach(t => { if (t.id) taskMap.set(t.id, t) })
                                                })
                                                const allTasks = Array.from(taskMap.values())

                                                // Find task IDs belonging to groups that are linked to this criteria
                                                const groupLinkedTaskIds = new Set<number>()
                                                pocTaskGroups.forEach(group => {
                                                    const groupCriteriaIds = group.success_criteria_ids || []
                                                    if (groupCriteriaIds.some((id: number) => id == criteria.id || String(id) === String(criteria.id))) {
                                                        (group.tasks || []).forEach(t => {
                                                            if (t.id) groupLinkedTaskIds.add(t.id)
                                                        })
                                                    }
                                                })

                                                // A task is related if it directly links to the criteria
                                                // OR belongs to a task group linked to the criteria
                                                const relatedTasks = allTasks.filter(task => {
                                                    // Check direct task-level link
                                                    if (task.success_criteria_ids && Array.isArray(task.success_criteria_ids)) {
                                                        if (task.success_criteria_ids.some(id =>
                                                            id == criteria.id || String(id) === String(criteria.id)
                                                        )) {
                                                            return true
                                                        }
                                                    }
                                                    // Check group-level link
                                                    if (task.id && groupLinkedTaskIds.has(task.id)) {
                                                        return true
                                                    }
                                                    return false
                                                })

                                                // Count tasks by status
                                                const notStarted = relatedTasks.filter(t => t.status === 'not_started' || !t.status).length
                                                const inProgress = relatedTasks.filter(t => t.status === 'in_progress').length
                                                const completed = relatedTasks.filter(t => t.status === 'completed').length
                                                const blocked = relatedTasks.filter(t => t.status === 'blocked').length
                                                const satisfied = relatedTasks.filter(t => t.status === 'satisfied').length
                                                const partiallySatisfied = relatedTasks.filter(t => t.status === 'partially_satisfied').length
                                                const notSatisfied = relatedTasks.filter(t => t.status === 'not_satisfied').length
                                                const total = relatedTasks.length

                                                return (
                                                    <tr key={criteria.id} className="hover:bg-gray-50">
                                                        <td className="px-4 py-3 text-sm font-medium text-gray-900">
                                                            <div className="flex items-center gap-2">
                                                                <div
                                                                    className="w-2 h-2 rounded-full"
                                                                    style={{
                                                                        backgroundColor:
                                                                            criteria.importance_level >= 4 ? '#ef4444' :
                                                                                criteria.importance_level >= 3 ? '#f59e0b' :
                                                                                    '#10b981'
                                                                    }}
                                                                />
                                                                {criteria.title}
                                                            </div>
                                                        </td>
                                                        {[
                                                            { count: notStarted, status: 'not_started', label: 'Not Started', color: 'gray-900', activeColor: 'gray-900' },
                                                            { count: inProgress, status: 'in_progress', label: 'In Progress', color: 'gray-400', activeColor: 'blue-600' },
                                                            { count: completed, status: 'completed', label: 'Completed', color: 'gray-400', activeColor: 'green-600' },
                                                            { count: blocked, status: 'blocked', label: 'Blocked', color: 'gray-400', activeColor: 'red-600' },
                                                            { count: satisfied, status: 'satisfied', label: 'Satisfied', color: 'gray-400', activeColor: 'emerald-600' },
                                                            { count: partiallySatisfied, status: 'partially_satisfied', label: 'Partially Satisfied', color: 'gray-400', activeColor: 'yellow-600' },
                                                            { count: notSatisfied, status: 'not_satisfied', label: 'Not Satisfied', color: 'gray-400', activeColor: 'orange-600' },
                                                        ].map(({ count, status, label, color, activeColor }) => (
                                                            <td key={status} className="px-3 py-3 text-center text-sm text-gray-700">
                                                                <button
                                                                    className={`${count > 0 ? `font-semibold text-${activeColor} hover:underline cursor-pointer` : 'text-gray-400 cursor-default'}`}
                                                                    disabled={count === 0}
                                                                    onClick={() => {
                                                                        if (count > 0) {
                                                                            const names = relatedTasks.filter(t => status === 'not_started' ? (t.status === 'not_started' || !t.status) : t.status === status).map(t => t.title)
                                                                            setCriteriaTaskListTitle(`${criteria.title} — ${label}`)
                                                                            setCriteriaTaskListNames(names)
                                                                            setShowCriteriaTaskListModal(true)
                                                                        }
                                                                    }}
                                                                >
                                                                    {count}
                                                                </button>
                                                            </td>
                                                        ))}
                                                        <td className="px-3 py-3 text-center text-sm text-gray-700">
                                                            <button
                                                                className={`${total > 0 ? 'font-semibold text-gray-900 hover:underline cursor-pointer' : 'font-semibold text-gray-900 cursor-default'}`}
                                                                disabled={total === 0}
                                                                onClick={() => {
                                                                    if (total > 0) {
                                                                        setCriteriaTaskListTitle(`${criteria.title} — All Tasks`)
                                                                        setCriteriaTaskListNames(relatedTasks.map(t => t.title))
                                                                        setShowCriteriaTaskListModal(true)
                                                                    }
                                                                }}
                                                            >
                                                                {total}
                                                            </button>
                                                        </td>
                                                    </tr>
                                                )
                                            })}
                                        </tbody>
                                    </table>
                                </div>
                                {successCriteria.every(sc => pocTasks.filter(t => t.success_criteria_ids?.includes(sc.id!)).length === 0) && (
                                    <p className="text-sm text-gray-500 text-center mt-4">No tasks are associated with success criteria yet.</p>
                                )}
                            </div>
                        )}

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
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                POC Title *
                            </label>
                            <input
                                type="text"
                                required
                                value={formData.title}
                                onChange={(e) => handleInputChange('title', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                placeholder="e.g., Acme Corp Enterprise Platform POC"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Customer Company Name *
                            </label>
                            <input
                                type="text"
                                required
                                value={formData.customer_company_name}
                                onChange={(e) => handleInputChange('customer_company_name', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                placeholder="e.g., Acme Corporation"
                            />
                        </div>

                        {/* Customer Logo Upload - Only show if POC is created */}
                        {pocId && (
                            <LogoUpload
                                currentLogoUrl={customerLogoUrl}
                                uploadEndpoint={`/pocs/${pocId}/logo`}
                                deleteEndpoint={`/pocs/${pocId}/logo`}
                                label="Customer Logo"
                                description="Upload the customer's logo to include in generated documents (max 2MB, JPEG/PNG/GIF/WebP)"
                                onUploadSuccess={(logoUrl) => setCustomerLogoUrl(logoUrl)}
                                onDelete={() => setCustomerLogoUrl(null)}
                            />
                        )}

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Description
                            </label>
                            <textarea
                                rows={3}
                                value={formData.description}
                                onChange={(e) => handleInputChange('description', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                placeholder="Brief description of the POC..."
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Executive Summary
                            </label>
                            <textarea
                                rows={4}
                                value={formData.executive_summary}
                                onChange={(e) => handleInputChange('executive_summary', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                placeholder="High-level summary for executives..."
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Objectives
                            </label>
                            <textarea
                                rows={4}
                                value={formData.objectives}
                                onChange={(e) => handleInputChange('objectives', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                placeholder="Key objectives and goals for this POC..."
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Start Date
                                </label>
                                <input
                                    type="date"
                                    value={formData.start_date}
                                    onChange={(e) => handleInputChange('start_date', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    End Date
                                </label>
                                <input
                                    type="date"
                                    value={formData.end_date}
                                    onChange={(e) => handleInputChange('end_date', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Products
                            </label>
                            <div className="border border-gray-300 rounded-lg p-3 max-h-48 overflow-y-auto">
                                {products.length === 0 ? (
                                    <p className="text-sm text-gray-500">No products available</p>
                                ) : (
                                    products.map((product) => (
                                        <label key={product.id} className="flex items-center py-2 hover:bg-gray-50">
                                            <input
                                                type="checkbox"
                                                checked={formData.product_ids.includes(product.id)}
                                                onChange={() => handleProductToggle(product.id)}
                                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                            />
                                            <span className="ml-2 text-sm text-gray-900">{product.name}</span>
                                        </label>
                                    ))
                                )}
                            </div>
                        </div>

                        <div className="flex gap-3">
                            <button
                                onClick={handleSubmitBasicInfo}
                                disabled={loading}
                                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                            >
                                {loading ? 'Saving...' : pocId ? 'Update POC' : 'Create POC'}
                            </button>
                        </div>
                    </div>
                )}

                {/* Success Criteria Tab */}
                {activeTab === 'criteria' && (
                    <div className="space-y-6">
                        <div className="bg-gray-50 p-4 rounded-lg">
                            <h3 className="font-semibold text-gray-900 mb-4">Add Success Criteria</h3>
                            <div className="space-y-3">
                                <input
                                    type="text"
                                    placeholder="Title *"
                                    value={newCriteria.title}
                                    onChange={(e) => setNewCriteria({ ...newCriteria, title: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                />
                                <textarea
                                    placeholder="Description"
                                    rows={2}
                                    value={newCriteria.description || ''}
                                    onChange={(e) => setNewCriteria({ ...newCriteria, description: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                />
                                <input
                                    type="text"
                                    placeholder="Target Value"
                                    value={newCriteria.target_value}
                                    onChange={(e) => setNewCriteria({ ...newCriteria, target_value: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                />
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Importance Level (1-5)
                                    </label>
                                    <input
                                        type="number"
                                        min="1"
                                        max="5"
                                        value={newCriteria.importance_level}
                                        onChange={(e) => setNewCriteria({ ...newCriteria, importance_level: parseInt(e.target.value) || 3 })}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                    />
                                </div>
                                <button
                                    onClick={handleAddCriteria}
                                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                                >
                                    Add Criteria
                                </button>
                            </div>
                        </div>

                        <div className="space-y-3">
                            {successCriteria.length === 0 ? (
                                <p className="text-center text-gray-500 py-8">No success criteria defined yet</p>
                            ) : (
                                successCriteria.map((criteria) => (
                                    <div key={criteria.id} className="border border-gray-200 rounded-lg p-4">
                                        <div className="flex justify-between items-start">
                                            <div className="flex-1">
                                                <h4 className="font-semibold text-gray-900">{criteria.title}</h4>
                                                {criteria.description && (
                                                    <p className="text-sm text-gray-600 mt-1">{criteria.description}</p>
                                                )}
                                                <div className="flex gap-4 mt-2 text-sm">
                                                    <span className="text-gray-500">Target: {criteria.target_value || 'N/A'}</span>
                                                    <span className="text-gray-500">
                                                        Importance: {'★'.repeat(criteria.importance_level)}{'☆'.repeat(5 - criteria.importance_level)}
                                                    </span>
                                                </div>
                                            </div>
                                            <button
                                                onClick={() => handleDeleteCriteria(criteria.id!)}
                                                className="text-red-600 hover:text-red-800"
                                            >
                                                Delete
                                            </button>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                )}

                {/* Tasks & Groups Tab */}
                {activeTab === 'tasks' && (
                    <div className="space-y-6">
                        {/* Tasks Section */}
                        <div>
                            <div className="flex justify-between items-center mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">Tasks</h3>
                                <button
                                    onClick={() => {
                                        setNewTask({ title: '', description: '', success_criteria_ids: [], sort_order: pocTasks.length })
                                        setShowTaskForm(true)
                                    }}
                                    className="px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                                >
                                    + Custom Task
                                </button>
                            </div>

                            {/* Template Selection */}
                            <div className="bg-gray-50 p-4 rounded-lg mb-4">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Or select from templates:
                                </label>
                                <select
                                    onChange={(e) => {
                                        if (e.target.value) {
                                            handleAddTaskFromTemplate(parseInt(e.target.value))
                                            e.target.value = ''
                                        }
                                    }}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                >
                                    <option value="">-- Select Task Template --</option>
                                    {taskTemplates.map((template) => (
                                        <option key={template.id} value={template.id}>
                                            {template.title}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Task Form */}
                            {showTaskForm && (
                                <div className="bg-blue-50 p-4 rounded-lg mb-4 border border-blue-200">
                                    <h4 className="font-semibold text-gray-900 mb-3">Add Task</h4>
                                    <div className="space-y-3">
                                        <input
                                            type="text"
                                            placeholder="Task Title *"
                                            value={newTask.title}
                                            onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                        />
                                        <textarea
                                            placeholder="Description"
                                            rows={2}
                                            value={newTask.description || ''}
                                            onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                        />

                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Start Date
                                                </label>
                                                <input
                                                    type="date"
                                                    value={newTask.start_date || ''}
                                                    min={formData.start_date || undefined}
                                                    max={formData.end_date || undefined}
                                                    onChange={(e) => setNewTask({ ...newTask, start_date: e.target.value })}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Due Date
                                                </label>
                                                <input
                                                    type="date"
                                                    value={newTask.due_date || ''}
                                                    min={formData.start_date || undefined}
                                                    max={formData.end_date || undefined}
                                                    onChange={(e) => setNewTask({ ...newTask, due_date: e.target.value })}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                                />
                                                {formData.end_date && (
                                                    <p className="text-xs text-gray-500 mt-1">Defaults to POC end date ({formData.end_date})</p>
                                                )}
                                            </div>
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                Link to Success Criteria (optional)
                                            </label>
                                            <div className="border border-gray-300 rounded-lg p-2 max-h-32 overflow-y-auto">
                                                {successCriteria.length === 0 ? (
                                                    <p className="text-sm text-gray-500">No success criteria defined yet</p>
                                                ) : (
                                                    successCriteria.map((criteria) => (
                                                        <label key={criteria.id} className="flex items-center py-1 hover:bg-gray-50">
                                                            <input
                                                                type="checkbox"
                                                                checked={newTask.success_criteria_ids.includes(criteria.id!)}
                                                                onChange={(e) => {
                                                                    if (e.target.checked) {
                                                                        setNewTask({
                                                                            ...newTask,
                                                                            success_criteria_ids: [...newTask.success_criteria_ids, criteria.id!]
                                                                        })
                                                                    } else {
                                                                        setNewTask({
                                                                            ...newTask,
                                                                            success_criteria_ids: newTask.success_criteria_ids.filter(id => id !== criteria.id)
                                                                        })
                                                                    }
                                                                }}
                                                                className="h-4 w-4 text-blue-600 rounded"
                                                            />
                                                            <span className="ml-2 text-sm text-gray-900">{criteria.title}</span>
                                                        </label>
                                                    ))
                                                )}
                                            </div>
                                        </div>

                                        <div className="flex gap-2">
                                            <button
                                                onClick={handleAddTask}
                                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                            >
                                                Add Task
                                            </button>
                                            <button
                                                onClick={() => {
                                                    setShowTaskForm(false)
                                                    setNewTask({ title: '', description: '', success_criteria_ids: [], sort_order: 0, start_date: '', due_date: formData.end_date || '' })
                                                }}
                                                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Task List */}
                            <div className="space-y-2">
                                {pocTasks.length === 0 ? (
                                    <p className="text-center text-gray-500 py-4">No tasks added yet</p>
                                ) : (
                                    pocTasks.map((task) => (
                                        <div key={task.id} className="border border-gray-200 rounded-lg p-3 bg-white">
                                            <div className="flex justify-between items-start gap-3">
                                                <div className="flex-1">
                                                    <h4 className="font-medium text-gray-900">{task.title}</h4>
                                                    {task.description && (
                                                        <p className="text-sm text-gray-600 mt-1">{task.description}</p>
                                                    )}
                                                    {(task.start_date || task.due_date) && (
                                                        <div className="mt-1 flex items-center gap-3 text-xs text-gray-500">
                                                            {task.start_date && (
                                                                <span>📅 Start: {task.start_date}</span>
                                                            )}
                                                            {task.due_date && (
                                                                <span>🏁 Due: {task.due_date}</span>
                                                            )}
                                                        </div>
                                                    )}
                                                    {pocId && (
                                                        <div className="mt-2 flex items-center gap-3">
                                                            <label className="text-xs text-gray-500">📅 Start:</label>
                                                            <input
                                                                type="date"
                                                                value={task.start_date || ''}
                                                                min={formData.start_date || undefined}
                                                                max={formData.end_date || undefined}
                                                                onChange={(e) => handleUpdateTaskDates(task.id!, 'start_date', e.target.value)}
                                                                className="px-2 py-1 border border-gray-300 rounded text-xs"
                                                            />
                                                            <label className="text-xs text-gray-500">🏁 Due:</label>
                                                            <input
                                                                type="date"
                                                                value={task.due_date || ''}
                                                                min={formData.start_date || undefined}
                                                                max={formData.end_date || undefined}
                                                                onChange={(e) => handleUpdateTaskDates(task.id!, 'due_date', e.target.value)}
                                                                className="px-2 py-1 border border-gray-300 rounded text-xs"
                                                            />
                                                        </div>
                                                    )}
                                                    {task.success_criteria_ids && task.success_criteria_ids.length > 0 && (
                                                        <div className="mt-2 flex flex-wrap gap-1">
                                                            {task.success_criteria_ids.map(criteriaId => {
                                                                const criteria = successCriteria.find(c => c.id === criteriaId)
                                                                return criteria ? (
                                                                    <span key={criteriaId} className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                                                                        {criteria.title}
                                                                    </span>
                                                                ) : null
                                                            })}
                                                        </div>
                                                    )}
                                                    {task.assignees && task.assignees.length > 0 && (
                                                        <div className="mt-2 flex flex-wrap gap-1">
                                                            <span className="text-xs text-gray-600 mr-1">Assigned to:</span>
                                                            {task.assignees.map(assignee => (
                                                                <span key={assignee.id} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs" title={assignee.participant_email}>
                                                                    👤 {assignee.participant_name}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    )}
                                                </div>
                                                {pocId && (
                                                    <div className="flex items-center gap-2">
                                                        <span className="text-xs text-gray-500">Status: {task.status || 'none'}</span>
                                                        <select
                                                            value={task.status || 'not_started'}
                                                            onChange={(e) => handleUpdateTaskStatus(task.id!, e.target.value)}
                                                            className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm bg-white text-gray-900"
                                                        >
                                                            <option value="not_started">Not Started</option>
                                                            <option value="in_progress">In Progress</option>
                                                            <option value="completed">Completed</option>
                                                            <option value="blocked">Blocked</option>
                                                            <option value="satisfied">Satisfied</option>
                                                            <option value="partially_satisfied">Partially Satisfied</option>
                                                            <option value="not_satisfied">Not Satisfied</option>
                                                        </select>
                                                        <button
                                                            onClick={() => handleOpenAssignmentModal(task)}
                                                            className="px-3 py-1.5 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 text-sm"
                                                            title="Assign Participants"
                                                        >
                                                            👥 Assign
                                                        </button>
                                                        <button
                                                            onClick={() => handleOpenCriteriaEdit(task)}
                                                            className="px-3 py-1.5 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 text-sm"
                                                            title="Link Success Criteria"
                                                        >
                                                            🎯 Criteria
                                                        </button>
                                                        <button
                                                            onClick={() => {
                                                                setCommentsModalTaskId(task.id)
                                                                setCommentsModalTaskGroupId(undefined)
                                                                setShowCommentsModal(true)
                                                            }}
                                                            className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm"
                                                            title="View Comments"
                                                        >
                                                            💬 Comments
                                                        </button>
                                                        <button
                                                            onClick={() => {
                                                                setResourcesModalTaskId(task.id)
                                                                setResourcesModalTaskGroupId(undefined)
                                                                setResourcesModalTitle(task.title)
                                                                setShowResourcesModal(true)
                                                            }}
                                                            className="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 text-sm font-medium"
                                                            title="View and manage resources"
                                                        >
                                                            📚 Resources
                                                        </button>
                                                        <button
                                                            onClick={() => handleDeleteTask(task.id!)}
                                                            className="text-red-600 hover:text-red-800"
                                                        >
                                                            Delete
                                                        </button>
                                                    </div>
                                                )}
                                                {!pocId && (
                                                    <button
                                                        onClick={() => handleDeleteTask(task.id!)}
                                                        className="text-red-600 hover:text-red-800 ml-2"
                                                    >
                                                        Delete
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>

                        {/* Task Groups Section */}
                        <div className="pt-6 border-t border-gray-200">
                            <div className="flex justify-between items-center mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">Task Groups</h3>
                                <button
                                    onClick={() => {
                                        setNewTaskGroup({ title: '', description: '', success_criteria_ids: [], sort_order: pocTaskGroups.length, start_date: '', due_date: formData.end_date || '' })
                                        setShowTaskGroupForm(true)
                                    }}
                                    className="px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                                >
                                    + Custom Group
                                </button>
                            </div>

                            {/* Template Selection */}
                            <div className="bg-gray-50 p-4 rounded-lg mb-4">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Or select from templates:
                                </label>
                                <select
                                    onChange={(e) => {
                                        if (e.target.value) {
                                            handleAddTaskGroupFromTemplate(parseInt(e.target.value))
                                            e.target.value = ''
                                        }
                                    }}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                >
                                    <option value="">-- Select Task Group Template --</option>
                                    {taskGroupTemplates.map((template) => (
                                        <option key={template.id} value={template.id}>
                                            {template.title}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Task Group Form */}
                            {showTaskGroupForm && (
                                <div className="bg-blue-50 p-4 rounded-lg mb-4 border border-blue-200">
                                    <h4 className="font-semibold text-gray-900 mb-3">Add Task Group</h4>
                                    <div className="space-y-3">
                                        <input
                                            type="text"
                                            placeholder="Group Title *"
                                            value={newTaskGroup.title}
                                            onChange={(e) => setNewTaskGroup({ ...newTaskGroup, title: e.target.value })}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                        />
                                        <textarea
                                            placeholder="Description"
                                            rows={2}
                                            value={newTaskGroup.description || ''}
                                            onChange={(e) => setNewTaskGroup({ ...newTaskGroup, description: e.target.value })}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                        />

                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Start Date
                                                </label>
                                                <input
                                                    type="date"
                                                    value={newTaskGroup.start_date || ''}
                                                    min={formData.start_date || undefined}
                                                    max={formData.end_date || undefined}
                                                    onChange={(e) => setNewTaskGroup({ ...newTaskGroup, start_date: e.target.value })}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Due Date
                                                </label>
                                                <input
                                                    type="date"
                                                    value={newTaskGroup.due_date || ''}
                                                    min={formData.start_date || undefined}
                                                    max={formData.end_date || undefined}
                                                    onChange={(e) => setNewTaskGroup({ ...newTaskGroup, due_date: e.target.value })}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                                />
                                                {formData.end_date && (
                                                    <p className="text-xs text-gray-500 mt-1">Defaults to POC end date ({formData.end_date})</p>
                                                )}
                                            </div>
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                Link to Success Criteria (optional)
                                            </label>
                                            <div className="border border-gray-300 rounded-lg p-2 max-h-32 overflow-y-auto">
                                                {successCriteria.length === 0 ? (
                                                    <p className="text-sm text-gray-500">No success criteria defined yet</p>
                                                ) : (
                                                    successCriteria.map((criteria) => (
                                                        <label key={criteria.id} className="flex items-center py-1 hover:bg-gray-50">
                                                            <input
                                                                type="checkbox"
                                                                checked={newTaskGroup.success_criteria_ids.includes(criteria.id!)}
                                                                onChange={(e) => {
                                                                    if (e.target.checked) {
                                                                        setNewTaskGroup({
                                                                            ...newTaskGroup,
                                                                            success_criteria_ids: [...newTaskGroup.success_criteria_ids, criteria.id!]
                                                                        })
                                                                    } else {
                                                                        setNewTaskGroup({
                                                                            ...newTaskGroup,
                                                                            success_criteria_ids: newTaskGroup.success_criteria_ids.filter(id => id !== criteria.id)
                                                                        })
                                                                    }
                                                                }}
                                                                className="h-4 w-4 text-blue-600 rounded"
                                                            />
                                                            <span className="ml-2 text-sm text-gray-900">{criteria.title}</span>
                                                        </label>
                                                    ))
                                                )}
                                            </div>
                                        </div>

                                        <div className="flex gap-2">
                                            <button
                                                onClick={handleAddTaskGroup}
                                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                            >
                                                Add Task Group
                                            </button>
                                            <button
                                                onClick={() => {
                                                    setShowTaskGroupForm(false)
                                                    setNewTaskGroup({ title: '', description: '', success_criteria_ids: [], sort_order: 0, start_date: '', due_date: formData.end_date || '' })
                                                }}
                                                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Task Group List */}
                            <div className="space-y-2">
                                {pocTaskGroups.length === 0 ? (
                                    <p className="text-center text-gray-500 py-4">No task groups added yet</p>
                                ) : (
                                    pocTaskGroups.map((group) => (
                                        <div key={group.id} className="border border-gray-200 rounded-lg bg-white">
                                            <div className="p-3">
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
                                                            <div className="flex items-center gap-2">
                                                                <span className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded text-xs font-medium">
                                                                    GROUP
                                                                </span>
                                                                <h4 className="font-medium text-gray-900">{group.title}</h4>
                                                            </div>
                                                            {group.description && (
                                                                <p className="text-sm text-gray-600 mt-1">{group.description}</p>
                                                            )}
                                                            {(group.start_date || group.due_date) && !pocId && (
                                                                <div className="mt-1 flex items-center gap-3 text-xs text-gray-500">
                                                                    {group.start_date && <span>📅 Start: {group.start_date}</span>}
                                                                    {group.due_date && <span>🏁 Due: {group.due_date}</span>}
                                                                </div>
                                                            )}
                                                            {pocId && (
                                                                <div className="mt-2 flex items-center gap-3">
                                                                    <label className="text-xs text-gray-500">📅 Start:</label>
                                                                    <input
                                                                        type="date"
                                                                        value={group.start_date || ''}
                                                                        min={formData.start_date || undefined}
                                                                        max={formData.end_date || undefined}
                                                                        onChange={(e) => handleUpdateTaskGroupDates(group.id!, 'start_date', e.target.value)}
                                                                        className="px-2 py-1 border border-gray-300 rounded text-xs"
                                                                    />
                                                                    <label className="text-xs text-gray-500">🏁 Due:</label>
                                                                    <input
                                                                        type="date"
                                                                        value={group.due_date || ''}
                                                                        min={formData.start_date || undefined}
                                                                        max={formData.end_date || undefined}
                                                                        onChange={(e) => handleUpdateTaskGroupDates(group.id!, 'due_date', e.target.value)}
                                                                        className="px-2 py-1 border border-gray-300 rounded text-xs"
                                                                    />
                                                                </div>
                                                            )}
                                                            {group.success_criteria_ids && group.success_criteria_ids.length > 0 && (
                                                                <div className="mt-2 flex flex-wrap gap-1">
                                                                    {group.success_criteria_ids.map(criteriaId => {
                                                                        const criteria = successCriteria.find(c => c.id === criteriaId)
                                                                        return criteria ? (
                                                                            <span key={criteriaId} className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                                                                                {criteria.title}
                                                                            </span>
                                                                        ) : null
                                                                    })}
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                    {pocId && (
                                                        <div className="flex items-center gap-2">
                                                            <span className="text-xs text-gray-500">Status: {group.status || 'none'}</span>
                                                            <select
                                                                value={group.status || 'not_started'}
                                                                onChange={(e) => handleUpdateTaskGroupStatus(group.id!, e.target.value)}
                                                                className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm bg-white text-gray-900"
                                                            >
                                                                <option value="not_started">Not Started</option>
                                                                <option value="in_progress">In Progress</option>
                                                                <option value="completed">Completed</option>
                                                                <option value="blocked">Blocked</option>
                                                                <option value="satisfied">Satisfied</option>
                                                                <option value="partially_satisfied">Partially Satisfied</option>
                                                                <option value="not_satisfied">Not Satisfied</option>
                                                            </select>
                                                            <button
                                                                onClick={() => {
                                                                    setCommentsModalTaskId(undefined)
                                                                    setCommentsModalTaskGroupId(group.id)
                                                                    setShowCommentsModal(true)
                                                                }}
                                                                className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm"
                                                                title="View Comments"
                                                            >
                                                                💬 Comments
                                                            </button>
                                                            <button
                                                                onClick={() => {
                                                                    setResourcesModalTaskId(undefined)
                                                                    setResourcesModalTaskGroupId(group.id)
                                                                    setResourcesModalTitle(group.title)
                                                                    setShowResourcesModal(true)
                                                                }}
                                                                className="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 text-sm font-medium"
                                                                title="View and manage resources"
                                                            >
                                                                📚 Resources
                                                            </button>
                                                            <button
                                                                onClick={() => handleDeleteTaskGroup(group.id!)}
                                                                className="text-red-600 hover:text-red-800"
                                                            >
                                                                Delete
                                                            </button>
                                                        </div>
                                                    )}
                                                    {!pocId && (
                                                        <button
                                                            onClick={() => handleDeleteTaskGroup(group.id!)}
                                                            className="text-red-600 hover:text-red-800 ml-2"
                                                        >
                                                            Delete
                                                        </button>
                                                    )}
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
                                                                            {pocId && (
                                                                                <div className="mt-2 flex items-center gap-2">
                                                                                    <label className="text-xs text-gray-500">📅</label>
                                                                                    <input
                                                                                        type="date"
                                                                                        value={task.start_date || ''}
                                                                                        min={formData.start_date || undefined}
                                                                                        max={formData.end_date || undefined}
                                                                                        onChange={(e) => handleUpdateTaskDates(task.id!, 'start_date', e.target.value)}
                                                                                        className="px-1 py-0.5 border border-gray-300 rounded text-xs"
                                                                                    />
                                                                                    <label className="text-xs text-gray-500">🏁</label>
                                                                                    <input
                                                                                        type="date"
                                                                                        value={task.due_date || ''}
                                                                                        min={formData.start_date || undefined}
                                                                                        max={formData.end_date || undefined}
                                                                                        onChange={(e) => handleUpdateTaskDates(task.id!, 'due_date', e.target.value)}
                                                                                        className="px-1 py-0.5 border border-gray-300 rounded text-xs"
                                                                                    />
                                                                                </div>
                                                                            )}
                                                                            {!pocId && (task.start_date || task.due_date) && (
                                                                                <div className="mt-1 flex items-center gap-3 text-xs text-gray-500">
                                                                                    {task.start_date && <span>📅 Start: {task.start_date}</span>}
                                                                                    {task.due_date && <span>🏁 Due: {task.due_date}</span>}
                                                                                </div>
                                                                            )}
                                                                            {task.success_criteria_ids && task.success_criteria_ids.length > 0 && (
                                                                                <div className="mt-2 flex flex-wrap gap-1">
                                                                                    {task.success_criteria_ids.map(criteriaId => {
                                                                                        const criteria = successCriteria.find(c => c.id === criteriaId)
                                                                                        return criteria ? (
                                                                                            <span key={criteriaId} className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                                                                                                {criteria.title}
                                                                                            </span>
                                                                                        ) : null
                                                                                    })}
                                                                                </div>
                                                                            )}
                                                                            {task.assignees && task.assignees.length > 0 && (
                                                                                <div className="mt-2 flex flex-wrap gap-1">
                                                                                    <span className="text-xs text-gray-600 mr-1">Assigned to:</span>
                                                                                    {task.assignees.map(assignee => (
                                                                                        <span key={assignee.id} className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs" title={assignee.participant_email}>
                                                                                            👤 {assignee.participant_name}
                                                                                        </span>
                                                                                    ))}
                                                                                </div>
                                                                            )}
                                                                        </div>
                                                                        {pocId && (
                                                                            <div className="flex items-center gap-2">
                                                                                <select
                                                                                    value={task.status || 'not_started'}
                                                                                    onChange={(e) => handleUpdateTaskStatus(task.id!, e.target.value)}
                                                                                    className="px-2 py-1 border border-gray-300 rounded text-xs bg-white text-gray-900"
                                                                                >
                                                                                    <option value="not_started">Not Started</option>
                                                                                    <option value="in_progress">In Progress</option>
                                                                                    <option value="completed">Completed</option>
                                                                                    <option value="blocked">Blocked</option>
                                                                                    <option value="satisfied">Satisfied</option>
                                                                                    <option value="partially_satisfied">Partially Satisfied</option>
                                                                                    <option value="not_satisfied">Not Satisfied</option>
                                                                                </select>
                                                                                <button
                                                                                    onClick={() => handleOpenAssignmentModal(task)}
                                                                                    className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 text-xs"
                                                                                    title="Assign Participants"
                                                                                >
                                                                                    👥
                                                                                </button>
                                                                                <button
                                                                                    onClick={() => handleOpenCriteriaEdit(task)}
                                                                                    className="px-2 py-1 bg-purple-100 text-purple-700 rounded hover:bg-purple-200 text-xs"
                                                                                    title="Link Success Criteria"
                                                                                >
                                                                                    🎯
                                                                                </button>
                                                                                <button
                                                                                    onClick={() => {
                                                                                        setCommentsModalTaskId(task.id)
                                                                                        setCommentsModalTaskGroupId(undefined)
                                                                                        setShowCommentsModal(true)
                                                                                    }}
                                                                                    className="px-2 py-1 bg-white text-gray-700 rounded hover:bg-gray-200 text-xs"
                                                                                    title="View Comments"
                                                                                >
                                                                                    💬
                                                                                </button>
                                                                                <button
                                                                                    onClick={() => {
                                                                                        setResourcesModalTaskId(task.id)
                                                                                        setResourcesModalTaskGroupId(undefined)
                                                                                        setResourcesModalTitle(task.title)
                                                                                        setShowResourcesModal(true)
                                                                                    }}
                                                                                    className="px-2 py-1 bg-blue-50 text-blue-700 rounded hover:bg-blue-100 text-xs font-medium"
                                                                                    title="Resources"
                                                                                >
                                                                                    📚
                                                                                </button>
                                                                            </div>
                                                                        )}
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

                {/* Participants Tab */}
                {activeTab === 'participants' && (
                    <div className="space-y-6">
                        <div className="bg-gray-50 p-4 rounded-lg">
                            <h3 className="font-semibold text-gray-900 mb-4">Add Participant</h3>
                            <div className="space-y-3">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Select Existing User
                                    </label>
                                    <select
                                        value={newParticipant.user_id || ''}
                                        onChange={(e) => setNewParticipant({ ...newParticipant, user_id: parseInt(e.target.value) || undefined })}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                    >
                                        <option value="">-- Select User --</option>
                                        {users.map((user) => (
                                            <option key={user.id} value={user.id}>
                                                {user.full_name} ({user.email}) - {user.role}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div className="text-center text-gray-500 text-sm">OR</div>
                                <input
                                    type="email"
                                    placeholder="Email (for new user invitation)"
                                    value={newParticipant.email}
                                    onChange={(e) => setNewParticipant({ ...newParticipant, email: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                />
                                <input
                                    type="text"
                                    placeholder="Full Name (for new user)"
                                    value={newParticipant.full_name}
                                    onChange={(e) => setNewParticipant({ ...newParticipant, full_name: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                />
                                <div className="flex gap-4">
                                    <label className="flex items-center">
                                        <input
                                            type="checkbox"
                                            checked={newParticipant.is_sales_engineer}
                                            onChange={(e) => setNewParticipant({ ...newParticipant, is_sales_engineer: e.target.checked })}
                                            className="h-4 w-4 text-blue-600 rounded"
                                        />
                                        <span className="ml-2 text-sm text-gray-900">Vendor/Sales Engineer</span>
                                    </label>
                                    <label className="flex items-center">
                                        <input
                                            type="checkbox"
                                            checked={newParticipant.is_customer}
                                            onChange={(e) => setNewParticipant({ ...newParticipant, is_customer: e.target.checked })}
                                            className="h-4 w-4 text-blue-600 rounded"
                                        />
                                        <span className="ml-2 text-sm text-gray-900">Customer</span>
                                    </label>
                                </div>
                                <button
                                    onClick={handleAddParticipant}
                                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                                >
                                    Add Participant
                                </button>
                            </div>
                        </div>

                        <div className="space-y-2">
                            {participants.length === 0 ? (
                                <p className="text-center text-gray-500 py-8">No participants added yet</p>
                            ) : (
                                participants.map((participant, index) => (
                                    <div key={index} className="border border-gray-200 rounded-lg p-3 bg-white">
                                        <div className="flex justify-between items-start">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2">
                                                    <p className="font-medium text-gray-900">{participant.full_name || participant.email}</p>
                                                    {participant.status === 'accepted' && (
                                                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
                                                            ✓ Accepted
                                                        </span>
                                                    )}
                                                    {participant.status === 'pending' && (
                                                        <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs font-medium">
                                                            ⏳ Pending
                                                        </span>
                                                    )}
                                                    {participant.status === 'expired' && (
                                                        <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-medium">
                                                            ⚠️ Expired
                                                        </span>
                                                    )}
                                                    {participant.status === 'failed' && (
                                                        <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-medium">
                                                            ✗ Failed
                                                        </span>
                                                    )}
                                                </div>
                                                <p className="text-sm text-gray-600">{participant.email}</p>
                                                <p className="text-sm text-gray-500 mt-1">
                                                    {participant.is_sales_engineer && <span className="mr-2">🏢 Vendor</span>}
                                                    {participant.is_customer && <span>👤 Customer</span>}
                                                </p>
                                                {participant.status !== 'accepted' && participant.invited_at && (
                                                    <p className="text-xs text-gray-400 mt-1">
                                                        Invited: {new Date(participant.invited_at).toLocaleDateString()}
                                                        {participant.resend_count > 0 && ` (Resent ${participant.resend_count}x)`}
                                                    </p>
                                                )}
                                            </div>
                                            <div className="flex gap-2">
                                                {(participant.status === 'pending' || participant.status === 'expired' || participant.status === 'failed') && participant.invitation_id && (
                                                    <button
                                                        onClick={async () => {
                                                            try {
                                                                await api.post(`/pocs/${pocId}/invitations/${participant.invitation_id}/resend`)
                                                                toast.success('Invitation resent successfully')
                                                                fetchPOCData()
                                                            } catch (error: any) {
                                                                toast.error(formatErrorMessage(error, 'Failed to resend invitation'))
                                                            }
                                                        }}
                                                        className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                                                        title="Resend invitation email"
                                                    >
                                                        Resend
                                                    </button>
                                                )}
                                                {participant.user_id && (
                                                    <button
                                                        onClick={async () => {
                                                            if (!window.confirm(`Are you sure you want to remove ${participant.full_name || participant.email} from this POC?`)) {
                                                                return
                                                            }
                                                            try {
                                                                await api.delete(`/pocs/${pocId}/participants/${participant.user_id}`)
                                                                toast.success('Participant removed successfully')
                                                                fetchPOCData()
                                                            } catch (error: any) {
                                                                toast.error(formatErrorMessage(error, 'Failed to remove participant'))
                                                            }
                                                        }}
                                                        className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                                                        title="Remove participant from POC"
                                                    >
                                                        Remove
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                )
                }

                {/* Resources Tab */}
                {
                    activeTab === 'resources' && (
                        <div className="space-y-6">
                            <div className="flex justify-between items-center">
                                <h3 className="font-semibold text-gray-900">POC Resources</h3>
                                <button
                                    onClick={() => setShowResourceModal(true)}
                                    disabled={!pocId}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                                >
                                    Add Resource
                                </button>
                            </div>

                            {!pocId && (
                                <p className="text-sm text-amber-600">
                                    Please save the POC first before adding resources
                                </p>
                            )}

                            <div className="space-y-4">
                                {resources.length === 0 ? (
                                    <p className="text-center text-gray-500 py-8">No resources added yet</p>
                                ) : (
                                    resources.map((resource) => (
                                        <div key={resource.id} className="border border-gray-200 rounded-lg p-4">
                                            <div className="flex justify-between items-start mb-2">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                                                            {resource.resource_type}
                                                        </span>
                                                        <h4 className="font-medium text-gray-900">{resource.title}</h4>
                                                    </div>
                                                    {resource.description && (
                                                        <p className="text-sm text-gray-600 mb-2">{resource.description}</p>
                                                    )}
                                                    {resource.resource_type === 'LINK' && (
                                                        <a
                                                            href={resource.content}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="text-sm text-blue-600 hover:underline break-all"
                                                        >
                                                            {resource.content}
                                                        </a>
                                                    )}
                                                    {resource.resource_type === 'TEXT' && (
                                                        <p className="text-sm text-gray-700 whitespace-pre-wrap">{resource.content}</p>
                                                    )}
                                                    {resource.resource_type === 'CODE' && (
                                                        <pre className="text-sm bg-gray-50 p-2 rounded overflow-x-auto">
                                                            <code>{resource.content}</code>
                                                        </pre>
                                                    )}
                                                </div>
                                                <button
                                                    onClick={() => handleDeleteResource(resource.id)}
                                                    className="text-red-600 hover:text-red-800 text-sm ml-4"
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>

                            {/* Resource Modal */}
                            {showResourceModal && (
                                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                                    <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                                        <h3 className="text-xl font-semibold mb-4">Add Resource</h3>

                                        <div className="space-y-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Type *
                                                </label>
                                                <select
                                                    value={newResource.resource_type}
                                                    onChange={(e) => setNewResource({ ...newResource, resource_type: e.target.value as any })}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                                >
                                                    <option value="LINK">Link (URL)</option>
                                                    <option value="TEXT">Text (Notes)</option>
                                                    <option value="CODE">Code (Snippet)</option>
                                                    <option value="FILE">File (Document)</option>
                                                </select>
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Title *
                                                </label>
                                                <input
                                                    type="text"
                                                    value={newResource.title}
                                                    onChange={(e) => setNewResource({ ...newResource, title: e.target.value })}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                                    placeholder="e.g., Setup Instructions, API Documentation"
                                                />
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Description
                                                </label>
                                                <input
                                                    type="text"
                                                    value={newResource.description}
                                                    onChange={(e) => setNewResource({ ...newResource, description: e.target.value })}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                                    placeholder="Optional description"
                                                />
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    {newResource.resource_type === 'LINK' ? 'URL *' :
                                                        newResource.resource_type === 'CODE' ? 'Code Snippet *' :
                                                            newResource.resource_type === 'FILE' ? 'File Path/URL *' :
                                                                'Content *'}
                                                </label>
                                                {newResource.resource_type === 'CODE' || newResource.resource_type === 'TEXT' ? (
                                                    <textarea
                                                        value={newResource.content}
                                                        onChange={(e) => setNewResource({ ...newResource, content: e.target.value })}
                                                        rows={6}
                                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm"
                                                        placeholder={newResource.resource_type === 'CODE' ? 'Paste code snippet here...' : 'Enter text content...'}
                                                    />
                                                ) : (
                                                    <input
                                                        type="text"
                                                        value={newResource.content}
                                                        onChange={(e) => setNewResource({ ...newResource, content: e.target.value })}
                                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                                        placeholder={newResource.resource_type === 'LINK' ? 'https://...' : 'Enter file path or URL'}
                                                    />
                                                )}
                                            </div>

                                            {successCriteria.length > 0 && (
                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                                        Link to Success Criteria (Optional)
                                                    </label>
                                                    <select
                                                        value={newResource.success_criteria_id || ''}
                                                        onChange={(e) => setNewResource({ ...newResource, success_criteria_id: e.target.value ? parseInt(e.target.value) : null })}
                                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                                    >
                                                        <option value="">None</option>
                                                        {successCriteria.map((sc) => (
                                                            <option key={sc.id} value={sc.id}>
                                                                {sc.title}
                                                            </option>
                                                        ))}
                                                    </select>
                                                </div>
                                            )}
                                        </div>

                                        <div className="flex gap-2 mt-6">
                                            <button
                                                onClick={handleAddResource}
                                                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                            >
                                                Add Resource
                                            </button>
                                            <button
                                                onClick={() => {
                                                    setShowResourceModal(false)
                                                    setNewResource({
                                                        title: '',
                                                        description: '',
                                                        resource_type: 'LINK',
                                                        content: '',
                                                        success_criteria_id: null,
                                                        sort_order: 0
                                                    })
                                                }}
                                                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
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
            </div >

            {/* Comments Modal */}
            {
                showCommentsModal && pocId && (
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
                )
            }

            {/* Resources Modal */}
            {showResourcesModal && pocId && (
                <ResourcesModal
                    pocId={pocId}
                    taskId={resourcesModalTaskId}
                    taskGroupId={resourcesModalTaskGroupId}
                    taskTitle={resourcesModalTitle}
                    onClose={() => {
                        setShowResourcesModal(false)
                        setResourcesModalTaskId(undefined)
                        setResourcesModalTaskGroupId(undefined)
                        setResourcesModalTitle('')
                    }}
                />
            )}

            {/* Document Generation Modal */}
            {
                showDocumentModal && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                            <h3 className="text-xl font-semibold mb-4">Generate POC Document</h3>

                            <p className="text-gray-600 mb-6">
                                Choose the format for your POC document. The document will include all POC details,
                                success criteria, tasks, and resources.
                            </p>

                            <div className="space-y-3 mb-6">
                                <button
                                    onClick={() => handleGenerateDocument('pdf')}
                                    disabled={generatingDocument}
                                    className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center gap-2"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                    </svg>
                                    {generatingDocument ? 'Generating...' : 'Download as PDF'}
                                </button>

                                <button
                                    onClick={() => handleGenerateDocument('markdown')}
                                    disabled={generatingDocument}
                                    className="w-full px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:bg-gray-400 flex items-center justify-center gap-2"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                    {generatingDocument ? 'Generating...' : 'Download as Markdown'}
                                </button>
                            </div>

                            <button
                                onClick={() => setShowDocumentModal(false)}
                                disabled={generatingDocument}
                                className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:bg-gray-100"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                )
            }

            {/* Task Assignment Modal */}
            {showAssignmentModal && assignmentModalTask && pocId && (
                <TaskAssignmentModal
                    pocId={pocId}
                    taskId={assignmentModalTask.id!}
                    taskTitle={assignmentModalTask.title}
                    participants={participants}
                    currentAssignees={assignmentModalTask.assignees}
                    onClose={() => {
                        setShowAssignmentModal(false)
                        setAssignmentModalTask(null)
                    }}
                    onAssigned={handleAssignmentComplete}
                />
            )}

            {/* Status Comment Modal */}
            {showStatusCommentModal && pendingStatusChange && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                        <h3 className="text-xl font-semibold mb-2">
                            {pendingStatusChange.status === 'partially_satisfied' ? 'Partially Satisfied' : 'Not Satisfied'} — Comment Required
                        </h3>
                        <p className="text-gray-600 mb-4 text-sm">
                            Please provide a comment explaining why this {pendingStatusChange.type === 'task' ? 'task' : 'task group'} is being marked as{' '}
                            <strong>{pendingStatusChange.status === 'partially_satisfied' ? 'Partially Satisfied' : 'Not Satisfied'}</strong>.
                        </p>
                        <textarea
                            value={statusCommentText}
                            onChange={(e) => setStatusCommentText(e.target.value)}
                            placeholder="Enter your comment here (required)..."
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            rows={4}
                            autoFocus
                        />
                        <div className="flex justify-end gap-3 mt-4">
                            <button
                                onClick={() => {
                                    setShowStatusCommentModal(false)
                                    setPendingStatusChange(null)
                                    setStatusCommentText('')
                                }}
                                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleStatusCommentSubmit}
                                disabled={!statusCommentText.trim()}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-sm"
                            >
                                Submit
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Criteria Edit Modal */}
            {showCriteriaEditModal && criteriaEditTaskId && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                        <h3 className="text-xl font-semibold mb-4">Link Success Criteria</h3>
                        <p className="text-gray-600 mb-4 text-sm">
                            Select which success criteria this task should be linked to.
                        </p>
                        <div className="border border-gray-300 rounded-lg p-3 max-h-60 overflow-y-auto space-y-1">
                            {successCriteria.length === 0 ? (
                                <p className="text-sm text-gray-500">No success criteria defined yet</p>
                            ) : (
                                successCriteria.map((criteria) => (
                                    <label key={criteria.id} className="flex items-center py-2 px-2 hover:bg-gray-50 rounded cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={criteriaEditSelectedIds.includes(criteria.id!)}
                                            onChange={(e) => {
                                                if (e.target.checked) {
                                                    setCriteriaEditSelectedIds([...criteriaEditSelectedIds, criteria.id!])
                                                } else {
                                                    setCriteriaEditSelectedIds(criteriaEditSelectedIds.filter(id => id !== criteria.id))
                                                }
                                            }}
                                            className="h-4 w-4 text-purple-600 rounded"
                                        />
                                        <span className="ml-2 text-sm text-gray-900">{criteria.title}</span>
                                    </label>
                                ))
                            )}
                        </div>
                        <div className="flex justify-end gap-3 mt-4">
                            <button
                                onClick={() => {
                                    setShowCriteriaEditModal(false)
                                    setCriteriaEditTaskId(null)
                                    setCriteriaEditSelectedIds([])
                                }}
                                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSaveCriteriaEdit}
                                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm"
                            >
                                Save
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Criteria Task List Modal */}
            {showCriteriaTaskListModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[70vh] flex flex-col">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">{criteriaTaskListTitle}</h3>
                        <ul className="space-y-2 overflow-y-auto flex-1 mb-4">
                            {criteriaTaskListNames.map((name, idx) => (
                                <li key={idx} className="flex items-center gap-2 text-sm text-gray-800">
                                    <span className="w-1.5 h-1.5 rounded-full bg-gray-400 flex-shrink-0" />
                                    {name}
                                </li>
                            ))}
                        </ul>
                        <div className="flex justify-end">
                            <button
                                onClick={() => setShowCriteriaTaskListModal(false)}
                                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div >
    )
}
