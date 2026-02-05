import { BookOpenIcon, QuestionMarkCircleIcon } from '@heroicons/react/24/outline'

export default function HelpBubble() {
    return (
        <div style={{
            position: 'fixed',
            bottom: '2rem',
            left: '2rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.75rem',
            zIndex: 1000
        }}>
            <a
                href="/docs"
                target="_blank"
                style={{
                    position: 'relative',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '3.5rem',
                    height: '3.5rem',
                    background: 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)',
                    borderRadius: '50%',
                    color: 'white',
                    boxShadow: '0 4px 12px rgba(59, 130, 246, 0.4)',
                    transition: 'all 0.3s ease',
                    cursor: 'pointer'
                }}
                className="help-bubble-item"
                aria-label="Documentation"
                onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'scale(1.1)'
                    e.currentTarget.style.boxShadow = '0 6px 20px rgba(59, 130, 246, 0.6)'
                    const tooltip = e.currentTarget.querySelector('.help-bubble-tooltip') as HTMLElement
                    if (tooltip) {
                        tooltip.style.opacity = '1'
                        tooltip.style.visibility = 'visible'
                    }
                }}
                onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'scale(1)'
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.4)'
                    const tooltip = e.currentTarget.querySelector('.help-bubble-tooltip') as HTMLElement
                    if (tooltip) {
                        tooltip.style.opacity = '0'
                        tooltip.style.visibility = 'hidden'
                    }
                }}
            >
                <BookOpenIcon style={{ width: '1.75rem', height: '1.75rem' }} />
                <span
                    className="help-bubble-tooltip"
                    style={{
                        position: 'absolute',
                        left: '4.5rem',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        backgroundColor: '#1f2937',
                        color: 'white',
                        padding: '0.5rem 1rem',
                        borderRadius: '0.5rem',
                        fontSize: '0.875rem',
                        whiteSpace: 'nowrap',
                        opacity: 0,
                        visibility: 'hidden',
                        transition: 'all 0.3s ease',
                        pointerEvents: 'none',
                        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
                    }}
                >
                    Documentation
                </span>
            </a>
            <a
                href="https://github.com/marcelonyc/poc-manager/issues/new?template=saas-question.md"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                    position: 'relative',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '3.5rem',
                    height: '3.5rem',
                    background: 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)',
                    borderRadius: '50%',
                    color: 'white',
                    boxShadow: '0 4px 12px rgba(59, 130, 246, 0.4)',
                    transition: 'all 0.3s ease',
                    cursor: 'pointer'
                }}
                className="help-bubble-item"
                aria-label="Support"
                onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'scale(1.1)'
                    e.currentTarget.style.boxShadow = '0 6px 20px rgba(59, 130, 246, 0.6)'
                    const tooltip = e.currentTarget.querySelector('.help-bubble-tooltip') as HTMLElement
                    if (tooltip) {
                        tooltip.style.opacity = '1'
                        tooltip.style.visibility = 'visible'
                    }
                }}
                onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'scale(1)'
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.4)'
                    const tooltip = e.currentTarget.querySelector('.help-bubble-tooltip') as HTMLElement
                    if (tooltip) {
                        tooltip.style.opacity = '0'
                        tooltip.style.visibility = 'hidden'
                    }
                }}
            >
                <QuestionMarkCircleIcon style={{ width: '1.75rem', height: '1.75rem' }} />
                <span
                    className="help-bubble-tooltip"
                    style={{
                        position: 'absolute',
                        left: '4.5rem',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        backgroundColor: '#1f2937',
                        color: 'white',
                        padding: '0.5rem 1rem',
                        borderRadius: '0.5rem',
                        fontSize: '0.875rem',
                        whiteSpace: 'nowrap',
                        opacity: 0,
                        visibility: 'hidden',
                        transition: 'all 0.3s ease',
                        pointerEvents: 'none',
                        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
                    }}
                >
                    Support
                </span>
            </a>
        </div>
    )
}

