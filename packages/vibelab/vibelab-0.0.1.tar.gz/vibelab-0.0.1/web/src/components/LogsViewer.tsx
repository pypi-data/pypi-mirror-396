import { useState, useCallback, useMemo, useRef, useEffect } from 'react'
import { cn } from '../lib/cn'
import { Button } from './ui/Button'

type ViewMode = 'chat' | 'raw'

// Unified message types after parsing
interface UnifiedMessage {
  type: 'system' | 'user' | 'assistant' | 'tool_call' | 'tool_result' | 'thinking' | 'result' | 'text'
  raw: string
  data: any
}

// Parse a single log line into a unified message
function parseLogLine(line: string): UnifiedMessage | null {
  const trimmed = line.trim()
  if (!trimmed) return null
  
  if (!trimmed.startsWith('{')) {
    return { type: 'text', raw: line, data: { text: line } }
  }
  
  try {
    const parsed = JSON.parse(trimmed)
    return normalizeMessage(parsed, line)
  } catch {
    return { type: 'text', raw: line, data: { text: line } }
  }
}

// Normalize different log formats into unified structure
function normalizeMessage(parsed: any, raw: string): UnifiedMessage | null {
  const type = parsed.type
  
  switch (type) {
    case 'system':
      return { type: 'system', raw, data: parsed }
    
    case 'user': {
      // Check if this is a tool result (Claude Code style)
      const content = parsed.message?.content
      if (Array.isArray(content)) {
        const toolResult = content.find((c: any) => c.type === 'tool_result')
        if (toolResult) {
          return {
            type: 'tool_result',
            raw,
            data: {
              tool_use_id: toolResult.tool_use_id,
              content: toolResult.content,
              is_error: toolResult.is_error,
              // Also include parsed result if available
              parsed_result: parsed.tool_use_result
            }
          }
        }
      }
      // Regular user message
      return { type: 'user', raw, data: parsed }
    }
    
    case 'assistant': {
      // Check for tool_use in content (Claude Code style)
      const content = parsed.message?.content
      if (Array.isArray(content)) {
        const toolUse = content.find((c: any) => c.type === 'tool_use')
        if (toolUse) {
          return {
            type: 'tool_call',
            raw,
            data: {
              id: toolUse.id,
              name: toolUse.name,
              input: toolUse.input,
              status: 'started', // Claude Code doesn't have separate started/completed
              // Keep the text content too if any
              text: content.find((c: any) => c.type === 'text')?.text
            }
          }
        }
        // Check for just text content
        const textContent = content.find((c: any) => c.type === 'text')
        if (textContent) {
          return {
            type: 'assistant',
            raw,
            data: { text: textContent.text, message: parsed.message }
          }
        }
      }
      return { type: 'assistant', raw, data: parsed }
    }
    
    case 'thinking':
      return { type: 'thinking', raw, data: parsed }
    
    case 'tool_call': {
      // Composer style tool calls
      const toolCall = parsed.tool_call
      let name = 'unknown'
      let input = {}
      let result = null
      
      // Extract from nested structure (readToolCall, editToolCall, etc.)
      if (toolCall) {
        const keys = Object.keys(toolCall).filter(k => k.endsWith('ToolCall'))
        if (keys.length > 0) {
          const key = keys[0]
          name = key.replace('ToolCall', '')
          input = toolCall[key]?.args || {}
          if (toolCall[key]?.result) {
            result = toolCall[key].result.success || toolCall[key].result.error
          }
        }
      }
      
      return {
        type: 'tool_call',
        raw,
        data: {
          id: parsed.call_id,
          name,
          input,
          result,
          status: parsed.subtype, // 'started' or 'completed'
          is_error: !!toolCall?.[Object.keys(toolCall).find(k => k.endsWith('ToolCall')) || '']?.result?.error
        }
      }
    }
    
    case 'result':
      return {
        type: 'result',
        raw,
        data: {
          success: !parsed.is_error,
          duration_ms: parsed.duration_ms,
          result: parsed.result,
          cost_usd: parsed.total_cost_usd,
          usage: parsed.usage,
          modelUsage: parsed.modelUsage
        }
      }
    
    default:
      return { type: 'text', raw, data: parsed }
  }
}

// Group messages for better display
function groupMessages(messages: UnifiedMessage[]): UnifiedMessage[][] {
  const groups: UnifiedMessage[][] = []
  let currentToolGroup: UnifiedMessage[] = []
  
  for (const msg of messages) {
    // Skip empty thinking deltas
    if (msg.type === 'thinking' && msg.data?.subtype === 'delta' && !msg.data?.text) {
      continue
    }
    
    // Group tool calls with their results
    if (msg.type === 'tool_call') {
      if (msg.data.status === 'started' || !msg.data.status) {
        // Start new tool group
        if (currentToolGroup.length > 0) {
          groups.push(currentToolGroup)
        }
        currentToolGroup = [msg]
      } else if (msg.data.status === 'completed') {
        currentToolGroup.push(msg)
        groups.push(currentToolGroup)
        currentToolGroup = []
      }
      continue
    }
    
    // Tool results (Claude Code style) - attach to previous tool call
    if (msg.type === 'tool_result') {
      if (currentToolGroup.length > 0) {
        currentToolGroup.push(msg)
        groups.push(currentToolGroup)
        currentToolGroup = []
      } else {
        groups.push([msg])
      }
      continue
    }
    
    // Flush any pending tool group
    if (currentToolGroup.length > 0) {
      groups.push(currentToolGroup)
      currentToolGroup = []
    }
    
    groups.push([msg])
  }
  
  // Flush remaining
  if (currentToolGroup.length > 0) {
    groups.push(currentToolGroup)
  }
  
  return groups
}

// Icons
function UserIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
      <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4zm-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10z"/>
    </svg>
  )
}

function BotIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
      <path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5ZM3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.58 26.58 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.933.933 0 0 1-.765.935c-.845.147-2.34.346-4.235.346-1.895 0-3.39-.2-4.235-.346A.933.933 0 0 1 3 9.219V8.062Zm4.542-.827a.25.25 0 0 0-.217.068l-.92.9a24.767 24.767 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25.286 25.286 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.135Z"/>
      <path d="M8.5 1.866a1 1 0 1 0-1 0V3h-2A4.5 4.5 0 0 0 1 7.5V8a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1v1a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1v-.5A4.5 4.5 0 0 0 10.5 3h-2V1.866ZM14 7.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7.5A3.5 3.5 0 0 1 5.5 4h5A3.5 3.5 0 0 1 14 7.5Z"/>
    </svg>
  )
}

function ToolIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
      <path d="M1 0L0 1l2.2 3.081a1 1 0 0 0 .815.419h.07a1 1 0 0 1 .708.293l2.675 2.675-2.617 2.654A3.003 3.003 0 0 0 0 13a3 3 0 1 0 5.878-.851l2.654-2.617.968.968-.305.914a1 1 0 0 0 .242 1.023l3.27 3.27a.997.997 0 0 0 1.414 0l1.586-1.586a.997.997 0 0 0 0-1.414l-3.27-3.27a1 1 0 0 0-1.023-.242l-.914.305-.968-.968 5.965-5.965a2.5 2.5 0 0 0-3.536-3.536L6.354 5.58l-.968-.968.305-.914a1 1 0 0 0-.242-1.023l-3.27-3.27a.997.997 0 0 0-1.414 0L.293 1.086a.997.997 0 0 0 0 1.414z"/>
    </svg>
  )
}

function CheckIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
      <path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.75.75 0 0 1 1.06-1.06L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0z"/>
    </svg>
  )
}

function ErrorIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
      <path d="M3.72 3.72a.75.75 0 0 1 1.06 0L8 6.94l3.22-3.22a.75.75 0 1 1 1.06 1.06L9.06 8l3.22 3.22a.75.75 0 1 1-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 0 1-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 0 1 0-1.06z"/>
    </svg>
  )
}

function ThinkingIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor" className="animate-pulse">
      <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
      <path d="M5.255 5.786a.237.237 0 0 0 .241.247h.825c.138 0 .248-.113.266-.25.09-.656.54-1.134 1.342-1.134.686 0 1.314.343 1.314 1.168 0 .635-.374.927-.965 1.371-.673.489-1.206 1.06-1.168 1.987l.003.217a.25.25 0 0 0 .25.246h.811a.25.25 0 0 0 .25-.25v-.105c0-.718.273-.927 1.01-1.486.609-.463 1.244-.977 1.244-2.056 0-1.511-1.276-2.241-2.673-2.241-1.267 0-2.655.59-2.75 2.286zm1.557 5.763c0 .533.425.927 1.01.927.609 0 1.028-.394 1.028-.927 0-.552-.42-.94-1.029-.94-.584 0-1.009.388-1.009.94z"/>
    </svg>
  )
}

// Format path for display
function formatPath(path: string): string {
  if (!path) return ''
  const parts = path.split('/')
  if (parts.length <= 3) return path
  return '.../' + parts.slice(-3).join('/')
}

// Format tool name for display
function formatToolName(name: string): string {
  // Handle camelCase and snake_case
  return name
    .replace(/([A-Z])/g, ' $1')
    .replace(/_/g, ' ')
    .replace(/^\s+/, '')
    .split(' ')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(' ')
}

// System init message
function SystemInitCard({ data }: { data: any }) {
  return (
    <div className="flex items-center gap-2 py-2 px-3 bg-surface-2 rounded-lg text-xs">
      <span className="text-status-info">●</span>
      <span className="text-text-secondary">Session started</span>
      <span className="text-text-tertiary">•</span>
      <span className="font-mono text-text-tertiary">{data.model || 'unknown'}</span>
      {data.cwd && (
        <>
          <span className="text-text-tertiary">•</span>
          <span className="font-mono text-text-disabled truncate max-w-[200px]" title={data.cwd}>
            {formatPath(data.cwd)}
          </span>
        </>
      )}
      {data.claude_code_version && (
        <>
          <span className="text-text-tertiary">•</span>
          <span className="text-text-disabled">v{data.claude_code_version}</span>
        </>
      )}
    </div>
  )
}

// User message
function UserMessageCard({ data }: { data: any }) {
  const content = data.message?.content
  let text = ''
  
  if (typeof content === 'string') {
    text = content
  } else if (Array.isArray(content)) {
    const textBlock = content.find((c: any) => c.type === 'text')
    text = textBlock?.text || ''
  }
  
  if (!text) return null
  
  return (
    <div className="flex gap-3 py-3">
      <div className="shrink-0 w-6 h-6 rounded-full bg-surface-3 flex items-center justify-center text-text-secondary">
        <UserIcon />
      </div>
      <div className="flex-1 min-w-0 pt-0.5">
        <div className="text-xs font-medium text-text-tertiary mb-1">You</div>
        <div className="text-sm text-text-primary whitespace-pre-wrap">{text}</div>
      </div>
    </div>
  )
}

// Assistant message
function AssistantMessageCard({ data }: { data: any }) {
  const text = data.text || ''
  if (!text.trim()) return null
  
  return (
    <div className="flex gap-3 py-3">
      <div className="shrink-0 w-6 h-6 rounded-full bg-accent flex items-center justify-center text-on-accent">
        <BotIcon />
      </div>
      <div className="flex-1 min-w-0 pt-0.5">
        <div className="text-xs font-medium text-text-tertiary mb-1">Assistant</div>
        <div className="text-sm text-text-primary whitespace-pre-wrap">{text.trim()}</div>
      </div>
    </div>
  )
}

// Thinking indicator
function ThinkingCard({ messages }: { messages: UnifiedMessage[] }) {
  const [expanded, setExpanded] = useState(false)
  const thinkingText = messages
    .filter(m => m.data?.text)
    .map(m => m.data.text)
    .join('')
  
  if (!thinkingText) {
    return (
      <div className="flex items-center gap-2 py-2 text-xs text-text-tertiary">
        <ThinkingIcon />
        <span>Thinking...</span>
      </div>
    )
  }
  
  return (
    <div className="py-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-xs text-text-tertiary hover:text-text-secondary transition-colors"
      >
        <ThinkingIcon />
        <span>Thinking</span>
        <span className="text-text-disabled">{expanded ? '▼' : '▶'}</span>
      </button>
      {expanded && (
        <div className="mt-2 pl-5 text-xs text-text-tertiary italic whitespace-pre-wrap border-l-2 border-border-muted">
          {thinkingText}
        </div>
      )}
    </div>
  )
}

// Tool call card (unified for both formats)
function ToolCallCard({ messages }: { messages: UnifiedMessage[] }) {
  const [expanded, setExpanded] = useState(false)
  
  const toolCall = messages.find(m => m.type === 'tool_call')
  const toolResult = messages.find(m => m.type === 'tool_result' || (m.type === 'tool_call' && m.data.status === 'completed'))
  
  if (!toolCall) return null
  
  const name = toolCall.data.name || 'unknown'
  const input = toolCall.data.input || {}
  const displayName = formatToolName(name)
  
  // Determine result
  let result: any = null
  let isError = false
  let isCompleted = false
  
  if (toolResult) {
    isCompleted = true
    if (toolResult.type === 'tool_result') {
      // Claude Code style
      result = toolResult.data.content || toolResult.data.parsed_result
      isError = toolResult.data.is_error
    } else {
      // Composer style
      result = toolResult.data.result
      isError = toolResult.data.is_error
    }
  }
  
  // Get inline info
  let inlineInfo = ''
  if (input.file_path || input.path) {
    inlineInfo = formatPath(input.file_path || input.path)
  } else if (input.query) {
    inlineInfo = input.query.substring(0, 40) + (input.query.length > 40 ? '...' : '')
  } else if (input.command) {
    inlineInfo = input.command.substring(0, 40) + (input.command.length > 40 ? '...' : '')
  }
  
  return (
    <div className="my-2 ml-9">
      <div className={cn(
        'border rounded-lg overflow-hidden',
        isCompleted 
          ? isError ? 'border-status-error/30 bg-status-error-muted' : 'border-status-success/30 bg-status-success-muted'
          : 'border-status-warning/30 bg-status-warning-muted'
      )}>
        {/* Header */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full px-3 py-2 flex items-center gap-2 text-left hover:bg-black/5 transition-colors"
        >
          <span className={cn(
            'shrink-0',
            isCompleted 
              ? isError ? 'text-status-error' : 'text-status-success'
              : 'text-status-warning'
          )}>
            {isCompleted ? (isError ? <ErrorIcon /> : <CheckIcon />) : <ToolIcon />}
          </span>
          <span className="text-sm font-medium text-text-primary">{displayName}</span>
          {inlineInfo && (
            <span className="text-xs text-text-tertiary font-mono truncate max-w-[300px]">{inlineInfo}</span>
          )}
          <span className="ml-auto text-text-disabled text-xs">{expanded ? '▼' : '▶'}</span>
        </button>
        
        {/* Expanded content */}
        {expanded && (
          <div className="border-t border-inherit">
            {/* Input */}
            <div className="px-3 py-2 bg-surface/50">
              <div className="text-xs text-text-tertiary mb-1">Input</div>
              <pre className="text-xs font-mono text-text-secondary overflow-x-auto max-h-40">
                {JSON.stringify(input, null, 2)}
              </pre>
            </div>
            
            {/* Result */}
            {result && (
              <div className="px-3 py-2 border-t border-inherit">
                <div className="text-xs text-text-tertiary mb-1">
                  {isError ? 'Error' : 'Result'}
                </div>
                <pre className="text-xs font-mono text-text-secondary overflow-x-auto max-h-48 whitespace-pre-wrap">
                  {typeof result === 'string' ? result : JSON.stringify(result, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// Tool result card (standalone, for when we don't have the matching call)
function ToolResultCard({ data }: { data: any }) {
  const [expanded, setExpanded] = useState(false)
  const isError = data.is_error
  const content = data.content || data.parsed_result
  
  return (
    <div className="my-2 ml-9">
      <div className={cn(
        'border rounded-lg overflow-hidden',
        isError ? 'border-status-error/30 bg-status-error-muted' : 'border-status-success/30 bg-status-success-muted'
      )}>
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full px-3 py-2 flex items-center gap-2 text-left hover:bg-black/5 transition-colors"
        >
          <span className={isError ? 'text-status-error' : 'text-status-success'}>
            {isError ? <ErrorIcon /> : <CheckIcon />}
          </span>
          <span className="text-sm text-text-secondary">Tool Result</span>
          <span className="ml-auto text-text-disabled text-xs">{expanded ? '▼' : '▶'}</span>
        </button>
        {expanded && (
          <div className="px-3 py-2 border-t border-inherit">
            <pre className="text-xs font-mono text-text-secondary overflow-x-auto max-h-48 whitespace-pre-wrap">
              {typeof content === 'string' ? content : JSON.stringify(content, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}

// Result message (final)
function ResultCard({ data }: { data: any }) {
  const [expanded, setExpanded] = useState(false)
  const isError = !data.success
  const duration = data.duration_ms ? `${(data.duration_ms / 1000).toFixed(1)}s` : null
  const cost = data.cost_usd ? `$${data.cost_usd.toFixed(4)}` : null
  
  return (
    <div className="my-4">
      <div className="flex items-center justify-center gap-3">
        <div className="h-px flex-1 bg-border" />
        <button
          onClick={() => setExpanded(!expanded)}
          className={cn(
            'flex items-center gap-2 px-3 py-1.5 rounded-full text-xs transition-colors',
            isError ? 'bg-status-error-muted text-status-error' : 'bg-status-success-muted text-status-success',
            'hover:brightness-95'
          )}
        >
          {isError ? <ErrorIcon /> : <CheckIcon />}
          <span className="font-medium">{isError ? 'Failed' : 'Completed'}</span>
          {duration && <span className="text-text-tertiary">• {duration}</span>}
          {cost && <span className="text-text-tertiary">• {cost}</span>}
          <span className="text-text-disabled ml-1">{expanded ? '▼' : '▶'}</span>
        </button>
        <div className="h-px flex-1 bg-border" />
      </div>
      
      {expanded && data.modelUsage && (
        <div className="mt-3 p-3 bg-surface-2 rounded-lg text-xs">
          <div className="text-text-tertiary mb-2">Model Usage</div>
          <div className="space-y-1 font-mono">
            {Object.entries(data.modelUsage).map(([model, usage]: [string, any]) => (
              <div key={model} className="flex items-center justify-between">
                <span className="text-text-secondary">{model}</span>
                <span className="text-text-tertiary">
                  {usage.inputTokens?.toLocaleString() || 0} in / {usage.outputTokens?.toLocaleString() || 0} out
                  {usage.costUSD && <span className="ml-2 text-status-success">${usage.costUSD.toFixed(4)}</span>}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Chat view
function ChatView({ messages }: { messages: UnifiedMessage[] }) {
  const groups = useMemo(() => groupMessages(messages), [messages])
  
  return (
    <div className="space-y-1">
      {groups.map((group, idx) => {
        const firstMsg = group[0]
        
        switch (firstMsg.type) {
          case 'system':
            if (firstMsg.data?.subtype === 'init') {
              return <SystemInitCard key={idx} data={firstMsg.data} />
            }
            return null
          
          case 'user':
            return <UserMessageCard key={idx} data={firstMsg.data} />
          
          case 'thinking':
            return <ThinkingCard key={idx} messages={group} />
          
          case 'assistant':
            return <AssistantMessageCard key={idx} data={firstMsg.data} />
          
          case 'tool_call':
            return <ToolCallCard key={idx} messages={group} />
          
          case 'tool_result':
            // Standalone tool result (no matching call found)
            return <ToolResultCard key={idx} data={firstMsg.data} />
          
          case 'result':
            return <ResultCard key={idx} data={firstMsg.data} />
          
          case 'text':
            if (!firstMsg.data?.text?.trim()) return null
            return (
              <div key={idx} className="py-1 text-xs text-text-tertiary font-mono">
                {firstMsg.data.text}
              </div>
            )
          
          default:
            return null
        }
      })}
    </div>
  )
}

// Raw log view
function RawView({ text }: { text: string }) {
  const lines = text.split('\n')
  
  return (
    <div className="font-mono text-xs leading-relaxed">
      {lines.map((line, idx) => {
        let color = 'text-text-secondary'
        
        if (line.trim().startsWith('{')) {
          try {
            const parsed = JSON.parse(line.trim())
            const typeColors: Record<string, string> = {
              'system': 'text-text-tertiary',
              'user': 'text-status-info',
              'thinking': 'text-text-disabled',
              'assistant': 'text-accent',
              'tool_call': 'text-status-warning',
              'result': 'text-status-success',
            }
            color = typeColors[parsed.type] || 'text-text-tertiary'
          } catch {
            // Invalid JSON
          }
        }
        
        return (
          <div key={idx} className={cn('py-0.5 hover:bg-surface-2 px-1 -mx-1 rounded', color)}>
            <span className="text-text-disabled select-none mr-3 inline-block w-8 text-right">{idx + 1}</span>
            {line || '\u00A0'}
          </div>
        )
      })}
    </div>
  )
}

interface LogsViewerProps {
  logs: string
  title?: string
  defaultMode?: ViewMode
  maxHeight?: string
}

export default function LogsViewer({ 
  logs, 
  title = 'Output',
  defaultMode = 'chat',
  maxHeight = '600px'
}: LogsViewerProps) {
  const [viewMode, setViewMode] = useState<ViewMode>(defaultMode)
  const [autoScroll, setAutoScroll] = useState(true)
  const containerRef = useRef<HTMLDivElement>(null)

  const messages = useMemo(() => {
    return logs.split('\n').map(parseLogLine).filter(Boolean) as UnifiedMessage[]
  }, [logs])

  const handleScroll = useCallback(() => {
    if (!containerRef.current) return
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50
    setAutoScroll(isAtBottom)
  }, [])

  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  if (!logs) {
    return (
      <div className="bg-surface border border-border rounded-lg p-8 text-center">
        <div className="text-text-tertiary">No output yet</div>
      </div>
    )
  }

  return (
    <div className="border border-border rounded-lg overflow-hidden bg-surface">
      {/* Header */}
      <div className="flex items-center justify-between bg-surface-2 px-4 py-2.5 border-b border-border">
        <span className="text-sm font-medium text-text-primary">{title}</span>
        
        <div className="flex items-center gap-2">
          {/* View mode toggle */}
          <div className="flex rounded-lg overflow-hidden border border-border bg-surface">
            <button
              onClick={() => setViewMode('chat')}
              className={cn(
                'px-3 py-1.5 text-xs font-medium transition-all',
                viewMode === 'chat'
                  ? 'bg-accent text-on-accent'
                  : 'text-text-tertiary hover:text-text-secondary hover:bg-surface-2'
              )}
            >
              Chat
            </button>
            <button
              onClick={() => setViewMode('raw')}
              className={cn(
                'px-3 py-1.5 text-xs font-medium transition-all border-l border-border',
                viewMode === 'raw'
                  ? 'bg-accent text-on-accent'
                  : 'text-text-tertiary hover:text-text-secondary hover:bg-surface-2'
              )}
            >
              Raw
            </button>
          </div>
          
          {/* Scroll to bottom */}
          <Button
            variant={autoScroll ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => {
              setAutoScroll(true)
              if (containerRef.current) {
                containerRef.current.scrollTop = containerRef.current.scrollHeight
              }
            }}
            title={autoScroll ? 'Auto-scroll enabled' : 'Click to scroll to bottom'}
          >
            ↓
          </Button>
        </div>
      </div>

      {/* Content */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="p-4 overflow-auto bg-canvas"
        style={{ maxHeight }}
      >
        {viewMode === 'chat' ? (
          <ChatView messages={messages} />
        ) : (
          <RawView text={logs} />
        )}
      </div>
    </div>
  )
}
