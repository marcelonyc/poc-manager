import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../lib/api';

const SetDemoPassword: React.FC = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);
    const [demoInfo, setDemoInfo] = useState<any>(null);
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    useEffect(() => {
        const validateToken = async () => {
            if (!token) {
                setError('Invalid setup link');
                setLoading(false);
                return;
            }

            try {
                const response = await api.get(`/demo/validate-token/${token}`);

                if (response.data.is_completed) {
                    setError('This demo account has already been set up');
                } else if (!response.data.is_verified) {
                    setError('Please verify your email first');
                } else {
                    setDemoInfo(response.data);
                }
                setLoading(false);
            } catch (err: any) {
                setError(err.response?.data?.detail || 'Invalid or expired setup link');
                setLoading(false);
            }
        };

        validateToken();
    }, [token]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (password.length < 8) {
            setError('Password must be at least 8 characters long');
            return;
        }

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        setSubmitting(true);

        try {
            const response = await api.post('/demo/set-password', {
                token,
                password,
            });

            // Show success message
            alert('Demo account created successfully! Redirecting to login...');

            // Redirect to login after a short delay
            setTimeout(() => {
                navigate('login');
            }, 1000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to set password');
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100 flex items-center justify-center p-4">
                <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Validating setup link...</p>
                </div>
            </div>
        );
    }

    if (error && !demoInfo) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100 flex items-center justify-center p-4">
                <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
                    <div className="text-center">
                        <svg
                            className="mx-auto h-16 w-16 text-red-500 mb-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                        </svg>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">
                            Invalid Setup Link
                        </h2>
                        <p className="text-gray-600 mb-6">{error}</p>
                        <button
                            onClick={() => navigate('demo/request')}
                            className="text-indigo-600 hover:text-indigo-500 font-medium"
                        >
                            Request a New Demo Account
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
                <div className="text-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                        Set Your Password
                    </h2>
                    <p className="text-gray-600">
                        Complete your demo account setup for <strong>{demoInfo?.company_name}</strong>
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-sm text-gray-700">
                            <strong>Name:</strong> {demoInfo?.name}
                        </p>
                        <p className="text-sm text-gray-700 mt-1">
                            <strong>Email:</strong> {demoInfo?.email}
                        </p>
                    </div>

                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                            Password *
                        </label>
                        <input
                            type="password"
                            id="password"
                            required
                            minLength={8}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            placeholder="Minimum 8 characters"
                        />
                    </div>

                    <div>
                        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                            Confirm Password *
                        </label>
                        <input
                            type="password"
                            id="confirmPassword"
                            required
                            minLength={8}
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            placeholder="Re-enter your password"
                        />
                    </div>

                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={submitting}
                        className="w-full bg-indigo-600 text-white py-3 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                    >
                        {submitting ? 'Creating Account...' : 'Complete Setup'}
                    </button>
                </form>

                <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-blue-800">
                        <strong>Note:</strong> Your demo account will be pre-populated with sample data including users, POCs, tasks, and success criteria to help you explore the platform.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default SetDemoPassword;
