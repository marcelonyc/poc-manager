import { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'

let mermaidInitialized = false

function initMermaid() {
    if (!mermaidInitialized) {
        mermaid.initialize({
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'loose',
            fontFamily: 'inherit',
        })
        mermaidInitialized = true
    }
}

let idCounter = 0

export default function MermaidDiagram({ code }: { code: string }) {
    const containerRef = useRef<HTMLDivElement>(null)
    const [svg, setSvg] = useState<string | null>(null)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        initMermaid()

        const id = `mermaid-${Date.now()}-${idCounter++}`

        let cancelled = false
        mermaid
            .render(id, code.trim())
            .then(({ svg: renderedSvg }) => {
                if (!cancelled) {
                    setSvg(renderedSvg)
                    setError(null)
                }
            })
            .catch((err) => {
                if (!cancelled) {
                    setError(err?.message || 'Failed to render diagram')
                    setSvg(null)
                }
            })

        return () => {
            cancelled = true
        }
    }, [code])

    if (error) {
        return (
            <div className="my-2 rounded-lg border border-red-200 bg-red-50 p-3">
                <p className="text-xs font-medium text-red-600 mb-1">Diagram render error</p>
                <pre className="text-xs text-red-500 whitespace-pre-wrap">{code.trim()}</pre>
            </div>
        )
    }

    if (!svg) {
        return (
            <div className="my-2 flex items-center justify-center rounded-lg bg-gray-50 p-4">
                <div className="animate-pulse text-xs text-gray-400">Rendering diagram...</div>
            </div>
        )
    }

    return (
        <div
            ref={containerRef}
            className="my-2 overflow-x-auto rounded-lg bg-white p-2 border border-gray-200"
            dangerouslySetInnerHTML={{ __html: svg }}
        />
    )
}
