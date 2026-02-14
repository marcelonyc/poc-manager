import { Children, isValidElement, type ReactNode } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github-dark.css'
import type { Components } from 'react-markdown'
import MermaidDiagram from './MermaidDiagram'

const MERMAID_LANGUAGES = ['mermaid', 'mermaid-js']

/** Recursively extract plain text from React children (handles rehype-highlight spans). */
function extractText(node: ReactNode): string {
    if (typeof node === 'string') return node
    if (typeof node === 'number') return String(node)
    if (!node) return ''
    if (Array.isArray(node)) return node.map(extractText).join('')
    if (isValidElement(node)) {
        return extractText(node.props.children)
    }
    return ''
}

/** Check whether a className string contains a mermaid language tag. */
function isMermaidClass(cls: string | undefined): boolean {
    if (!cls) return false
    return MERMAID_LANGUAGES.some((lang) => cls.includes(`language-${lang}`))
}

interface MarkdownMessageProps {
    content: string
    className?: string
}

const markdownComponents: Components = {
    // Headings
    h1: ({ children }) => (
        <h1 className="text-lg font-bold mt-3 mb-1.5 first:mt-0">{children}</h1>
    ),
    h2: ({ children }) => (
        <h2 className="text-base font-bold mt-2.5 mb-1 first:mt-0">{children}</h2>
    ),
    h3: ({ children }) => (
        <h3 className="text-sm font-bold mt-2 mb-1 first:mt-0">{children}</h3>
    ),

    // Paragraphs
    p: ({ children }) => (
        <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>
    ),

    // Lists
    ul: ({ children }) => (
        <ul className="list-disc list-inside mb-2 last:mb-0 space-y-0.5">{children}</ul>
    ),
    ol: ({ children }) => (
        <ol className="list-decimal list-inside mb-2 last:mb-0 space-y-0.5">{children}</ol>
    ),
    li: ({ children }) => (
        <li className="leading-relaxed">{children}</li>
    ),

    // Code blocks — intercept mermaid diagrams
    pre: ({ children }) => {
        const child = Children.toArray(children)[0]
        if (isValidElement(child) && child.props) {
            const cls: string | undefined = child.props.className
            if (isMermaidClass(cls)) {
                const code = extractText(child.props.children).replace(/\n$/, '')
                return <MermaidDiagram code={code} />
            }
        }
        return (
            <pre className="bg-gray-800 text-gray-100 rounded-lg p-3 my-2 overflow-x-auto text-xs leading-relaxed">
                {children}
            </pre>
        )
    },
    code: ({ className, children, ...props }) => {
        const isInline = !className
        if (isInline) {
            return (
                <code className="bg-gray-200 text-indigo-700 rounded px-1 py-0.5 text-xs font-mono" {...props}>
                    {children}
                </code>
            )
        }
        return (
            <code className={`${className || ''} text-xs font-mono`} {...props}>
                {children}
            </code>
        )
    },

    // Blockquotes
    blockquote: ({ children }) => (
        <blockquote className="border-l-3 border-indigo-400 pl-3 my-2 text-gray-600 italic">
            {children}
        </blockquote>
    ),

    // Tables
    table: ({ children }) => (
        <div className="overflow-x-auto my-2">
            <table className="min-w-full text-xs border-collapse">{children}</table>
        </div>
    ),
    thead: ({ children }) => (
        <thead className="bg-gray-200">{children}</thead>
    ),
    th: ({ children }) => (
        <th className="border border-gray-300 px-2 py-1 text-left font-semibold">{children}</th>
    ),
    td: ({ children }) => (
        <td className="border border-gray-300 px-2 py-1">{children}</td>
    ),

    // Links
    a: ({ href, children }) => (
        <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-600 underline hover:text-indigo-800"
        >
            {children}
        </a>
    ),

    // Horizontal rule
    hr: () => <hr className="my-3 border-gray-300" />,

    // Strong / emphasis
    strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
    em: ({ children }) => <em className="italic">{children}</em>,
}

export default function MarkdownMessage({ content, className = '' }: MarkdownMessageProps) {
    return (
        <div className={`markdown-message prose-sm max-w-none break-words ${className}`}>
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[[rehypeHighlight, { plainText: ['mermaid', 'mermaid-js'] }]]}
                components={markdownComponents}
            >
                {content}
            </ReactMarkdown>
        </div>
    )
}
