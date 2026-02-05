import { useState } from 'react'
import { api, API_URL } from '../lib/api'
import toast from 'react-hot-toast'

interface LogoUploadProps {
    currentLogoUrl?: string | null
    onUploadSuccess?: (logoUrl: string) => void
    onDelete?: () => void
    uploadEndpoint: string
    deleteEndpoint: string
    label?: string
    description?: string
}

export default function LogoUpload({
    currentLogoUrl,
    onUploadSuccess,
    onDelete,
    uploadEndpoint,
    deleteEndpoint,
    label = "Logo",
    description = "Upload a logo image (max 2MB, JPEG/PNG/GIF/WebP)"
}: LogoUploadProps) {
    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)
    const [uploading, setUploading] = useState(false)
    const [deleting, setDeleting] = useState(false)

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) {
            // Validate file type
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if (!allowedTypes.includes(file.type)) {
                toast.error('Invalid file type. Please select a JPEG, PNG, GIF, or WebP image.')
                return
            }

            // Validate file size (2MB)
            if (file.size > 2 * 1024 * 1024) {
                toast.error('File too large. Maximum size is 2MB.')
                return
            }

            setSelectedFile(file)
            const reader = new FileReader()
            reader.onloadend = () => {
                setPreviewUrl(reader.result as string)
            }
            reader.readAsDataURL(file)
        }
    }

    const handleUpload = async () => {
        if (!selectedFile) return

        setUploading(true)
        try {
            const formData = new FormData()
            formData.append('logo', selectedFile)

            const response = await api.post(uploadEndpoint, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                }
            })

            toast.success('Logo uploaded successfully')
            setSelectedFile(null)
            setPreviewUrl(null)

            if (onUploadSuccess && response.data.logo_url) {
                onUploadSuccess(response.data.logo_url)
            }
        } catch (err: any) {
            console.error('Logo upload error:', err.response?.data)
            if (err.response?.data?.detail) {
                toast.error(err.response.data.detail)
            } else {
                toast.error('Failed to upload logo')
            }
        } finally {
            setUploading(false)
        }
    }

    const handleDelete = async () => {
        if (!confirm('Are you sure you want to delete this logo?')) return

        setDeleting(true)
        try {
            await api.delete(deleteEndpoint)
            toast.success('Logo deleted successfully')
            setPreviewUrl(null)

            if (onDelete) {
                onDelete()
            }
        } catch (err: any) {
            toast.error(err.response?.data?.detail || 'Failed to delete logo')
        } finally {
            setDeleting(false)
        }
    }

    const handleCancel = () => {
        setSelectedFile(null)
        setPreviewUrl(null)
    }

    const displayUrl = previewUrl || (currentLogoUrl ? `${API_URL}${currentLogoUrl}` : null)

    return (
        <div className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    {label}
                </label>
                <p className="text-sm text-gray-500 mb-3">{description}</p>

                {/* Current or preview image */}
                {displayUrl && (
                    <div className="mb-4 flex items-center space-x-4">
                        <img
                            src={displayUrl}
                            alt="Logo"
                            className="h-24 w-24 object-contain border border-gray-300 rounded-lg p-2 bg-white"
                        />
                        {currentLogoUrl && !previewUrl && (
                            <button
                                type="button"
                                onClick={handleDelete}
                                disabled={deleting}
                                className="px-4 py-2 text-sm text-red-600 hover:text-red-700 font-medium disabled:opacity-50"
                            >
                                {deleting ? 'Deleting...' : 'Remove Logo'}
                            </button>
                        )}
                    </div>
                )}

                {/* File input */}
                <div className="flex items-center space-x-4">
                    <label className="cursor-pointer">
                        <input
                            type="file"
                            accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
                            onChange={handleFileSelect}
                            className="hidden"
                        />
                        <span className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg border border-gray-300 text-sm font-medium inline-block">
                            {currentLogoUrl && !previewUrl ? 'Upload New Logo' : 'Choose File'}
                        </span>
                    </label>

                    {selectedFile && (
                        <>
                            <span className="text-sm text-gray-600">{selectedFile.name}</span>
                            <button
                                type="button"
                                onClick={handleUpload}
                                disabled={uploading}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium disabled:opacity-50"
                            >
                                {uploading ? 'Uploading...' : 'Upload'}
                            </button>
                            <button
                                type="button"
                                onClick={handleCancel}
                                disabled={uploading}
                                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-700 font-medium"
                            >
                                Cancel
                            </button>
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}
