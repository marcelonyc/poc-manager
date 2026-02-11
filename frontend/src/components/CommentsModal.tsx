import { useState, useEffect } from 'react'
import api from '../lib/api'
import { toast } from 'react-hot-toast'

interface Comment {
    id: number
    subject: string
    content: string
    user_id: number
    poc_id: number
    poc_task_id?: number
    poc_task_group_id?: number
    is_internal: boolean
    created_at: string
    updated_at?: string
    user?: {
        id: number
        email: string
        full_name: string
    }
}

interface CommentsModalProps {
    pocId: number
    taskId?: number
    taskGroupId?: number
    isPublicAccess?: boolean
    publicPocData?: any
    onClose: () => void
}

export default function CommentsModal({ pocId, taskId, taskGroupId, isPublicAccess = false, publicPocData, onClose }: CommentsModalProps) {
    const [comments, setComments] = useState<Comment[]>([])
    const [loading, setLoading] = useState(true)
    const [showNewCommentForm, setShowNewCommentForm] = useState(false)
    const [replyToSubject, setReplyToSubject] = useState<string | null>(null)
    const [newComment, setNewComment] = useState({
        subject: '',
        content: '',
        is_internal: false,
        guest_name: publicPocData?.customer_company_name || '',
        guest_email: ''
    })

    const subjects = Array.from(new Set(comments.map(c => c.subject)))

    useEffect(() => {
        // Validate that either taskId or taskGroupId is provided
        if (!taskId && !taskGroupId) {
            console.error('CommentsModal requires either taskId or taskGroupId')
            return
        }
        fetchComments()
    }, [pocId, taskId, taskGroupId])

    const fetchComments = async () => {
        try {
            // Validate that either taskId or taskGroupId is provided
            if (!taskId && !taskGroupId) {
                setLoading(false)
                return
            }

            setLoading(true)
            let url = isPublicAccess
                ? `/public/pocs/${publicPocData?.access_token || ''}/comments?`
                : `/pocs/${pocId}/comments?`
            if (taskId) url += `task_id=${taskId}`
            if (taskGroupId) url += `task_group_id=${taskGroupId}`

            const response = await api.get(url)
            setComments(response.data)
        } catch (error: any) {
            toast.error('Failed to load comments')
        } finally {
            setLoading(false)
        }
    }

    const handleCreateComment = async () => {
        // Validate that either taskId or taskGroupId is provided
        if (!taskId && !taskGroupId) {
            toast.error('Comment must be associated with either a task or task group')
            return
        }

        if (!newComment.subject.trim() || !newComment.content.trim()) {
            toast.error('Subject and content are required')
            return
        }

        if (isPublicAccess && (!newComment.guest_name.trim() || !newComment.guest_email.trim())) {
            toast.error('Name and email are required')
            return
        }

        if (newComment.content.length > 1000) {
            toast.error('Content must be 1000 characters or less')
            return
        }

        try {
            const commentData = {
                ...newComment,
                poc_task_id: taskId || undefined,
                poc_task_group_id: taskGroupId || undefined
            }

            let url = ''
            if (isPublicAccess) {
                // Remove is_internal and undefined fields for public comments
                delete commentData.is_internal
                url = `/public/pocs/${publicPocData?.access_token}/comments`
                if (taskId) url += `?poc_task_id=${taskId}`
                else if (taskGroupId) url += `?poc_task_group_id=${taskGroupId}`
                await api.post(url, commentData)
            } else {
                url = `/pocs/${pocId}/comments`
                if (taskId) url += `?task_id=${taskId}`
                else if (taskGroupId) url += `?task_group_id=${taskGroupId}`
                await api.post(url, commentData)
            }

            toast.success('Comment added')
            setNewComment({
                subject: '',
                content: '',
                is_internal: false,
                guest_name: publicPocData?.customer_company_name || '',
                guest_email: ''
            })
            setShowNewCommentForm(false)
            setReplyToSubject(null)
            fetchComments()
        } catch (error: any) {
            toast.error('Failed to add comment')
        }
    }

    const handleReply = (subject: string) => {
        setReplyToSubject(subject)
        setNewComment({ ...newComment, subject })
        setShowNewCommentForm(true)
    }

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString()
    }

    const groupedComments = subjects.reduce((acc, subject) => {
        acc[subject] = comments.filter(c => c.subject === subject)
        return acc
    }, {} as Record<string, Comment[]>)

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
                {/* Header */}
                <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                    <h2 className="text-xl font-semibold text-gray-900">
                        Comments {taskId && '- Task'} {taskGroupId && '- Task Group'}
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    {loading ? (
                        <div className="text-center py-8 text-gray-500">Loading comments...</div>
                    ) : (
                        <>
                            {/* New Comment Button */}
                            {!showNewCommentForm && (
                                <button
                                    onClick={() => {
                                        setShowNewCommentForm(true)
                                        setReplyToSubject(null)
                                        setNewComment({
                                            subject: '',
                                            content: '',
                                            is_internal: false,
                                            guest_name: publicPocData?.customer_company_name || '',
                                            guest_email: ''
                                        })
                                    }}
                                    className="mb-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                >
                                    + New Comment
                                </button>
                            )}

                            {/* New Comment Form */}
                            {showNewCommentForm && (
                                <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                    <h3 className="font-semibold text-gray-900 mb-3">
                                        {replyToSubject ? `Reply to: ${replyToSubject}` : 'New Comment'}
                                    </h3>

                                    {!replyToSubject && (
                                        <div className="mb-3">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                                Subject *
                                            </label>
                                            <input
                                                type="text"
                                                value={newComment.subject}
                                                onChange={(e) => setNewComment({ ...newComment, subject: e.target.value })}
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                                placeholder="Enter subject"
                                            />
                                        </div>
                                    )}

                                    {isPublicAccess && (
                                        <>
                                            <div className="mb-3">
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Your Name *
                                                </label>
                                                <input
                                                    type="text"
                                                    value={newComment.guest_name}
                                                    onChange={(e) => setNewComment({ ...newComment, guest_name: e.target.value })}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                                    placeholder="Your name"
                                                />
                                            </div>

                                            <div className="mb-3">
                                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                                    Your Email *
                                                </label>
                                                <input
                                                    type="email"
                                                    value={newComment.guest_email}
                                                    onChange={(e) => setNewComment({ ...newComment, guest_email: e.target.value })}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                                    placeholder="your.email@example.com"
                                                />
                                            </div>
                                        </>
                                    )}

                                    <div className="mb-3">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">
                                            Content * (max 1000 characters)
                                        </label>
                                        <textarea
                                            value={newComment.content}
                                            onChange={(e) => setNewComment({ ...newComment, content: e.target.value })}
                                            rows={4}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                            placeholder="Enter your comment"
                                        />
                                        <div className="text-xs text-gray-500 mt-1">
                                            {newComment.content.length}/1000 characters
                                        </div>
                                    </div>

                                    {!isPublicAccess && (
                                        <div className="mb-3">
                                            <label className="flex items-center">
                                                <input
                                                    type="checkbox"
                                                    checked={newComment.is_internal}
                                                    onChange={(e) => setNewComment({ ...newComment, is_internal: e.target.checked })}
                                                    className="h-4 w-4 text-blue-600 rounded"
                                                />
                                                <span className="ml-2 text-sm text-gray-900">
                                                    Internal comment (not visible to customers)
                                                </span>
                                            </label>
                                        </div>
                                    )}

                                    <div className="flex gap-2">
                                        <button
                                            onClick={handleCreateComment}
                                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                        >
                                            Post Comment
                                        </button>
                                        <button
                                            onClick={() => {
                                                setShowNewCommentForm(false)
                                                setReplyToSubject(null)
                                                setNewComment({
                                                    subject: '',
                                                    content: '',
                                                    is_internal: false,
                                                    guest_name: publicPocData?.customer_company_name || '',
                                                    guest_email: ''
                                                })
                                            }}
                                            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* Comments List */}
                            {comments.length === 0 ? (
                                <div className="text-center py-8 text-gray-500">
                                    No comments yet. Be the first to comment!
                                </div>
                            ) : (
                                <div className="space-y-6">
                                    {subjects.map(subject => (
                                        <div key={subject} className="border border-gray-200 rounded-lg p-4">
                                            <div className="flex justify-between items-start mb-3">
                                                <h3 className="text-lg font-semibold text-gray-900">{subject}</h3>
                                                <button
                                                    onClick={() => handleReply(subject)}
                                                    className="text-sm text-blue-600 hover:text-blue-700"
                                                >
                                                    Reply
                                                </button>
                                            </div>

                                            <div className="space-y-3">
                                                {groupedComments[subject]?.map(comment => (
                                                    <div key={comment.id} className="pl-4 border-l-2 border-gray-200">
                                                        <div className="flex items-start gap-3">
                                                            <div className="flex-1">
                                                                <div className="flex items-center gap-2 mb-1">
                                                                    <span className="font-medium text-sm text-gray-900">
                                                                        {comment.user?.full_name || comment.user?.email || 'Unknown User'}
                                                                    </span>
                                                                    <span className="text-xs text-gray-500">
                                                                        {formatDate(comment.created_at)}
                                                                    </span>
                                                                    {comment.is_internal && (
                                                                        <span className="px-2 py-0.5 bg-yellow-100 text-yellow-800 text-xs rounded">
                                                                            Internal
                                                                        </span>
                                                                    )}
                                                                </div>
                                                                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                                                                    {comment.content}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}
