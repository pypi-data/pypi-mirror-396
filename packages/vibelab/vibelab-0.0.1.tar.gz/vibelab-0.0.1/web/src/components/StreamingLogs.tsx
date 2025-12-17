import { useEffect, useState } from 'react'
import { subscribeToResultStream } from '../api'
import LogsViewer from './LogsViewer'
import { cn } from '../lib/cn'

interface StreamingLogsProps {
  resultId: number
  onStatusChange?: (status: string) => void
  onPatchUpdate?: (patch: string) => void
  onComplete?: () => void
  initialLogs?: string
}

export default function StreamingLogs({
  resultId,
  onStatusChange,
  onPatchUpdate,
  onComplete,
  initialLogs = '',
}: StreamingLogsProps) {
  const [logs, setLogs] = useState(initialLogs)
  const [status, setStatus] = useState<string>('connecting')
  const [isStreaming, setIsStreaming] = useState(true)

  useEffect(() => {
    const close = subscribeToResultStream(resultId, {
      onConnect: () => setStatus('connected'),
      onStatus: (newStatus) => {
        setStatus(newStatus)
        onStatusChange?.(newStatus)
      },
      onOutput: (data) => setLogs((prev) => prev + data),
      onPatch: (patch) => onPatchUpdate?.(patch),
      onDone: (finalStatus) => {
        setStatus(finalStatus)
        setIsStreaming(false)
        onStatusChange?.(finalStatus)
        onComplete?.()
      },
      onError: (error) => {
        setStatus('error')
        setIsStreaming(false)
        setLogs((prev) => prev + `\n\n[Error: ${error}]`)
      },
    })

    return () => close()
  }, [resultId, onStatusChange, onPatchUpdate, onComplete])

  const statusConfig = {
    connecting: { color: 'bg-status-warning', label: 'Connecting' },
    connected: { color: 'bg-status-info', label: 'Connected' },
    queued: { color: 'bg-status-warning', label: 'Queued' },
    starting: { color: 'bg-status-info', label: 'Starting' },
    cloning: { color: 'bg-status-info', label: 'Cloning repository' },
    running: { color: 'bg-status-info', label: 'Running' },
    completed: { color: 'bg-status-success', label: 'Completed' },
    failed: { color: 'bg-status-error', label: 'Failed' },
    infra_failure: { color: 'bg-status-error', label: 'Infra Failure' },
    error: { color: 'bg-status-error', label: 'Error' },
    waiting: { color: 'bg-status-warning', label: 'Waiting' },
    timeout: { color: 'bg-status-error', label: 'Timeout' },
  }[status] || { color: 'bg-text-tertiary', label: status }

  return (
    <div className="flex flex-col h-full">
      {/* Streaming status banner */}
      <div className="flex items-center gap-2 px-4 py-2 bg-surface-2 rounded-t border-b border-border">
        <div className={cn('w-2 h-2 rounded-full', statusConfig.color, isStreaming && 'animate-pulse')} />
        <span className="text-xs text-text-tertiary uppercase tracking-wider">{statusConfig.label}</span>
        {isStreaming && (
          <span className="text-xs text-accent ml-auto animate-pulse">● Live</span>
        )}
      </div>
      
      {/* Logs viewer */}
      {logs ? (
        <LogsViewer 
          logs={logs} 
          title={`vibelab — result ${resultId}`}
          defaultMode="chat"
          maxHeight="500px"
        />
      ) : (
        <div className="bg-canvas p-4 rounded-b text-text-disabled flex items-center gap-2 min-h-[200px] justify-center">
          {isStreaming ? (
            <>
              <span className="inline-block w-2 h-4 bg-text-tertiary animate-pulse" />
              Waiting for output...
            </>
          ) : (
            'No output'
          )}
        </div>
      )}
    </div>
  )
}
