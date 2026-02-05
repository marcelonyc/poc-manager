import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Login from './pages/Login'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import DemoRequest from './pages/DemoRequest'
import VerifyDemoEmail from './pages/VerifyDemoEmail'
import SetDemoPassword from './pages/SetDemoPassword'
import DemoConversionApproval from './pages/DemoConversionApproval'
import Dashboard from './pages/Dashboard'
import POCList from './pages/POCList'
import POCDetail from './pages/POCDetail'
import TaskTemplates from './pages/TaskTemplates'
import TenantSettings from './pages/TenantSettings'
import Tenants from './pages/Tenants'
import Users from './pages/Users'
import Products from './pages/Products'
import DemoRequests from './pages/DemoRequests'
import PlatformAdminInvitations from './pages/PlatformAdminInvitations'
import AcceptInvitation from './pages/AcceptInvitation'
import AcceptPOCInvitation from './pages/AcceptPOCInvitation'
import Layout from './components/Layout'
import HelpBubble from './components/HelpBubble'

function App() {
    const { isAuthenticated, user } = useAuthStore()
    const isCustomer = user?.role === 'customer'

    return (
        <>
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />
                <Route path="/reset-password" element={<ResetPassword />} />
                <Route path="/demo/request" element={<DemoRequest />} />
                <Route path="/verify-demo-email" element={<VerifyDemoEmail />} />
                <Route path="/demo/set-password" element={<SetDemoPassword />} />
                <Route path="/accept-invitation" element={<AcceptInvitation />} />
                <Route path="/poc-invitation" element={<AcceptPOCInvitation />} />

                {isAuthenticated ? (
                    <Route path="/" element={<Layout />}>
                        <Route index element={isCustomer ? <Navigate to="/pocs" replace /> : <Dashboard />} />
                        <Route path="pocs" element={<POCList />} />
                        <Route path="pocs/:id" element={<POCDetail />} />
                        <Route path="templates" element={<TaskTemplates />} />
                        <Route path="tenants" element={<Tenants />} />
                        <Route path="users" element={<Users />} />
                        <Route path="products" element={<Products />} />
                        <Route path="settings" element={<TenantSettings />} />
                        <Route path="invitations" element={<PlatformAdminInvitations />} />
                        <Route path="demo-requests" element={<DemoRequests />} />
                        <Route path="admin/demo-conversions/:requestId" element={<DemoConversionApproval />} />
                    </Route>
                ) : (
                    <Route path="*" element={<Navigate to="/login" replace />} />
                )}
            </Routes>
            <HelpBubble />
        </>
    )
}

export default App
