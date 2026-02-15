import type { CalendarTask } from './TaskCalendar'

interface TaskDetailModalProps {
    task: CalendarTask
    onClose: () => void
}

const STATUS_LABELS: Record<string, string> = {
    not_started: 'Not Started',
    in_progress: 'In Progress',
    completed: 'Completed',
    blocked: 'Blocked',
    satisfied: 'Satisfied',
    partially_satisfied: 'Partially Satisfied',
    not_satisfied: 'Not Satisfied',
}

const STATUS_BADGES: Record<string, string> = {
    not_started: 'bg-gray-100 text-gray-800',
    in_progress: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    blocked: 'bg-red-100 text-red-800',
    satisfied: 'bg-emerald-100 text-emerald-800',
    partially_satisfied: 'bg-yellow-100 text-yellow-800',
    not_satisfied: 'bg-orange-100 text-orange-800',
}

export default function TaskDetailModal({ task, onClose }: TaskDetailModalProps) {
    const statusLabel = STATUS_LABELS[task.status || 'not_started'] || 'Unknown'
    const statusBadge = STATUS_BADGES[task.status || 'not_started'] || 'bg-gray-100 text-gray-800'

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
            <div
                className="bg-white rounded-xl shadow-2xl max-w-lg w-full mx-4 overflow-hidden"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="bg-gradient-to-r from-indigo-600 to-indigo-500 px-6 py-4 text-white">
                    <div className="flex items-start justify-between">
                        <div className="flex-1 mr-4">
                            <div className="flex items-center gap-2 mb-1">
                                {task.isGroup && (
                                    <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">📁 Task Group</span>
                                )}
                                {task.groupTitle && (
                                    <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">Group: {task.groupTitle}</span>
                                )}
                            </div>
                            <h2 className="text-xl font-bold">{task.title}</h2>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-1 hover:bg-white/20 rounded-lg transition-colors"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>

                {/* Body */}
                <div className="px-6 py-5 space-y-5 max-h-[60vh] overflow-y-auto">
                    {/* Status */}
                    <div className="flex items-center gap-3">
                        <span className="text-sm font-medium text-gray-500 w-20">Status</span>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusBadge}`}>
                            {statusLabel}
                        </span>
                    </div>

                    {/* Dates */}
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <span className="text-sm font-medium text-gray-500 block mb-1">Start Date</span>
                            <span className="text-sm text-gray-900">
                                {task.start_date ? new Date(task.start_date + 'T00:00:00').toLocaleDateString('en-US', {
                                    weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
                                }) : '—'}
                            </span>
                        </div>
                        <div>
                            <span className="text-sm font-medium text-gray-500 block mb-1">Due Date</span>
                            <span className="text-sm text-gray-900">
                                {task.due_date ? new Date(task.due_date + 'T00:00:00').toLocaleDateString('en-US', {
                                    weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
                                }) : '—'}
                            </span>
                        </div>
                    </div>

                    {/* Duration */}
                    {task.start_date && task.due_date && (
                        <div className="flex items-center gap-3">
                            <span className="text-sm font-medium text-gray-500 w-20">Duration</span>
                            <span className="text-sm text-gray-900">
                                {Math.max(1, Math.ceil((new Date(task.due_date).getTime() - new Date(task.start_date).getTime()) / (1000 * 60 * 60 * 24)) + 1)} day(s)
                            </span>
                        </div>
                    )}

                    {/* Description */}
                    {task.description && (
                        <div>
                            <span className="text-sm font-medium text-gray-500 block mb-2">Description</span>
                            <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-700 whitespace-pre-wrap">
                                {task.description}
                            </div>
                        </div>
                    )}

                    {/* Assignees */}
                    {task.assignees && task.assignees.length > 0 && (
                        <div>
                            <span className="text-sm font-medium text-gray-500 block mb-2">Assignees</span>
                            <div className="flex flex-wrap gap-2">
                                {task.assignees.map((a) => (
                                    <div
                                        key={a.id}
                                        className="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-lg px-3 py-1.5"
                                        title={a.participant_email}
                                    >
                                        <div className="w-6 h-6 bg-blue-200 rounded-full flex items-center justify-center text-blue-700 text-xs font-bold">
                                            {a.participant_name.charAt(0).toUpperCase()}
                                        </div>
                                        <div>
                                            <div className="text-sm font-medium text-gray-900">{a.participant_name}</div>
                                            <div className="text-xs text-gray-500">{a.participant_email}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Success Criteria */}
                    {task.success_criteria_ids && task.success_criteria_ids.length > 0 && (
                        <div>
                            <span className="text-sm font-medium text-gray-500 block mb-1">Linked Success Criteria</span>
                            <span className="text-sm text-gray-700">
                                {task.success_criteria_ids.length} criteria linked
                            </span>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="border-t border-gray-200 px-6 py-3 flex justify-end bg-gray-50">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 text-sm font-medium transition-colors"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    )
}
