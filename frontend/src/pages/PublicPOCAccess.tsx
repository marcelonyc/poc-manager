import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api, API_URL } from '../lib/api'
import toast from 'react-hot-toast'
import CustomerPOCView from '../components/CustomerPOCView'

export default function PublicPOCAccess() {
    const { token } = useParams<{ token: string }>()
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [pocData, setPocData] = useState<any>(null)
    const [pocTasks, setPocTasks] = useState<any[]>([])
    const [pocTaskGroups, setPocTaskGroups] = useState<any[]>([])
    const [successCriteria, setSuccessCriteria] = useState<any[]>([])

    useEffect(() => {
        if (token) {
            fetchPublicPOC()
        }
    }, [token])

    const fetchPublicPOC = async () => {
        try {
            const [pocResponse, tasksResponse, taskGroupsResponse, criteriaResponse] = await Promise.all([
                api.get(`/public/pocs/${token}`),
                api.get(`/public/pocs/${token}/tasks`),
                api.get(`/public/pocs/${token}/task-groups`),
                api.get(`/public/pocs/${token}/success-criteria`)
            ])

            setPocData({
                ...pocResponse.data,
                access_token: token  // Add token to pocData for comments
            })
            setPocTasks(tasksResponse.data || [])
            setPocTaskGroups(taskGroupsResponse.data || [])
            setSuccessCriteria(criteriaResponse.data || [])
        } catch (error: any) {
            setError(error.response?.data?.detail || 'Failed to load POC. The link may be invalid or expired.')
            toast.error('Invalid or expired public link')
        } finally {
            setLoading(false)
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

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <h2 className="text-lg font-semibold text-red-900 mb-2">Access Error</h2>
                    <p className="text-red-800">{error}</p>
                    <button
                        onClick={() => navigate('/')}
                        className="mt-4 px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50"
                    >
                        Go to Home
                    </button>
                </div>
            </div>
        )
    }

    if (!pocData) {
        return (
            <div className="p-6">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-yellow-800">POC not found</p>
                </div>
            </div>
        )
    }

    // Use a custom read-only view by passing the public POC data
    return (
        <div className="p-6">
            <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                    ℹ️ You are viewing this POC via a public share link. Some features may be limited.
                </p>
            </div>
            <CustomerPOCView
                pocId={pocData.id}
                isPublicAccess={true}
                publicPocData={pocData}
                publicPocTasks={pocTasks}
                publicPocTaskGroups={pocTaskGroups}
                publicSuccessCriteria={successCriteria}
                publicAccessToken={token}
            />
        </div>
    )
}
