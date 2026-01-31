import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { useAuthStore } from '../store/authStore';

interface DemoLimits {
    is_demo: boolean;
    limits: {
        pocs: { used: number; max: number; remaining: number };
        tasks: { used: number; max: number; remaining: number };
        task_groups: { used: number; max: number; remaining: number };
        resources: { used: number; max: number; remaining: number };
    } | null;
}

const DemoLimitsBanner: React.FC = () => {
    const { isAuthenticated } = useAuthStore();
    const [limits, setLimits] = useState<DemoLimits | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (isAuthenticated) {
            fetchLimits();
        }
    }, [isAuthenticated]);

    const fetchLimits = async () => {
        try {
            const response = await api.get('/demo/limits');
            setLimits(response.data);
        } catch (err) {
            // Silently fail - not a demo account or error fetching
        } finally {
            setLoading(false);
        }
    };

    if (loading || !limits?.is_demo || !limits.limits) {
        return null;
    }

    const hasWarning = Object.values(limits.limits).some(limit => limit.remaining <= 2);

    if (!hasWarning) {
        return null;
    }

    return (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
            <div className="flex">
                <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                </div>
                <div className="ml-3">
                    <h3 className="text-sm font-medium text-yellow-800">Demo Account Limits</h3>
                    <div className="mt-2 text-sm text-yellow-700">
                        <p className="mb-2">You are approaching demo account limits:</p>
                        <ul className="list-disc list-inside space-y-1">
                            {limits.limits.pocs.remaining <= 2 && (
                                <li>POCs: {limits.limits.pocs.used}/{limits.limits.pocs.max} used ({limits.limits.pocs.remaining} remaining)</li>
                            )}
                            {limits.limits.tasks.remaining <= 5 && (
                                <li>Tasks: {limits.limits.tasks.used}/{limits.limits.tasks.max} used ({limits.limits.tasks.remaining} remaining)</li>
                            )}
                            {limits.limits.task_groups.remaining <= 5 && (
                                <li>Task Groups: {limits.limits.task_groups.used}/{limits.limits.task_groups.max} used ({limits.limits.task_groups.remaining} remaining)</li>
                            )}
                            {limits.limits.resources.remaining <= 3 && (
                                <li>Resources: {limits.limits.resources.used}/{limits.limits.resources.max} used ({limits.limits.resources.remaining} remaining)</li>
                            )}
                        </ul>
                        <p className="mt-2">
                            <a href="/settings" className="font-medium underline text-yellow-800 hover:text-yellow-900">
                                Upgrade to a full account
                            </a>
                            {' '}to remove these limits.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DemoLimitsBanner;
