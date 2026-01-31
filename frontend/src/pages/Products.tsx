import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import toast from 'react-hot-toast'
import { useAuthStore } from '../store/authStore'

interface Product {
    id: number
    name: string
    tenant_id: number
    created_at: string
    updated_at?: string
}

interface ProductWithUsage extends Product {
    poc_count: number
    poc_titles: string[]
}

export default function Products() {
    const { user } = useAuthStore()
    const [products, setProducts] = useState<Product[]>([])
    const [loading, setLoading] = useState(true)
    const [showForm, setShowForm] = useState(false)
    const [editingProduct, setEditingProduct] = useState<Product | null>(null)
    const [productName, setProductName] = useState('')
    const [submitting, setSubmitting] = useState(false)
    const [showDeleteModal, setShowDeleteModal] = useState(false)
    const [deletingProduct, setDeletingProduct] = useState<ProductWithUsage | null>(null)
    const [showRenameModal, setShowRenameModal] = useState(false)
    const [renamingProduct, setRenamingProduct] = useState<Product | null>(null)
    const [newName, setNewName] = useState('')

    useEffect(() => {
        fetchProducts()
    }, [])

    const fetchProducts = async () => {
        try {
            const response = await api.get('/products/')
            setProducts(response.data)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to fetch products')
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setSubmitting(true)

        try {
            if (editingProduct) {
                await api.put(`/products/${editingProduct.id}`, { name: productName })
                toast.success('Product updated successfully')
            } else {
                await api.post('/products/', { name: productName })
                toast.success('Product created successfully')
            }
            setShowForm(false)
            setEditingProduct(null)
            setProductName('')
            fetchProducts()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to save product')
        } finally {
            setSubmitting(false)
        }
    }

    const handleEdit = (product: Product) => {
        setEditingProduct(product)
        setProductName(product.name)
        setShowForm(true)
    }

    const handleRenameClick = (product: Product) => {
        setRenamingProduct(product)
        setNewName(product.name)
        setShowRenameModal(true)
    }

    const handleRenameConfirm = async () => {
        if (!renamingProduct) return

        setSubmitting(true)
        try {
            await api.put(`/products/${renamingProduct.id}`, { name: newName })
            toast.success('Product renamed successfully')
            setShowRenameModal(false)
            setRenamingProduct(null)
            setNewName('')
            fetchProducts()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to rename product')
        } finally {
            setSubmitting(false)
        }
    }

    const handleDeleteClick = async (product: Product) => {
        try {
            const response = await api.get(`/products/${product.id}`)
            setDeletingProduct(response.data)
            setShowDeleteModal(true)
        } catch (error: any) {
            toast.error('Failed to check product usage')
        }
    }

    const handleDeleteConfirm = async () => {
        if (!deletingProduct) return

        try {
            await api.delete(`/products/${deletingProduct.id}`)
            toast.success('Product deleted successfully')
            setShowDeleteModal(false)
            setDeletingProduct(null)
            fetchProducts()
        } catch (error: any) {
            if (error.response?.status === 400 && error.response?.data?.detail?.pocs) {
                // Product is in use, modal will show the POCs
                setDeletingProduct({
                    ...deletingProduct,
                    poc_count: error.response.data.detail.pocs.length,
                    poc_titles: error.response.data.detail.pocs.map((p: any) => p.title)
                })
            } else {
                toast.error(error.response?.data?.detail || 'Failed to delete product')
            }
        }
    }

    if (user?.role !== 'tenant_admin' && user?.role !== 'administrator') {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800">Access denied. Only Tenant Admins and Administrators can manage products.</p>
                </div>
            </div>
        )
    }

    if (loading) {
        return (
            <div className="p-6">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading products...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="p-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-gray-900">Product Management</h1>
                <button
                    onClick={() => {
                        setShowForm(!showForm)
                        setEditingProduct(null)
                        setProductName('')
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                    {showForm ? 'Cancel' : '+ Add Product'}
                </button>
            </div>

            {showForm && (
                <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                    <h2 className="text-xl font-semibold mb-4">{editingProduct ? 'Edit' : 'Add'} Product</h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Product Name *
                            </label>
                            <input
                                type="text"
                                required
                                value={productName}
                                onChange={(e) => setProductName(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="e.g., Enterprise Platform, Analytics Suite"
                            />
                        </div>
                        <div className="flex gap-3">
                            <button
                                type="submit"
                                disabled={submitting}
                                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                            >
                                {submitting ? 'Saving...' : editingProduct ? 'Update' : 'Create'}
                            </button>
                            <button
                                type="button"
                                onClick={() => {
                                    setShowForm(false)
                                    setEditingProduct(null)
                                    setProductName('')
                                }}
                                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="bg-white rounded-lg shadow-md overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Product Name
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Created
                            </th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {products.length === 0 ? (
                            <tr>
                                <td colSpan={3} className="px-6 py-12 text-center text-gray-500">
                                    No products yet. Create your first product to get started.
                                </td>
                            </tr>
                        ) : (
                            products.map((product) => (
                                <tr key={product.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-gray-900">{product.name}</div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-500">
                                            {new Date(product.created_at).toLocaleDateString()}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <button
                                            onClick={() => handleRenameClick(product)}
                                            className="text-blue-600 hover:text-blue-900 mr-4"
                                        >
                                            Rename
                                        </button>
                                        <button
                                            onClick={() => handleDeleteClick(product)}
                                            className="text-red-600 hover:text-red-900"
                                        >
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Rename Confirmation Modal */}
            {showRenameModal && renamingProduct && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
                    <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
                        <h2 className="text-xl font-bold text-gray-900 mb-4">Rename Product</h2>
                        <p className="text-sm text-gray-600 mb-4">
                            Are you sure you want to rename "{renamingProduct.name}"?
                        </p>
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                New Name *
                            </label>
                            <input
                                type="text"
                                required
                                value={newName}
                                onChange={(e) => setNewName(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={() => {
                                    setShowRenameModal(false)
                                    setRenamingProduct(null)
                                    setNewName('')
                                }}
                                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                disabled={submitting}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleRenameConfirm}
                                disabled={submitting || !newName || newName === renamingProduct.name}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                            >
                                {submitting ? 'Renaming...' : 'Confirm Rename'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Delete Confirmation Modal */}
            {showDeleteModal && deletingProduct && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
                    <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 p-6 max-h-[80vh] overflow-y-auto">
                        <h2 className="text-xl font-bold text-gray-900 mb-4">
                            {deletingProduct.poc_count > 0 ? 'Cannot Delete Product' : 'Delete Product'}
                        </h2>

                        {deletingProduct.poc_count > 0 ? (
                            <>
                                <p className="text-sm text-gray-600 mb-4">
                                    The product "{deletingProduct.name}" is currently in use by {deletingProduct.poc_count} POC(s) and cannot be deleted.
                                </p>
                                <div className="mb-4">
                                    <h3 className="font-medium text-gray-900 mb-2">POCs using this product:</h3>
                                    <div className="bg-gray-50 rounded-lg p-3 max-h-60 overflow-y-auto">
                                        <ul className="space-y-2">
                                            {deletingProduct.poc_titles.map((title, index) => (
                                                <li key={index} className="text-sm text-gray-700">
                                                    • {title}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                                <div className="flex justify-end">
                                    <button
                                        onClick={() => {
                                            setShowDeleteModal(false)
                                            setDeletingProduct(null)
                                        }}
                                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                    >
                                        Close
                                    </button>
                                </div>
                            </>
                        ) : (
                            <>
                                <p className="text-sm text-gray-600 mb-4">
                                    Are you sure you want to delete "{deletingProduct.name}"? This action cannot be undone.
                                </p>
                                <div className="flex gap-3 justify-end">
                                    <button
                                        onClick={() => {
                                            setShowDeleteModal(false)
                                            setDeletingProduct(null)
                                        }}
                                        className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={handleDeleteConfirm}
                                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                                    >
                                        Delete Product
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}
