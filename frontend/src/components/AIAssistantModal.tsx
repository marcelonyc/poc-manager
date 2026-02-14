import { useState, useEffect, useRef, useCallback } from 'react'
import { api } from '../lib/api'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'
import MarkdownMessage from './MarkdownMessage'
import CopyButton from './CopyButton'

interface ChatMessage {
    role: 'user' | 'assistant'
    content: string
    timestamp: string
}

interface AIAssistantStatus {
    enabled: boolean
    has_api_key: boolean
    message: string
}

const SESSION_TIMEOUT_MS = 10 * 60 * 1000 // 10 minutes

export default function AIAssistantModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
    const { user } = useAuthStore()
    const [status, setStatus] = useState<AIAssistantStatus | null>(null)
    const [loading, setLoading] = useState(true)
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [input, setInput] = useState('')
    const [sending, setSending] = useState(false)
    const [sessionId, setSessionId] = useState<string | null>(null)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
    const inputRef = useRef<HTMLTextAreaElement>(null)

    // Auto-scroll to bottom on new messages
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    // Focus input when modal opens
    useEffect(() => {
        if (isOpen) {
            setTimeout(() => inputRef.current?.focus(), 100)
        }
    }, [isOpen])

    // Check AI assistant status when modal opens
    useEffect(() => {
        if (isOpen) {
            checkStatus()
        }
        return () => {
            if (timeoutRef.current) clearTimeout(timeoutRef.current)
        }
    }, [isOpen])

    // Inactivity timeout
    const resetTimeout = useCallback(() => {
        if (timeoutRef.current) clearTimeout(timeoutRef.current)
        timeoutRef.current = setTimeout(() => {
            toast('Chat session timed out due to inactivity', { icon: '⏰' })
            handleClose()
        }, SESSION_TIMEOUT_MS)
    }, [])

    useEffect(() => {
        if (isOpen && status?.enabled && status?.has_api_key) {
            resetTimeout()
        }
        return () => {
            if (timeoutRef.current) clearTimeout(timeoutRef.current)
        }
    }, [isOpen, status, resetTimeout])

    const checkStatus = async () => {
        setLoading(true)
        try {
            const response = await api.get('/ai-assistant/status')
            setStatus(response.data)
        } catch (err: any) {
            if (err.response?.status === 403) {
                setStatus({
                    enabled: false,
                    has_api_key: false,
                    message: 'AI Assistant is not available for your role.',
                })
            } else {
                setStatus({
                    enabled: false,
                    has_api_key: false,
                    message: 'Failed to check AI Assistant status.',
                })
            }
        } finally {
            setLoading(false)
        }
    }

    const handleNewChat = async () => {
        try {
            const params = sessionId ? `?session_id=${sessionId}` : ''
            const response = await api.post(`/ai-assistant/chat/new${params}`)
            setSessionId(response.data.session_id)
        } catch {
            // Even if the backend call fails, reset locally
        }
        setMessages([])
        setInput('')
        resetTimeout()
        inputRef.current?.focus()
    }

    const handleClose = () => {
        if (sessionId) {
            api.delete(`/ai-assistant/chat/${sessionId}`).catch(() => { })
        }
        setMessages([])
        setSessionId(null)
        setInput('')
        if (timeoutRef.current) clearTimeout(timeoutRef.current)
        onClose()
    }

    const handleSend = async () => {
        if (!input.trim() || sending) return
        resetTimeout()

        const userMessage = input.trim()
        setInput('')
        setSending(true)

        // Optimistically add user message
        setMessages((prev) => [
            ...prev,
            { role: 'user', content: userMessage, timestamp: new Date().toISOString() },
        ])

        try {
            const response = await api.post('/ai-assistant/chat', {
                message: userMessage,
                session_id: sessionId,
            })

            setSessionId(response.data.session_id)
            // Replace messages with server state
            setMessages(response.data.messages)
        } catch (err: any) {
            const detail = err.response?.data?.detail || 'Failed to send message'
            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: `Error: ${detail}`, timestamp: new Date().toISOString() },
            ])
        } finally {
            setSending(false)
            inputRef.current?.focus()
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-y-0 right-0 w-full sm:w-[420px] bg-white shadow-2xl z-50 flex flex-col border-l border-gray-200">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
                <div className="flex items-center gap-2">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                    </svg>
                    <h2 className="text-lg font-semibold">AI Assistant</h2>
                    <span className="px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide bg-yellow-400 text-yellow-900 rounded-full leading-none">Beta</span>
                </div>
                <div className="flex items-center gap-1">
                    <button
                        onClick={handleNewChat}
                        className="p-1 hover:bg-white/20 rounded transition-colors"
                        title="New Chat"
                        disabled={sending}
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                    </button>
                    <button
                        onClick={handleClose}
                        className="p-1 hover:bg-white/20 rounded transition-colors"
                        title="Close"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
            </div>

            {/* Content */}
            {loading ? (
                <div className="flex-1 flex items-center justify-center">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mx-auto" />
                        <p className="mt-3 text-gray-500 text-sm">Checking AI Assistant status...</p>
                    </div>
                </div>
            ) : !status?.enabled || !status?.has_api_key ? (
                <div className="flex-1 flex items-center justify-center p-6">
                    <div className="text-center max-w-sm">
                        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                            </svg>
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Assistant Not Available</h3>
                        <p className="text-sm text-gray-600 mb-4">{status?.message}</p>
                        {user?.role === 'tenant_admin' && !status?.enabled && (
                            <a
                                href="/settings"
                                className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium transition-colors"
                                onClick={handleClose}
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                                Go to Settings
                            </a>
                        )}
                    </div>
                </div>
            ) : (
                <>
                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
                        {messages.length === 0 && (
                            <div className="text-center text-gray-400 mt-12">
                                <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                                </svg>
                                <p className="text-sm font-medium">How can I help you today?</p>
                                <p className="text-xs mt-1">Ask me anything about your POCs, tasks, or data.</p>
                            </div>
                        )}

                        {messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`group relative max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${msg.role === 'user'
                                        ? 'bg-indigo-600 text-white rounded-br-md'
                                        : 'bg-gray-100 text-gray-800 rounded-bl-md'
                                        }`}
                                >
                                    {msg.role === 'assistant' ? (
                                        <>
                                            <MarkdownMessage content={msg.content} />
                                            <CopyButton text={msg.content} />
                                        </>
                                    ) : (
                                        <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                                    )}
                                </div>
                            </div>
                        ))}

                        {sending && (
                            <div className="flex justify-start">
                                <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
                                    <div className="flex space-x-1.5">
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                    </div>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="border-t border-gray-200 px-4 py-3">
                        <div className="flex items-end gap-2">
                            <textarea
                                ref={inputRef}
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Type your message..."
                                rows={1}
                                className="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none max-h-32"
                                style={{ minHeight: '42px' }}
                                disabled={sending}
                            />
                            <button
                                onClick={handleSend}
                                disabled={!input.trim() || sending}
                                className="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                </svg>
                            </button>
                        </div>
                        <p className="text-xs text-gray-400 mt-1.5 text-center">
                            Session times out after 10 min of inactivity
                        </p>
                    </div>
                </>
            )}
        </div>
    )
}
