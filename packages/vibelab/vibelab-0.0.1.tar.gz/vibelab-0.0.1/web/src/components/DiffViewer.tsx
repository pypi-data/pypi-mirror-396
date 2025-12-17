import { useState, useMemo } from 'react'
import { cn } from '../lib/cn'

interface DiffViewerProps {
  patch: string
  className?: string
}

interface DiffHunk {
  header: string
  oldStart: number
  newStart: number
  lines: Array<{
    type: 'addition' | 'deletion' | 'context' | 'header'
    content: string
    oldLineNum?: number
    newLineNum?: number
  }>
}

interface DiffFile {
  header: string
  oldPath: string
  newPath: string
  hunks: DiffHunk[]
}

function parseDiff(patch: string): DiffFile[] {
  const files: DiffFile[] = []
  const lines = patch.split('\n')
  
  let currentFile: DiffFile | null = null
  let currentHunk: DiffHunk | null = null
  let oldLineNum = 0
  let newLineNum = 0
  
  for (const line of lines) {
    // File header
    if (line.startsWith('diff --git')) {
      if (currentFile) files.push(currentFile)
      const match = line.match(/a\/(.+?) b\/(.+)/)
      currentFile = {
        header: line,
        oldPath: match?.[1] || '',
        newPath: match?.[2] || '',
        hunks: []
      }
      currentHunk = null
      continue
    }
    
    // Skip index and mode lines
    if (line.startsWith('index ') || line.startsWith('old mode') || line.startsWith('new mode')) {
      continue
    }
    
    // Old/new file markers
    if (line.startsWith('---') || line.startsWith('+++')) {
      continue
    }
    
    // Hunk header
    if (line.startsWith('@@')) {
      const match = line.match(/@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@/)
      oldLineNum = match ? parseInt(match[1], 10) : 1
      newLineNum = match ? parseInt(match[2], 10) : 1
      currentHunk = {
        header: line,
        oldStart: oldLineNum,
        newStart: newLineNum,
        lines: [{
          type: 'header',
          content: line
        }]
      }
      if (currentFile) currentFile.hunks.push(currentHunk)
      continue
    }
    
    if (!currentHunk) continue
    
    if (line.startsWith('+')) {
      currentHunk.lines.push({
        type: 'addition',
        content: line.slice(1),
        newLineNum: newLineNum++
      })
    } else if (line.startsWith('-')) {
      currentHunk.lines.push({
        type: 'deletion',
        content: line.slice(1),
        oldLineNum: oldLineNum++
      })
    } else {
      currentHunk.lines.push({
        type: 'context',
        content: line.startsWith(' ') ? line.slice(1) : line,
        oldLineNum: oldLineNum++,
        newLineNum: newLineNum++
      })
    }
  }
  
  if (currentFile) files.push(currentFile)
  return files
}

function FileIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" className="text-text-tertiary">
      <path fillRule="evenodd" d="M3.75 1.5a.25.25 0 0 0-.25.25v12.5c0 .138.112.25.25.25h8.5a.25.25 0 0 0 .25-.25V4.664a.25.25 0 0 0-.073-.177l-2.914-2.914a.25.25 0 0 0-.177-.073H3.75zM2 1.75C2 .784 2.784 0 3.75 0h5.586c.464 0 .909.184 1.237.513l2.914 2.914c.329.328.513.773.513 1.237v9.586A1.75 1.75 0 0 1 12.25 16h-8.5A1.75 1.75 0 0 1 2 14.25V1.75z"/>
    </svg>
  )
}

function DiffFileView({ file }: { file: DiffFile }) {
  const [expanded, setExpanded] = useState(true)
  
  const stats = useMemo(() => {
    let additions = 0
    let deletions = 0
    for (const hunk of file.hunks) {
      for (const line of hunk.lines) {
        if (line.type === 'addition') additions++
        if (line.type === 'deletion') deletions++
      }
    }
    return { additions, deletions }
  }, [file])
  
  return (
    <div className="border border-border rounded-lg overflow-hidden w-full">
      {/* File header */}
      <div 
        className="flex items-center gap-2 px-3 py-2 bg-surface-2 border-b border-border cursor-pointer hover:bg-surface-3 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <button className="text-text-tertiary hover:text-text-secondary">
          <svg 
            width="12" 
            height="12" 
            viewBox="0 0 12 12" 
            fill="currentColor"
            className={cn('transition-transform', expanded ? 'rotate-90' : '')}
          >
            <path d="M4.5 2L9 6l-4.5 4V2z"/>
          </svg>
        </button>
        <FileIcon />
        <span className="text-sm font-mono text-text-primary flex-1 truncate">
          {file.newPath || file.oldPath}
        </span>
        <div className="flex items-center gap-2 text-xs">
          {stats.additions > 0 && (
            <span className="text-status-success font-medium">+{stats.additions}</span>
          )}
          {stats.deletions > 0 && (
            <span className="text-status-error font-medium">−{stats.deletions}</span>
          )}
        </div>
      </div>
      
      {/* Diff content */}
      {expanded && (
        <div className="overflow-x-auto">
          <table className="w-full min-w-full text-xs font-mono border-collapse table-fixed">
            <tbody>
              {file.hunks.map((hunk, hunkIdx) => (
                hunk.lines.map((line, lineIdx) => {
                  if (line.type === 'header') {
                    return (
                      <tr key={`${hunkIdx}-${lineIdx}`} className="bg-status-info-muted">
                        <td style={{ width: '50px' }} className="px-2 py-0.5 text-right text-status-info select-none border-r border-border-muted">...</td>
                        <td style={{ width: '50px' }} className="px-2 py-0.5 text-right text-status-info select-none border-r border-border-muted">...</td>
                        <td className="px-3 py-0.5 text-status-info">{line.content}</td>
                      </tr>
                    )
                  }
                  
                  const bgClass = {
                    addition: 'bg-status-success-muted',
                    deletion: 'bg-status-error-muted',
                    context: 'bg-surface'
                  }[line.type]
                  
                  const textClass = {
                    addition: 'text-status-success',
                    deletion: 'text-status-error',
                    context: 'text-text-secondary'
                  }[line.type]
                  
                  const lineNumClass = {
                    addition: 'bg-status-success-muted text-status-success',
                    deletion: 'bg-status-error-muted text-status-error',
                    context: 'bg-surface-2 text-text-tertiary'
                  }[line.type]
                  
                  const prefix = line.type === 'addition' ? '+' : line.type === 'deletion' ? '−' : ' '
                  
                  return (
                    <tr 
                      key={`${hunkIdx}-${lineIdx}`} 
                      className={cn(bgClass, 'hover:brightness-95 dark:hover:brightness-110 transition-all')}
                    >
                      <td style={{ width: '50px' }} className={cn('px-2 py-0.5 text-right select-none border-r border-border-muted tabular-nums', lineNumClass)}>
                        {line.oldLineNum ?? ''}
                      </td>
                      <td style={{ width: '50px' }} className={cn('px-2 py-0.5 text-right select-none border-r border-border-muted tabular-nums', lineNumClass)}>
                        {line.newLineNum ?? ''}
                      </td>
                      <td className={cn('px-3 py-0.5 whitespace-pre overflow-hidden text-ellipsis', textClass)}>
                        <span className="select-none mr-2">{prefix}</span>
                        {line.content || ' '}
                      </td>
                    </tr>
                  )
                })
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default function DiffViewer({ patch, className }: DiffViewerProps) {
  const files = useMemo(() => parseDiff(patch), [patch])
  
  if (!patch || files.length === 0) {
    return (
      <div className={cn('bg-surface border border-border rounded-lg p-8 text-center', className)}>
        <div className="text-text-tertiary">No changes</div>
      </div>
    )
  }
  
  const totalStats = useMemo(() => {
    let additions = 0
    let deletions = 0
    for (const file of files) {
      for (const hunk of file.hunks) {
        for (const line of hunk.lines) {
          if (line.type === 'addition') additions++
          if (line.type === 'deletion') deletions++
        }
      }
    }
    return { additions, deletions, files: files.length }
  }, [files])
  
  return (
    <div className={cn('space-y-3', className)}>
      {/* Summary header */}
      <div className="flex items-center gap-4 text-sm text-text-secondary">
        <span>
          Showing <strong className="text-text-primary">{totalStats.files}</strong> changed {totalStats.files === 1 ? 'file' : 'files'}
        </span>
        <span className="text-status-success font-medium">+{totalStats.additions}</span>
        <span className="text-status-error font-medium">−{totalStats.deletions}</span>
      </div>
      
      {/* File diffs */}
      <div className="space-y-4">
        {files.map((file, idx) => (
          <DiffFileView key={idx} file={file} />
        ))}
      </div>
    </div>
  )
}
