import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { api } from '../lib/api'

interface InvitationInfo {
    email: string
    full_name: string
    invited_by_email: string
    expires_at: string
}

export default function AcceptInvitation() {
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()
    const token = searchParams.get('token')

    const [loading, setLoading] = useState(true)
    const [validating, setValidating] = useState(true)
    const [invitationInfo, setInvitationInfo] = useState<InvitationInfo | null>(null)
    const [error, setError] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
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
            const response = await api.get(`/invitations/validate/${token}`)
            setInvitationInfo(response.data)
            setError('')
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Invalid or expired invitation')
        } finally {
            setValidating(false)
            setLoading(false)
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        if (password.length < 8) {
            setError('Password must be at least 8 characters long')
            return
        }

        if (password !== confirmPassword) {
            setError('Passwords do not match')
            return
        }

        try {
            setSubmitting(true)
            await api.post('/invitations/accept', {
                token,
                password,
            })

            // Redirect to login with success message
            navigate('login?message=Account created successfully. Please log in.')
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to accept invitation')
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
                        <h2 className="mt-4 text-2xl font-bold text-gray-900">Invalid Invitation</h2>
                        <p className="mt-2 text-gray-600">{error}</p>
                        <button
                            onClick={() => navigate('login')}
                            className="mt-6 bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
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
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold text-gray-900">Accept Invitation</h2>
                    <p className="mt-2 text-gray-600">
                        You've been invited to join as a Platform Administrator
                    </p>
                </div>

                {invitationInfo && (
                    <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 mb-6">
                        <div className="space-y-2 text-sm">
                            <div>
                                <span className="font-medium text-gray-700">Email:</span>
                                <span className="ml-2 text-gray-900">{invitationInfo.email}</span>
                            </div>
                            <div>
                                <span className="font-medium text-gray-700">Name:</span>
                                <span className="ml-2 text-gray-900">{invitationInfo.full_name}</span>
                            </div>
                            <div>
                                <span className="font-medium text-gray-700">Invited by:</span>
                                <span className="ml-2 text-gray-900">{invitationInfo.invited_by_email}</span>
                            </div>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
                        <p className="text-red-800 text-sm">{error}</p>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                            Password
                        </label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            minLength={8}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            placeholder="Enter your password (min 8 characters)"
                        />
                    </div>

                    <div>
                        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                            Confirm Password
                        </label>
                        <input
                            type="password"
                            id="confirmPassword"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            minLength={8}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            placeholder="Confirm your password"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={submitting}
                        className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 font-medium"
                    >
                        {submitting ? 'Creating Account...' : 'Create Account'}
                    </button>
                </form>

                <div className="mt-6 text-center text-sm text-gray-600">
                    Already have an account?{' '}
                    <button
                        onClick={() => navigate('login')}
                        className="text-indigo-600 hover:text-indigo-500 font-medium"
                    >
                        Log in
                    </button>
                </div>
            </div>
        </div>
    )
}
