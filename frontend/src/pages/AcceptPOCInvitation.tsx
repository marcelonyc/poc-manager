import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { api } from '../lib/api'
import toast from 'react-hot-toast'
import { useAuthStore } from '../store/authStore'

interface InvitationData {
    poc_id: number
    poc_title: string
    email: string
    full_name: string
    is_customer: boolean
    invited_by_name: string
    expires_at: string
    personal_message?: string
    user_exists: boolean
}

export default function AcceptPOCInvitation() {
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()
    const { user } = useAuthStore()
    const token = searchParams.get('token')

    const [loading, setLoading] = useState(true)
    const [submitting, setSubmitting] = useState(false)
    const [invitationData, setInvitationData] = useState<InvitationData | null>(null)
    const [error, setError] = useState<string>('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')

    useEffect(() => {
        if (token) {
            validateToken()
        } else {
            setError('Invalid invitation link')
            setLoading(false)
        }
    }, [token])

    const validateToken = async () => {
        try {
            const response = await api.get(`/poc-invitations/validate/${token}`)
            setInvitationData(response.data)

            // If user exists but not logged in, redirect to login
            if (response.data.user_exists && !user) {
                toast.error('Please log in to accept this invitation')
                setTimeout(() => {
                    navigate('/login', {
                        state: {
                            message: 'Please log in to accept the POC invitation',
                            redirectTo: `/accept-poc-invitation?token=${token}`
                        }
                    })
                }, 1500)
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Invalid or expired invitation')
        } finally {
            setLoading(false)
        }
    }

    const handleAccept = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!invitationData?.user_exists) {
            // New user - validate password
            if (!password) {
                setError('Password is required')
                return
            }

            if (password.length < 8) {
                setError('Password must be at least 8 characters')
                return
            }

            if (password !== confirmPassword) {
                setError('Passwords do not match')
                return
            }
        }

        setSubmitting(true)
        setError('')

        try {
            if (invitationData?.user_exists) {
                // Existing user - use authenticated endpoint
                await api.post('/poc-invitations/accept-existing', { token })
                toast.success('Invitation accepted successfully!')

                // Redirect to POC view
                setTimeout(() => {
                    navigate(`/pocs/${invitationData.poc_id}`)
                }, 1500)
            } else {
                // New user - use public endpoint with password
                await api.post('/poc-invitations/accept', {
                    token,
                    password
                })
                toast.success('Account created successfully!')

                // Redirect to login
                setTimeout(() => {
                    navigate('/login', {
                        state: {
                            message: 'Your account has been created. Please log in to continue.',
                            email: invitationData?.email
                        }
                    })
                }, 1500)
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to accept invitation')
        } finally {
            setSubmitting(false)
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
                <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                        <p className="mt-4 text-gray-600">Validating invitation...</p>
                    </div>
                </div>
            </div>
        )
    }

    if (error && !invitationData) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
                <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
                    <div className="text-center">
                        <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                            <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </div>
                        <h2 className="mt-4 text-2xl font-bold text-gray-900">Invalid Invitation</h2>
                        <p className="mt-2 text-gray-600">{error}</p>
                        <button
                            onClick={() => navigate('/login')}
                            className="mt-6 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                        >
                            Go to Login
                        </button>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
                <div className="text-center mb-6">
                    <h2 className="text-3xl font-bold text-gray-900">POC Invitation</h2>
                    <p className="mt-2 text-gray-600">You've been invited to join a POC</p>
                </div>

                {invitationData && (
                    <div className="mb-6">
                        <div className="bg-indigo-50 rounded-lg p-4 mb-4">
                            <h3 className="font-semibold text-indigo-900 mb-2">{invitationData.poc_title}</h3>
                            <p className="text-sm text-indigo-700">
                                Invited by: <strong>{invitationData.invited_by_name}</strong>
                            </p>
                            <p className="text-sm text-indigo-700 mt-1">
                                Role: <strong>{invitationData.is_customer ? 'Customer' : 'Vendor/Sales Engineer'}</strong>
                            </p>
                        </div>

                        {invitationData.personal_message && (
                            <div className="bg-gray-50 rounded-lg p-4 mb-4">
                                <p className="text-sm text-gray-700 italic">"{invitationData.personal_message}"</p>
                            </div>
                        )}

                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                            <div className="flex items-start">
                                <div className="flex-shrink-0">
                                    <svg className="h-5 w-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                    </svg>
                                </div>
                                <div className="ml-3">
                                    <p className="text-sm text-blue-700">
                                        {invitationData.user_exists ? (
                                            user ? (
                                                <>You are logged in as <strong>{user.email}</strong>. Click "Accept Invitation" to be added to this POC.</>
                                            ) : (
                                                <>Your account (<strong>{invitationData.email}</strong>) already exists. Please log in to accept this invitation.</>
                                            )
                                        ) : (
                                            <>A new account will be created for <strong>{invitationData.email}</strong>. Please set a password below.</>
                                        )}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <form onSubmit={handleAccept} className="space-y-4">
                            {!invitationData.user_exists && (
                                <>
                                    <div>
                                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                                            Password
                                        </label>
                                        <input
                                            id="password"
                                            type="password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                            placeholder="Enter your password"
                                            required
                                            minLength={8}
                                        />
                                        <p className="mt-1 text-xs text-gray-500">Must be at least 8 characters</p>
                                    </div>

                                    <div>
                                        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                                            Confirm Password
                                        </label>
                                        <input
                                            id="confirmPassword"
                                            type="password"
                                            value={confirmPassword}
                                            onChange={(e) => setConfirmPassword(e.target.value)}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                            placeholder="Confirm your password"
                                            required
                                        />
                                    </div>
                                </>
                            )}

                            {error && (
                                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                                    <p className="text-sm text-red-800">{error}</p>
                                </div>
                            )}

                            <button
                                type="submit"
                                disabled={submitting}
                                className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
                            >
                                {submitting ? (
                                    <>
                                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Accepting...
                                    </>
                                ) : (
                                    'Accept Invitation'
                                )}
                            </button>
                        </form>
                    </div>
                )}
            </div>
        </div>
    )
}
