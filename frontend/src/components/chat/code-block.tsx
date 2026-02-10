import * as React from 'react'
import { Check, Copy } from 'lucide-react'
import { cn } from '@/lib/utils'

interface CodeBlockProps {
  children: string
  language?: string
  className?: string
}

export const CodeBlock = React.memo(function CodeBlock({ children, language, className }: CodeBlockProps) {
  const [copied, setCopied] = React.useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(children)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={cn("relative group my-3", className)}>
      {language && (
        <div className="flex items-center justify-between px-4 py-2 bg-muted/80 border-b border-border rounded-t-lg">
          <span className="text-xs text-muted-foreground font-mono">{language}</span>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5" />
                Copied
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" />
                Copy
              </>
            )}
          </button>
        </div>
      )}
      <pre className={cn(
        "overflow-x-auto p-4 bg-muted/50 text-sm",
        language ? "rounded-b-lg" : "rounded-lg"
      )}>
        <code className={cn("font-mono", language && `language-${language}`)}>
          {children}
        </code>
      </pre>
      {!language && (
        <button
          onClick={handleCopy}
          className="absolute top-2 right-2 p-1.5 rounded bg-muted hover:bg-muted/80 opacity-0 group-hover:opacity-100 transition-opacity"
          title="Copy code"
        >
          {copied ? (
            <Check className="h-4 w-4 text-green-500" />
          ) : (
            <Copy className="h-4 w-4 text-muted-foreground" />
          )}
        </button>
      )}
    </div>
  )
})
