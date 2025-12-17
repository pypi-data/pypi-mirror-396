import { useState, Fragment } from 'react'
import { cn } from '../lib/cn'

interface DiffLine {
  type: 'context' | 'added' | 'removed' | 'hunk'
  content: string
  oldLineNumber: number | null
  newLineNumber: number | null
}

interface ParsedDiff {
  lines: DiffLine[]
  oldPath: string | null
  newPath: string | null
}

function parseUnifiedDiff(patch: string): ParsedDiff {
  const lines = patch.split('\n')
  const diffLines: DiffLine[] = []
  let oldPath: string | null = null
  let newPath: string | null = null
  let oldLineNum = 0
  let newLineNum = 0

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    // Extract file paths
    if (line.startsWith('---')) {
      const match = line.match(/^---\s+(?:a\/)?(.+)$/)
      if (match) oldPath = match[1]
      continue
    }
    if (line.startsWith('+++')) {
      const match = line.match(/^\+\+\+\s+(?:b\/)?(.+)$/)
      if (match) newPath = match[1]
      continue
    }

    // Hunk header: @@ -oldStart,oldCount +newStart,newCount @@
    if (line.startsWith('@@')) {
      const match = line.match(/^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@/)
      if (match) {
        oldLineNum = parseInt(match[1], 10)
        newLineNum = parseInt(match[3], 10)
        diffLines.push({
          type: 'hunk',
          content: line,
          oldLineNumber: null,
          newLineNumber: null,
        })
      }
      continue
    }

    // Diff lines
    if (line.startsWith(' ')) {
      // Context line (unchanged)
      diffLines.push({
        type: 'context',
        content: line.substring(1),
        oldLineNumber: oldLineNum,
        newLineNumber: newLineNum,
      })
      oldLineNum++
      newLineNum++
    } else if (line.startsWith('-')) {
      // Removed line
      diffLines.push({
        type: 'removed',
        content: line.substring(1),
        oldLineNumber: oldLineNum,
        newLineNumber: null,
      })
      oldLineNum++
    } else if (line.startsWith('+')) {
      // Added line
      diffLines.push({
        type: 'added',
        content: line.substring(1),
        oldLineNumber: null,
        newLineNumber: newLineNum,
      })
      newLineNum++
    } else if (line.trim() === '') {
      // Empty line
      diffLines.push({
        type: 'context',
        content: '',
        oldLineNumber: oldLineNum,
        newLineNumber: newLineNum,
      })
      oldLineNum++
      newLineNum++
    }
  }

  return { lines: diffLines, oldPath, newPath }
}

interface GitHubDiffViewerProps {
  patch: string
  maxHeight?: string
}

export default function GitHubDiffViewer({ patch, maxHeight = '600px' }: GitHubDiffViewerProps) {
  const parsed = parseUnifiedDiff(patch)
  const [expandedHunks, setExpandedHunks] = useState<Set<number>>(new Set([0])) // First hunk expanded by default

  // Group lines into hunks
  const hunks: Array<{ startIdx: number; endIdx: number }> = []
  let currentHunk: { startIdx: number; endIdx: number } | null = null

  parsed.lines.forEach((line, idx) => {
    if (line.type === 'hunk') {
      if (currentHunk) {
        currentHunk.endIdx = idx - 1
        hunks.push(currentHunk)
      }
      currentHunk = { startIdx: idx, endIdx: parsed.lines.length - 1 }
    }
  })
  if (currentHunk) {
    hunks.push(currentHunk)
  }

  // If no hunks found, treat entire diff as one hunk
  if (hunks.length === 0 && parsed.lines.length > 0) {
    hunks.push({ startIdx: 0, endIdx: parsed.lines.length - 1 })
  }

  const toggleHunk = (hunkIdx: number) => {
    setExpandedHunks((prev) => {
      const next = new Set(prev)
      if (next.has(hunkIdx)) {
        next.delete(hunkIdx)
      } else {
        next.add(hunkIdx)
      }
      return next
    })
  }

  const renderLine = (line: DiffLine, idx: number) => {
    const bgClass = {
      added: 'bg-status-success-muted',
      removed: 'bg-status-error-muted',
      context: 'bg-transparent',
      hunk: 'bg-status-info-muted',
    }[line.type]

    const textClass = {
      added: 'text-status-success',
      removed: 'text-status-error',
      context: 'text-text-secondary',
      hunk: 'text-status-info',
    }[line.type]

    return (
      <tr key={idx} className={cn('hover:brightness-95 dark:hover:brightness-110 transition-all', bgClass)}>
        {/* Old line number */}
        <td style={{ width: '50px' }} className="px-2 py-0.5 text-right text-xs text-text-disabled select-none border-r border-border-muted tabular-nums">
          {line.oldLineNumber !== null ? line.oldLineNumber : ''}
        </td>
        {/* New line number */}
        <td style={{ width: '50px' }} className="px-2 py-0.5 text-right text-xs text-text-disabled select-none border-r border-border-muted tabular-nums">
          {line.newLineNumber !== null ? line.newLineNumber : ''}
        </td>
        {/* Line content - takes remaining width */}
        <td className={cn('px-3 py-0.5 text-sm font-mono whitespace-pre', textClass)}>
          {line.type === 'hunk' ? (
            <span className="font-semibold">{line.content}</span>
          ) : (
            <span>{line.content || ' '}</span>
          )}
        </td>
      </tr>
    )
  }

  if (parsed.lines.length === 0) {
    return (
      <div className="border border-border rounded-lg p-8 text-text-tertiary text-sm text-center">
        No changes to display
      </div>
    )
  }

  return (
    <div className="border border-border rounded-lg overflow-hidden bg-surface w-full">
      {/* File header */}
      {(parsed.oldPath || parsed.newPath) && (
        <div className="bg-surface-2 border-b border-border px-4 py-2 text-sm">
          <div className="flex items-center gap-3">
            {parsed.oldPath && (
              <span className="text-status-error">
                <span className="text-text-disabled mr-1">---</span>
                <span className="font-mono">{parsed.oldPath}</span>
              </span>
            )}
            {parsed.newPath && (
              <span className="text-status-success">
                <span className="text-text-disabled mr-1">+++</span>
                <span className="font-mono">{parsed.newPath}</span>
              </span>
            )}
          </div>
        </div>
      )}

      {/* Diff table */}
      <div className="overflow-x-auto" style={{ maxHeight }}>
        <table className="w-full">
          <tbody>
            {hunks.map((hunk, hunkIdx) => {
              const isExpanded = expandedHunks.has(hunkIdx)
              const hunkLine = parsed.lines[hunk.startIdx]
              const startContentIdx = hunkLine.type === 'hunk' ? hunk.startIdx + 1 : hunk.startIdx
              const hunkLines = parsed.lines.slice(startContentIdx, hunk.endIdx + 1)

              return (
                <Fragment key={hunkIdx}>
                  {/* Hunk header */}
                  {hunkLine.type === 'hunk' && (
                    <tr className="bg-surface-2 hover:bg-surface-3 transition-colors">
                      <td colSpan={3} className="px-3 py-2">
                        <button
                          onClick={() => toggleHunk(hunkIdx)}
                          className="flex items-center gap-2 w-full text-left text-xs text-text-tertiary hover:text-text-secondary transition-colors"
                        >
                          <span className="text-text-disabled">{isExpanded ? '▼' : '▶'}</span>
                          <span className="font-mono text-status-info">{hunkLine.content}</span>
                          <span className="text-text-disabled">
                            ({hunkLines.length} line{hunkLines.length !== 1 ? 's' : ''})
                          </span>
                        </button>
                      </td>
                    </tr>
                  )}
                  {/* Hunk content */}
                  {isExpanded &&
                    hunkLines.map((line, lineIdx) => {
                      const actualLineIdx = startContentIdx + lineIdx
                      return renderLine(line, actualLineIdx)
                    })}
                </Fragment>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
