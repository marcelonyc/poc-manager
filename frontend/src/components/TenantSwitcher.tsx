import React, { useState, useEffect } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { ChevronDownIcon, CheckIcon } from '@heroicons/react/24/outline';

interface TenantOption {
    tenant_id: number | null;
    tenant_name: string | null;
    tenant_slug: string | null;
    role: string;
    is_default: boolean;
}

interface TenantSwitcherProps {
    currentTenantId: number | null;
    currentTenantName: string | null;
    currentRole: string | null;
    tenants: TenantOption[];
    onTenantSwitch: (tenantId: number | null) => void;
}

export default function TenantSwitcher({
    currentTenantId,
    currentTenantName,
    currentRole,
    tenants,
    onTenantSwitch
}: TenantSwitcherProps) {
    const [isLoading, setIsLoading] = useState(false);

    const handleSwitchTenant = async (tenantId: number | null) => {
        if (tenantId === currentTenantId) return;

        setIsLoading(true);
        try {
            await onTenantSwitch(tenantId);
        } catch (error) {
            console.error('Failed to switch tenant:', error);
        } finally {
            setIsLoading(false);
        }
    };

    if (!tenants || tenants.length === 0) {
        return null;
    }

    // If user has only one tenant, show static display
    if (tenants.length === 1) {
        return (
            <div className="flex items-center space-x-2 px-3 py-2 rounded-md bg-gray-100">
                <div className="flex flex-col">
                    <span className="text-sm font-medium text-gray-900">
                        {currentTenantName || 'Platform Admin'}
                    </span>
                    <span className="text-xs text-gray-500">
                        {currentRole || 'No Role'}
                    </span>
                </div>
            </div>
        );
    }

    return (
        <Menu as="div" className="relative inline-block text-left">
            <div>
                <Menu.Button
                    disabled={isLoading}
                    className="inline-flex w-full justify-between items-center gap-x-2 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <div className="flex flex-col items-start min-w-0">
                        <span className="text-sm font-medium text-gray-900 truncate max-w-[200px]">
                            {currentTenantName || 'Platform Admin'}
                        </span>
                        <span className="text-xs text-gray-500">
                            {currentRole || 'No Role'}
                        </span>
                    </div>
                    <ChevronDownIcon className="h-5 w-5 text-gray-400 flex-shrink-0" aria-hidden="true" />
                </Menu.Button>
            </div>

            <Transition
                as={React.Fragment}
                enter="transition ease-out duration-100"
                enterFrom="transform opacity-0 scale-95"
                enterTo="transform opacity-100 scale-100"
                leave="transition ease-in duration-75"
                leaveFrom="transform opacity-100 scale-100"
                leaveTo="transform opacity-0 scale-95"
            >
                <Menu.Items className="absolute right-0 z-10 mt-2 w-72 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                    <div className="py-1">
                        <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                            Switch Tenant
                        </div>
                        {tenants.map((tenant) => (
                            <Menu.Item key={tenant.tenant_id || 'platform'}>
                                {({ active }) => (
                                    <button
                                        onClick={() => handleSwitchTenant(tenant.tenant_id)}
                                        className={`
                      ${active ? 'bg-gray-100 text-gray-900' : 'text-gray-700'}
                      ${tenant.tenant_id === currentTenantId ? 'bg-indigo-50' : ''}
                      group flex w-full items-center justify-between px-4 py-2 text-sm
                    `}
                                    >
                                        <div className="flex flex-col items-start min-w-0 flex-1">
                                            <span className="font-medium truncate max-w-[200px]">
                                                {tenant.tenant_name || 'Platform Admin'}
                                            </span>
                                            <span className="text-xs text-gray-500">
                                                {tenant.role}
                                                {tenant.is_default && (
                                                    <span className="ml-1 text-indigo-600">(default)</span>
                                                )}
                                            </span>
                                        </div>
                                        {tenant.tenant_id === currentTenantId && (
                                            <CheckIcon className="h-5 w-5 text-indigo-600 flex-shrink-0" aria-hidden="true" />
                                        )}
                                    </button>
                                )}
                            </Menu.Item>
                        ))}
                    </div>
                </Menu.Items>
            </Transition>
        </Menu>
    );
}
