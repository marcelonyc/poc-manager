import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { api } from '../lib/api'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

interface TenantInvitationInfo {
    email: string
    tenant_name: string
    role: string
    invited_by_email: string
    expires_at: string
}

export default function AcceptTenantInvitation() {
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()
    const token = searchParams.get('token')
    const { isAuthenticated, user } = useAuthStore()

    const [loading, setLoading] = useState(true)
    const [validating, setValidating] = useState(true)
    const [invitationInfo, setInvitationInfo] = useState<TenantInvitationInfo | null>(null)
    const [error, setError] = useState('')
    const [submitting, setSubmitting] = useState(false)

    useEffect(() => {
        if (!token) {
            setError('Invalid invitation link')
            setValidating(false)
            setLoading(false)
            return
        }
        validateInvitation()
    }, [token])

    const validateInvitation = async () => {
        try {
            setValidating(true)
            const response = await api.get(`/tenant-invitations/validate/${token}`)
            setInvitationInfo(response.data)
            setError('')
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Invalid or expired invitation')
        } finally {
            setValidating(false)
            setLoading(false)
        }
    }

    const handleAccept = async () => {
        if (!isAuthenticated) {
            // Redirect to login with return URL
            navigate(`/login?returnUrl=/tenant-invitation?token=${token}`)
            return
        }

        // Check if logged-in user matches invitation email
        if (user?.email !== invitationInfo?.email) {
            toast.error(`This invitation is for ${invitationInfo?.email}. Please log in with that account.`)
            navigate(`/login?returnUrl=/tenant-invitation?token=${token}`)
            return
        }

        try {
            setSubmitting(true)
            const response = await api.post('/tenant-invitations/accept', { token })

            toast.success(response.data.message || 'Successfully accepted invitation!')

            // Redirect to login to refresh tenant list
            navigate('login?message=Invitation accepted! Please log in to access your new tenant.')
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to accept invitation')
            toast.error(err.response?.data?.detail || 'Failed to accept invitation')
        } finally {
            setSubmitting(false)
        }
    }

    if (loading || validating) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Validating invitation...</p>
                </div>
            </div>
        )
    }

    if (error && !invitationInfo) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
                    <div className="text-center">
                        <svg
                            className="mx-auto h-12 w-12 text-red-500"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                            />
                        </svg>
                        <h2 className="mt-4 text-xl font-semibold text-gray-900">Invalid Invitation</h2>
                        <p className="mt-2 text-gray-600">{error}</p>
                        <button
                            onClick={() => navigate('login')}
                            className="mt-6 w-full px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                        >
                            Go to Login
                        </button>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
                <div className="text-center mb-6">
                    <svg
                        className="mx-auto h-12 w-12 text-indigo-600"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76"
                        />
                    </svg>
                    <h2 className="mt-4 text-2xl font-bold text-gray-900">
                        Tenant Invitation
                    </h2>
                    <p className="mt-2 text-sm text-gray-600">
                        You've been invited to join a tenant
                    </p>
                </div>

                {invitationInfo && (
                    <div className="space-y-4">
                        <div className="bg-indigo-50 rounded-lg p-4">
                            <h3 className="text-sm font-medium text-gray-900 mb-3">Invitation Details</h3>
                            <dl className="space-y-2">
                                <div>
                                    <dt className="text-xs text-gray-600">Tenant</dt>
                                    <dd className="text-sm font-medium text-gray-900">{invitationInfo.tenant_name}</dd>
                                </div>
                                <div>
                                    <dt className="text-xs text-gray-600">Role</dt>
                                    <dd className="text-sm font-medium text-gray-900">{invitationInfo.role}</dd>
                                </div>
                                <div>
                                    <dt className="text-xs text-gray-600">Invited by</dt>
                                    <dd className="text-sm font-medium text-gray-900">{invitationInfo.invited_by_email}</dd>
                                </div>
                                <div>
                                    <dt className="text-xs text-gray-600">Your email</dt>
                                    <dd className="text-sm font-medium text-gray-900">{invitationInfo.email}</dd>
                                </div>
                            </dl>
                        </div>

                        {!isAuthenticated && (
                            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                                <p className="text-sm text-yellow-800">
                                    You need to log in to accept this invitation.
                                </p>
                            </div>
                        )}

                        {isAuthenticated && user?.email !== invitationInfo.email && (
                            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                <p className="text-sm text-red-800">
                                    You are logged in as <strong>{user?.email}</strong>, but this invitation is for{' '}
                                    <strong>{invitationInfo.email}</strong>. Please log out and log in with the correct account.
                                </p>
                            </div>
                        )}

                        {error && (
                            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                <p className="text-sm text-red-800">{error}</p>
                            </div>
                        )}

                        <button
                            onClick={handleAccept}
                            disabled={submitting}
                            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {submitting ? (
                                <span className="flex items-center">
                                    <svg
                                        className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                                        xmlns="http://www.w3.org/2000/svg"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                    >
                                        <circle
                                            className="opacity-25"
                                            cx="12"
                                            cy="12"
                                            r="10"
                                            stroke="currentColor"
                                            strokeWidth="4"
                                        ></circle>
                                        <path
                                            className="opacity-75"
                                            fill="currentColor"
                                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                        ></path>
                                    </svg>
                                    Accepting...
                                </span>
                            ) : isAuthenticated ? (
                                'Accept Invitation'
                            ) : (
                                'Log In to Accept'
                            )}
                        </button>

                        <button
                            onClick={() => navigate('login')}
                            className="w-full py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                            Cancel
                        </button>
                    </div>
                )}
            </div>
        </div>
    )
}
