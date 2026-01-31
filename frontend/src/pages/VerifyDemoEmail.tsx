import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../lib/api';

const VerifyDemoEmail: React.FC = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [verifying, setVerifying] = useState(false);
    const [verified, setVerified] = useState(false);
    const [demoInfo, setDemoInfo] = useState<any>(null);

    useEffect(() => {
        const validateToken = async () => {
            if (!token) {
                setError('Invalid verification link');
                setLoading(false);
                return;
            }

            try {
                const response = await api.get(`/demo/validate-token/${token}`);
                setDemoInfo(response.data);

                if (response.data.is_completed) {
                    setError('This demo account has already been set up');
                } else if (response.data.is_verified) {
                    // Already verified, can proceed to set password
                    navigate(`/demo/set-password?token=${token}`);
                } else {
                    // Need to verify
                    setLoading(false);
                }
            } catch (err: any) {
                setError(err.response?.data?.detail || 'Invalid or expired verification link');
                setLoading(false);
            }
        };

        validateToken();
    }, [token, navigate]);

    const handleVerify = async () => {
        setVerifying(true);
        setError(null);

        try {
            await api.post('/demo/verify-email', { token });
            setVerified(true);
            // Redirect to password setup after 2 seconds
            setTimeout(() => {
                navigate(`/demo/set-password?token=${token}`);
            }, 2000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Verification failed');
            setVerifying(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100 flex items-center justify-center p-4">
                <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Validating verification link...</p>
                </div>
            </div>
        );
    }

    if (verified) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100 flex items-center justify-center p-4">
                <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
                    <div className="text-center">
                        <svg
                            className="mx-auto h-16 w-16 text-green-500 mb-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                        </svg>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">
                            Email Verified!
                        </h2>
                        <p className="text-gray-600 mb-4">
                            Redirecting you to set up your password...
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
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
                            Verification Failed
                        </h2>
                        <p className="text-gray-600 mb-6">{error}</p>
                        <button
                            onClick={() => navigate('/demo/request')}
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
                        Verify Your Email
                    </h2>
                    <p className="text-gray-600">
                        Welcome, <strong>{demoInfo?.name}</strong>! Please verify your email to continue.
                    </p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                    <p className="text-sm text-gray-700">
                        <strong>Email:</strong> {demoInfo?.email}
                    </p>
                    <p className="text-sm text-gray-700 mt-1">
                        <strong>Company:</strong> {demoInfo?.company_name}
                    </p>
                </div>

                <button
                    onClick={handleVerify}
                    disabled={verifying}
                    className="w-full bg-indigo-600 text-white py-3 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                    {verifying ? 'Verifying...' : 'Verify Email Address'}
                </button>
            </div>
        </div>
    );
};

export default VerifyDemoEmail;
