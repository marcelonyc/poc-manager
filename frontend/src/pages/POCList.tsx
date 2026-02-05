import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, API_URL } from '../lib/api'
import toast from 'react-hot-toast'
import { useAuthStore } from '../store/authStore'
import POCForm from '../components/POCForm'
import DemoLimitsBanner from '../components/DemoLimitsBanner'

interface POC {
    id: number
    title: string
    customer_company_name: string
    customer_logo_url?: string | null
    status: string
    start_date: string
    end_date: string
    created_at: string
}

export default function POCList() {
    const { user } = useAuthStore()
    const [pocs, setPocs] = useState<POC[]>([])
    const [loading, setLoading] = useState(true)
    const [showCreateForm, setShowCreateForm] = useState(false)
    const navigate = useNavigate()

    const isCustomer = user?.role === 'customer'

    useEffect(() => {
        fetchPOCs()
    }, [])

    const fetchPOCs = async () => {
        try {
            const response = await api.get('/pocs/')
            setPocs(response.data)
        } catch (error: any) {
            toast.error('Failed to fetch POCs')
        } finally {
            setLoading(false)
        }
    }

    const getStatusBadgeClass = (status: string) => {
        const classes: Record<string, string> = {
            draft: 'bg-gray-100 text-gray-800',
            active: 'bg-green-100 text-green-800',
            completed: 'bg-purple-100 text-purple-800',
            archived: 'bg-red-100 text-red-800',
        }
        return classes[status.toLowerCase()] || 'bg-gray-100 text-gray-800'
    }

    if (loading) {
        return (
            <div className="p-6">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading POCs...</p>
                </div>
            </div>
        )
    }

    if (showCreateForm) {
        return (
            <div className="p-6">
                <POCForm onClose={() => {
                    setShowCreateForm(false)
                    fetchPOCs()
                }} />
            </div>
        )
    }

    return (
        <div className="p-6">
            <DemoLimitsBanner />

            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-gray-900">POCs</h1>
                {!isCustomer && (
                    <button
                        onClick={() => setShowCreateForm(true)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        + Create POC
                    </button>
                )}
            </div>

            <div className="bg-white rounded-lg shadow-md overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                POC Title
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Customer
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Status
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Duration
                            </th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {pocs.length === 0 ? (
                            <tr>
                                <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                                    No POCs yet. Create your first POC to get started.
                                </td>
                            </tr>
                        ) : (
                            pocs.map((poc) => (
                                <tr key={poc.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-gray-900">{poc.title}</div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center gap-3">
                                            {poc.customer_logo_url && (
                                                <img
                                                    src={`${API_URL}${poc.customer_logo_url}`}
                                                    alt={poc.customer_company_name}
                                                    className="h-8 w-8 object-contain rounded"
                                                />
                                            )}
                                            <div className="text-sm text-gray-500">{poc.customer_company_name}</div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeClass(poc.status)}`}>
                                            {poc.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {poc.start_date && poc.end_date ? (
                                            <>
                                                {new Date(poc.start_date).toLocaleDateString()} - {new Date(poc.end_date).toLocaleDateString()}
                                            </>
                                        ) : (
                                            'Not set'
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <Link
                                            to={`/pocs/${poc.id}`}
                                            className="text-blue-600 hover:text-blue-900 mr-4"
                                        >
                                            View
                                        </Link>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

