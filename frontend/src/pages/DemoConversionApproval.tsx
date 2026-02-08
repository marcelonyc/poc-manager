import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../lib/api';

interface ConversionRequest {
    id: number;
    tenant_id: number;
    requested_by_user_id: number;
    reason: string | null;
    status: string;
    approved: boolean;
    created_at: string;
}

const DemoConversionApproval: React.FC = () => {
    const { requestId } = useParams<{ requestId: string }>();
    const navigate = useNavigate();
    const { user } = useAuthStore();

    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [request, setRequest] = useState<ConversionRequest | null>(null);
    const [rejectionReason, setRejectionReason] = useState('');
    const [showRejectForm, setShowRejectForm] = useState(false);

    useEffect(() => {
        // Check if user is platform admin
        if (user?.role !== 'platform_admin') {
            setError('Access denied. Only platform administrators can approve demo conversions.');
            setLoading(false);
            return;
        }

        fetchRequest();
    }, [requestId, user]);

    const fetchRequest = async () => {
        try {
            const response = await api.get('/demo/conversions');
            const foundRequest = response.data.find((r: ConversionRequest) => r.id === parseInt(requestId || '0'));

            if (!foundRequest) {
                setError('Conversion request not found');
            } else {
                setRequest(foundRequest);
            }
            setLoading(false);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load conversion request');
            setLoading(false);
        }
    };

    const handleApprove = async () => {
        if (!confirm('Are you sure you want to approve this demo conversion? This will remove all demo limits.')) {
            return;
        }

        setSubmitting(true);
        setError(null);

        try {
            await api.post(`/demo/conversions/${requestId}/approve`, {
                approved: true,
                rejection_reason: null
            });

            alert('Demo conversion approved successfully!');
            navigate('admin/demo-conversions');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to approve conversion');
            setSubmitting(false);
        }
    };

    const handleReject = async () => {
        if (!rejectionReason.trim()) {
            setError('Please provide a reason for rejection');
            return;
        }

        setSubmitting(true);
        setError(null);

        try {
            await api.post(`/demo/conversions/${requestId}/approve`, {
                approved: false,
                rejection_reason: rejectionReason
            });

            alert('Demo conversion rejected');
            navigate('admin/demo-conversions');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to reject conversion');
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    if (error && !request) {
        return (
            <div className="max-w-2xl mx-auto p-6">
                <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                    <h2 className="text-xl font-bold text-red-900 mb-2">Error</h2>
                    <p className="text-red-700">{error}</p>
                    <button
                        onClick={() => navigate('')}
                        className="mt-4 text-red-600 hover:text-red-700 font-medium"
                    >
                        Return to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    if (request?.status !== 'pending') {
        return (
            <div className="max-w-2xl mx-auto p-6">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                    <h2 className="text-xl font-bold text-yellow-900 mb-2">Request Already Processed</h2>
                    <p className="text-yellow-700">
                        This conversion request has already been <strong>{request?.status}</strong>.
                    </p>
                    <button
                        onClick={() => navigate('')}
                        className="mt-4 text-yellow-600 hover:text-yellow-700 font-medium"
                    >
                        Return to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-2xl mx-auto p-6">
            <div className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                    Demo Account Conversion Request
                </h2>

                <div className="space-y-4 mb-6">
                    <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-sm text-gray-600 mb-1">Request ID</p>
                        <p className="font-semibold text-gray-900">{request?.id}</p>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-sm text-gray-600 mb-1">Tenant ID</p>
                        <p className="font-semibold text-gray-900">{request?.tenant_id}</p>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-sm text-gray-600 mb-1">Requested By (User ID)</p>
                        <p className="font-semibold text-gray-900">{request?.requested_by_user_id}</p>
                    </div>

                    {request?.reason && (
                        <div className="bg-gray-50 rounded-lg p-4">
                            <p className="text-sm text-gray-600 mb-1">Reason</p>
                            <p className="text-gray-900">{request.reason}</p>
                        </div>
                    )}

                    <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-sm text-gray-600 mb-1">Requested At</p>
                        <p className="text-gray-900">{new Date(request?.created_at || '').toLocaleString()}</p>
                    </div>
                </div>

                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
                        {error}
                    </div>
                )}

                {!showRejectForm ? (
                    <div className="flex gap-4">
                        <button
                            onClick={handleApprove}
                            disabled={submitting}
                            className="flex-1 bg-green-600 text-white py-3 px-6 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                        >
                            {submitting ? 'Approving...' : 'Approve Conversion'}
                        </button>
                        <button
                            onClick={() => setShowRejectForm(true)}
                            disabled={submitting}
                            className="flex-1 bg-red-600 text-white py-3 px-6 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                        >
                            Reject
                        </button>
                    </div>
                ) : (
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Rejection Reason *
                            </label>
                            <textarea
                                value={rejectionReason}
                                onChange={(e) => setRejectionReason(e.target.value)}
                                rows={4}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                placeholder="Provide a reason for rejecting this conversion request..."
                            />
                        </div>
                        <div className="flex gap-4">
                            <button
                                onClick={handleReject}
                                disabled={submitting || !rejectionReason.trim()}
                                className="flex-1 bg-red-600 text-white py-3 px-6 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                            >
                                {submitting ? 'Rejecting...' : 'Confirm Rejection'}
                            </button>
                            <button
                                onClick={() => {
                                    setShowRejectForm(false);
                                    setRejectionReason('');
                                }}
                                disabled={submitting}
                                className="flex-1 bg-gray-300 text-gray-700 py-3 px-6 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default DemoConversionApproval;
