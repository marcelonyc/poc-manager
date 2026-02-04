import { BookOpenIcon, QuestionMarkCircleIcon } from '@heroicons/react/24/outline'

export default function HelpBubble() {
    return (
        <div className="help-bubble">
            <a
                href="/docs"
                className="help-bubble-item group"
                aria-label="Documentation"
            >
                <BookOpenIcon className="help-icon" />
                <span className="help-bubble-tooltip">Documentation</span>
            </a>
            <a
                href="https://github.com/marcelonyc/poc-manager/issues/new"
                target="_blank"
                rel="noopener noreferrer"
                className="help-bubble-item group"
                aria-label="Support"
            >
                <QuestionMarkCircleIcon className="help-icon" />
                <span className="help-bubble-tooltip">Support</span>
            </a>
        </div>
    )
}
