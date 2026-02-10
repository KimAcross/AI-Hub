import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import { Bot } from 'lucide-react'
import { CodeBlock } from './code-block'

interface StreamingMessageProps {
  content: string
}

export function StreamingMessage({ content }: StreamingMessageProps) {
  return (
    <div className="group flex gap-3 py-4 px-4 bg-muted/30">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted">
        <Bot className="h-4 w-4" />
      </div>

      <div className="flex-1 min-w-0 space-y-2">
        <div className="flex items-center gap-2">
          <span className="font-medium text-sm">Assistant</span>
          <span className="text-xs text-muted-foreground">typing...</span>
        </div>

        <div className="prose prose-sm dark:prose-invert max-w-none">
          {content ? (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
              components={{
                code({ className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '')
                  const isInline = !match && !className

                  if (isInline) {
                    return (
                      <code
                        className="px-1.5 py-0.5 rounded bg-muted font-mono text-sm"
                        {...props}
                      >
                        {children}
                      </code>
                    )
                  }

                  return (
                    <CodeBlock language={match?.[1]}>
                      {String(children).replace(/\n$/, '')}
                    </CodeBlock>
                  )
                },
                pre({ children }) {
                  return <>{children}</>
                },
              }}
            >
              {content}
            </ReactMarkdown>
          ) : (
            <span className="text-muted-foreground">Thinking...</span>
          )}
          <span className="inline-block w-2 h-4 ml-1 bg-foreground animate-pulse" />
        </div>
      </div>
    </div>
  )
}
