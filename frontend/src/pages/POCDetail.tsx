import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api, API_URL } from '../lib/api'
import toast from 'react-hot-toast'
import { useAuthStore } from '../store/authStore'
import POCForm from '../components/POCForm'
import CustomerPOCView from '../components/CustomerPOCView'

export default function POCDetail() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const { user } = useAuthStore()
    const [poc, setPoc] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [isEditing, setIsEditing] = useState(false)

    const isCustomer = user?.role === 'customer'

    useEffect(() => {
        if (id) {
            fetchPOC()
        }
    }, [id])

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

    // Show customer view for customer users
    if (isCustomer) {
        return (
            <div className="p-6">
                <div className="mb-4">
                    <button
                        onClick={() => navigate('pocs')}
                        className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                    >
                        ← Back to List
                    </button>
                </div>
                <CustomerPOCView pocId={parseInt(id!)} />
            </div>
        )
    }

    if (isEditing) {
        return (
            <div className="p-6">
                <POCForm
                    pocId={parseInt(id!)}
                    initialData={poc}
                    onClose={() => {
                        setIsEditing(false)
                        fetchPOC()
                    }}
                />
            </div>
        )
    }

    return (
        <div className="p-6">
            <div className="bg-white rounded-lg shadow-md">
                <div className="border-b border-gray-200 px-6 py-4">
                    <div className="flex justify-between items-center">
                        <div className="flex items-center gap-4">
                            {poc.customer_logo_url && (
                                <img
                                    src={`${API_URL}${poc.customer_logo_url}`}
                                    alt={poc.customer_company_name}
                                    className="h-16 w-16 object-contain"
                                />
                            )}
                            <div>
                                <h1 className="text-3xl font-bold text-gray-900">{poc.title}</h1>
                                <p className="text-gray-600 mt-1">{poc.customer_company_name}</p>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            {!isCustomer && (
                                <button
                                    onClick={() => setIsEditing(true)}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                >
                                    Edit POC
                                </button>
                            )}
                            <button
                                onClick={() => navigate('pocs')}
                                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                            >
                                Back to List
                            </button>
                        </div>
                    </div>
                </div>

                <div className="p-6">
                    <div className="grid grid-cols-2 gap-6">
                        <div>
                            <h3 className="text-sm font-medium text-gray-500 mb-1">Status</h3>
                            <p className="text-gray-900 capitalize">{poc.status}</p>
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-gray-500 mb-1">Duration</h3>
                            <p className="text-gray-900">
                                {poc.start_date && poc.end_date
                                    ? `${new Date(poc.start_date).toLocaleDateString()} - ${new Date(poc.end_date).toLocaleDateString()}`
                                    : 'Not set'}
                            </p>
                        </div>
                    </div>

                    {poc.description && (
                        <div className="mt-6">
                            <h3 className="text-sm font-medium text-gray-500 mb-1">Description</h3>
                            <p className="text-gray-900 whitespace-pre-wrap">{poc.description}</p>
                        </div>
                    )}

                    {poc.executive_summary && (
                        <div className="mt-6">
                            <h3 className="text-sm font-medium text-gray-500 mb-1">Executive Summary</h3>
                            <p className="text-gray-900 whitespace-pre-wrap">{poc.executive_summary}</p>
                        </div>
                    )}

                    {poc.objectives && (
                        <div className="mt-6">
                            <h3 className="text-sm font-medium text-gray-500 mb-1">Objectives</h3>
                            <p className="text-gray-900 whitespace-pre-wrap">{poc.objectives}</p>
                        </div>
                    )}

                    {poc.products && poc.products.length > 0 && (
                        <div className="mt-6">
                            <h3 className="text-sm font-medium text-gray-500 mb-2">Products</h3>
                            <div className="flex flex-wrap gap-2">
                                {poc.products.map((product: any) => (
                                    <span key={product.id} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                                        {product.name}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

