import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { BuildingOfficeIcon } from '@heroicons/react/24/outline';
import { api } from '../lib/api';
import { useAuthStore } from '../store/authStore';
import toast from 'react-hot-toast';

interface TenantOption {
    tenant_id: number | null;
    tenant_name: string | null;
    tenant_slug: string | null;
    role: string;
    is_default: boolean;
}

interface LocationState {
    tenants: TenantOption[];
    user: {
        id: number;
        email: string;
        full_name: string;
    };
    credentials: {
        email: string;
        password: string;
    };
}

export default function TenantSelection() {
    const navigate = useNavigate();
    const location = useLocation();
    const state = location.state as LocationState;
    const login = useAuthStore((state) => state.login);

    const [selectedTenant, setSelectedTenant] = useState<number | null>(
        state?.tenants?.find(t => t.is_default)?.tenant_id || state?.tenants?.[0]?.tenant_id || null
    );
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    if (!state || !state.tenants) {
        // Redirect to login if accessed directly
        navigate('login');
        return null;
    }

    const handleSelectTenant = async () => {
        if (!selectedTenant) {
            setError('Please select a tenant');
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const response = await api.post('/auth/select-tenant', {
                tenant_id: selectedTenant,
                email: state.credentials.email,
                password: state.credentials.password,
            });

            // Use auth store to save login state
            login(response.data.access_token, {
                id: response.data.user_id,
                email: response.data.email,
                full_name: response.data.full_name,
                role: response.data.role,
                tenant_id: response.data.tenant_id,
            });

            toast.success('Tenant selected successfully!');
            // Redirect to dashboard
            navigate('/');
        } catch (err: any) {
            console.error('Failed to select tenant:', err);
            setError(err.response?.data?.detail || 'Failed to select tenant. Please try again.');
            toast.error(err.response?.data?.detail || 'Failed to select tenant');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div>
                    <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-indigo-100">
                        <BuildingOfficeIcon className="h-8 w-8 text-indigo-600" />
                    </div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Select a Tenant
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        You have access to multiple tenants. Please select one to continue.
                    </p>
                </div>

                {error && (
                    <div className="rounded-md bg-red-50 p-4">
                        <div className="flex">
                            <div className="ml-3">
                                <h3 className="text-sm font-medium text-red-800">{error}</h3>
                            </div>
                        </div>
                    </div>
                )}

                <div className="mt-8 space-y-4">
                    {state.tenants.map((tenant) => (
                        <div
                            key={tenant.tenant_id || 'platform'}
                            onClick={() => setSelectedTenant(tenant.tenant_id)}
                            className={`
                relative rounded-lg border-2 p-4 cursor-pointer transition-all
                ${selectedTenant === tenant.tenant_id
                                    ? 'border-indigo-600 bg-indigo-50'
                                    : 'border-gray-300 hover:border-gray-400'
                                }
              `}
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex-1 min-w-0">
                                    <label className="flex items-center cursor-pointer">
                                        <input
                                            type="radio"
                                            checked={selectedTenant === tenant.tenant_id}
                                            onChange={() => setSelectedTenant(tenant.tenant_id)}
                                            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                                        />
                                        <div className="ml-3">
                                            <p className="text-sm font-medium text-gray-900">
                                                {tenant.tenant_name || 'Platform Admin'}
                                            </p>
                                            <p className="text-sm text-gray-500">
                                                Role: {tenant.role}
                                                {tenant.is_default && (
                                                    <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800">
                                                        Default
                                                    </span>
                                                )}
                                            </p>
                                        </div>
                                    </label>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <div>
                    <button
                        onClick={handleSelectTenant}
                        disabled={isLoading || !selectedTenant}
                        className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? 'Loading...' : 'Continue'}
                    </button>
                </div>

                <div className="text-center">
                    <button
                        onClick={() => navigate('login')}
                        className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
                    >
                        Back to login
                    </button>
                </div>
            </div>
        </div>
    );
}
