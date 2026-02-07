import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import toast from 'react-hot-toast'

interface Participant {
    id?: number
    user_id?: number
    email?: string
    full_name?: string
    is_sales_engineer: boolean
    is_customer: boolean
    joined_at?: string
    status?: string
}

interface TaskAssignee {
    id: number
    participant_id: number
    participant_name: string
    participant_email: string
    assigned_at: string
}

interface TaskAssignmentModalProps {
    pocId: number
    taskId: number
    taskTitle: string
    participants: Participant[]
    currentAssignees?: TaskAssignee[]
    onClose: () => void
    onAssigned: () => void
}

export default function TaskAssignmentModal({
    pocId,
    taskId,
    taskTitle,
    participants,
    currentAssignees = [],
    onClose,
    onAssigned
}: TaskAssignmentModalProps) {
    const [selectedParticipantIds, setSelectedParticipantIds] = useState<Set<number>>(new Set())
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        // Pre-select currently assigned participants
        const assignedIds = new Set(currentAssignees.map(a => a.participant_id))
        setSelectedParticipantIds(assignedIds)
    }, [currentAssignees])

    const toggleParticipant = (participantId: number) => {
        const newSelected = new Set(selectedParticipantIds)
        if (newSelected.has(participantId)) {
            newSelected.delete(participantId)
        } else {
            newSelected.add(participantId)
        }
        setSelectedParticipantIds(newSelected)
    }

    const handleAssign = async () => {
        setLoading(true)
        try {
            if (selectedParticipantIds.size === 0) {
                // Unassign all
                await api.delete(`/tasks/pocs/${pocId}/tasks/${taskId}/assign`)
                toast.success('All participants unassigned')
            } else {
                // Assign selected participants
                await api.post(`/tasks/pocs/${pocId}/tasks/${taskId}/assign`, {
                    participant_ids: Array.from(selectedParticipantIds)
                })
                toast.success('Participants assigned successfully')
            }
            onAssigned()
            onClose()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to assign participants')
        } finally {
            setLoading(false)
        }
    }

    // Filter active participants (accepted or pending/invited)
    // Accepted participants have joined the POC
    // Pending/invited participants have invitations that haven't been accepted yet
    const activeParticipants = participants.filter(p =>
        p.status === 'accepted' || p.status === 'pending' || p.status === 'invited'
    )

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="border-b border-gray-200 px-6 py-4">
                    <h2 className="text-xl font-semibold text-gray-900">Assign Participants to Task</h2>
                    <p className="text-sm text-gray-600 mt-1">{taskTitle}</p>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto px-6 py-4">
                    {activeParticipants.length === 0 ? (
                        <div className="text-center py-8">
                            <p className="text-gray-500">No participants available in this POC</p>
                            <p className="text-sm text-gray-400 mt-2">Add participants to assign tasks</p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            <p className="text-sm text-gray-600 mb-4">
                                Select one or more participants to assign to this task:
                            </p>
                            {activeParticipants.map((participant) => {
                                const participantId = participant.id || participant.user_id
                                if (!participantId) return null

                                const isSelected = selectedParticipantIds.has(participantId)

                                return (
                                    <div
                                        key={participantId}
                                        onClick={() => toggleParticipant(participantId)}
                                        className={`border rounded-lg p-4 cursor-pointer transition-all ${isSelected
                                            ? 'border-indigo-500 bg-indigo-50'
                                            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                                            }`}
                                    >
                                        <div className="flex items-start gap-3">
                                            <div className="flex items-center h-5">
                                                <input
                                                    type="checkbox"
                                                    checked={isSelected}
                                                    onChange={() => toggleParticipant(participantId)}
                                                    className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                                                />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2">
                                                    <p className="font-medium text-gray-900">
                                                        {participant.full_name || participant.email}
                                                    </p>
                                                    {participant.is_sales_engineer && (
                                                        <span className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded">
                                                            Sales Engineer
                                                        </span>
                                                    )}
                                                    {participant.is_customer && (
                                                        <span className="px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded">
                                                            Customer
                                                        </span>
                                                    )}
                                                    {(participant.status === 'pending' || participant.status === 'invited') && (
                                                        <span className="px-2 py-0.5 bg-yellow-100 text-yellow-800 text-xs rounded">
                                                            Pending
                                                        </span>
                                                    )}
                                                    {participant.status === 'expired' && (
                                                        <span className="px-2 py-0.5 bg-red-100 text-red-800 text-xs rounded">
                                                            Expired
                                                        </span>
                                                    )}
                                                </div>
                                                {participant.full_name && (
                                                    <p className="text-sm text-gray-600 mt-0.5">
                                                        {participant.email}
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
                    <div className="flex justify-between items-center">
                        <p className="text-sm text-gray-600">
                            {selectedParticipantIds.size} participant{selectedParticipantIds.size !== 1 ? 's' : ''} selected
                        </p>
                        <div className="flex gap-2">
                            <button
                                onClick={onClose}
                                disabled={loading}
                                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleAssign}
                                disabled={loading || activeParticipants.length === 0}
                                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Assigning...' : 'Assign'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
