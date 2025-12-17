import { useSearchParams, Link, useNavigate } from 'react-router-dom'
import { useQueries, useQuery, useQueryClient } from '@tanstack/react-query'
import { getResult, getResultPatch, getResultLogs, Result, listScenarioJudgements, Judgement } from '../api'
import GitHubDiffViewer from './GitHubDiffViewer'
import LogsViewer from './LogsViewer'
import StreamingLogs from './StreamingLogs'
import { PageHeader, Card, Table, StatusBadge, Button, EmptyState, Select, QualityBadge } from './ui'
import { useState, useMemo } from 'react'

// Quality color mapping for scatter plot
function getQualityColor(quality: number | null | undefined): string {
  if (quality === null || quality === undefined) return '#6b7280'
  if (quality >= 3.5) return '#34d399' // emerald
  if (quality >= 2.5) return '#38bdf8' // sky
  if (quality >= 1.5) return '#fbbf24' // amber
  return '#f87171' // rose
}

// Scatter Plot component for time vs score tradeoff
interface ScatterPlotProps {
  results: Result[]
  judgementsByResult: Record<number, Judgement | null>
  onPointClick?: (resultId: number) => void
}

function TimeVsScoreChart({ results, judgementsByResult, onPointClick }: ScatterPlotProps) {
  const [hoveredPoint, setHoveredPoint] = useState<number | null>(null)
  const safeJudgements = judgementsByResult || {}
  
  // Collect data points (completed results with duration and quality)
  const dataPoints = useMemo(() => {
    return results
      .filter(r => r.status === 'completed' && r.duration_ms != null)
      .map(r => {
        // Get quality score - prefer human, fall back to judge
        let quality: number | undefined = r.quality ?? undefined
        if (quality === undefined) {
          const judgement = safeJudgements[r.id]
          quality = judgement?.quality ?? undefined
        }
        return {
          id: r.id,
          duration: r.duration_ms!,
          quality,
          executor: `${r.harness}:${r.provider}:${r.model}`,
          model: r.model,
        }
      })
      .filter(p => p.quality != null) as Array<{
        id: number
        duration: number
        quality: number
        executor: string
        model: string
      }>
  }, [results, safeJudgements])

  if (dataPoints.length === 0) {
    return (
      <div className="flex items-center justify-center h-[180px] text-text-tertiary text-sm">
        No completed results with quality scores yet
      </div>
    )
  }

  // Chart dimensions
  const width = 380
  const height = 180
  const padding = { top: 16, right: 16, bottom: 36, left: 50 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom

  // Calculate scales
  const durations = dataPoints.map(p => p.duration)
  const minDuration = Math.min(...durations)
  const maxDuration = Math.max(...durations)
  const durationRange = maxDuration - minDuration || 1

  // X scale: duration
  const xScale = (d: number) => padding.left + ((d - minDuration) / durationRange) * chartWidth
  // Y scale: quality (1-4)
  const yScale = (q: number) => padding.top + chartHeight - ((q - 1) / 3) * chartHeight

  // Format duration for labels
  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${Math.round(ms)}ms`
    if (ms < 60000) return `${(ms / 1000).toFixed(0)}s`
    return `${Math.round(ms / 60000)}m`
  }

  // X axis ticks
  const xTicks = [minDuration, (minDuration + maxDuration) / 2, maxDuration]
  // Y axis ticks
  const yTicks = [1, 2, 3, 4]
  const yLabels = ['Bad', 'Workable', 'Good', 'Perfect']

  return (
    <div className="relative">
      <svg width={width} height={height} className="overflow-visible">
        {/* Grid lines */}
        <g className="text-border">
          {yTicks.map(tick => (
            <line
              key={`y-grid-${tick}`}
              x1={padding.left}
              y1={yScale(tick)}
              x2={width - padding.right}
              y2={yScale(tick)}
              stroke="currentColor"
              strokeOpacity={0.3}
              strokeDasharray="4,4"
            />
          ))}
        </g>

        {/* X axis */}
        <line
          x1={padding.left}
          y1={height - padding.bottom}
          x2={width - padding.right}
          y2={height - padding.bottom}
          stroke="currentColor"
          className="text-border"
        />
        {xTicks.map(tick => (
          <g key={`x-tick-${tick}`}>
            <text
              x={xScale(tick)}
              y={height - padding.bottom + 14}
              textAnchor="middle"
              className="text-[10px] fill-text-tertiary"
            >
              {formatDuration(tick)}
            </text>
          </g>
        ))}
        <text
          x={padding.left + chartWidth / 2}
          y={height - 2}
          textAnchor="middle"
          className="text-[10px] fill-text-tertiary"
        >
          Execution Time
        </text>

        {/* Y axis */}
        <line
          x1={padding.left}
          y1={padding.top}
          x2={padding.left}
          y2={height - padding.bottom}
          stroke="currentColor"
          className="text-border"
        />
        {yTicks.map((tick, i) => (
          <g key={`y-tick-${tick}`}>
            <text
              x={padding.left - 8}
              y={yScale(tick) + 3}
              textAnchor="end"
              className="text-[10px] fill-text-tertiary"
            >
              {yLabels[i]}
            </text>
          </g>
        ))}

        {/* Data points */}
        {dataPoints.map(point => {
          const isHovered = hoveredPoint === point.id
          return (
            <g key={point.id}>
              <circle
                cx={xScale(point.duration)}
                cy={yScale(point.quality)}
                r={isHovered ? 8 : 6}
                fill={getQualityColor(point.quality)}
                fillOpacity={isHovered ? 1 : 0.8}
                stroke={isHovered ? '#fff' : 'transparent'}
                strokeWidth={2}
                className="cursor-pointer transition-all duration-150"
                onMouseEnter={() => setHoveredPoint(point.id)}
                onMouseLeave={() => setHoveredPoint(null)}
                onClick={() => onPointClick?.(point.id)}
              />
            </g>
          )
        })}
      </svg>

      {/* Tooltip */}
      {hoveredPoint && (() => {
        const point = dataPoints.find(p => p.id === hoveredPoint)
        if (!point) return null
        const x = xScale(point.duration)
        const y = yScale(point.quality)
        return (
          <div
            className="absolute pointer-events-none bg-surface-3 border border-border rounded-md shadow-lg px-2 py-1 text-xs z-10"
            style={{
              left: x + 12,
              top: y - 20,
              transform: x > width - 100 ? 'translateX(-100%)' : undefined,
            }}
          >
            <div className="font-medium text-text-primary truncate max-w-[150px]">{point.model}</div>
            <div className="text-text-tertiary">{formatDuration(point.duration)} • Quality: {point.quality}</div>
          </div>
        )
      })()}
    </div>
  )
}

interface ParsedPatch {
  files: Array<{ path: string; content: string }>
}

function parsePatch(patch: string): ParsedPatch {
  const files: Array<{ path: string; content: string }> = []
  const lines = patch.split('\n')
  let currentFile: { path: string; content: string } | null = null
  let seenPaths = new Set<string>()

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    
    if (line.startsWith('---') || line.startsWith('+++')) {
      const match = line.match(/^[+-]{3}\s+(?:a|b)\/(.+)$/)
      if (match) {
        const path = match[1]
        if (!seenPaths.has(path)) {
          if (currentFile) {
            files.push(currentFile)
          }
          seenPaths.add(path)
          currentFile = { path, content: line + '\n' }
        } else {
          if (currentFile) {
            currentFile.content += line + '\n'
          }
        }
      } else {
        if (currentFile) {
          currentFile.content += line + '\n'
        }
      }
    } else {
      if (currentFile) {
        currentFile.content += line + '\n'
      } else {
        if (line.startsWith('@@') || line.startsWith('+') || line.startsWith('-') || line.trim() === '') {
          if (!files.length) {
            files.push({ path: 'changes', content: line + '\n' })
          } else {
            files[files.length - 1].content += line + '\n'
          }
        }
      }
    }
  }

  if (currentFile) {
    files.push(currentFile)
  }

  if (files.length === 0 && patch.trim()) {
    files.push({ path: 'changes', content: patch })
  }

  return { files }
}

// Extract file contents from a patch (for baseline comparison)
function extractFileContents(patch: string): Record<string, string> {
  const parsed = parsePatch(patch)
  const contents: Record<string, string> = {}
  for (const file of parsed.files) {
    contents[file.path] = file.content
  }
  return contents
}

// Compute a simple diff between two patches (for baseline comparison)
function computePatchDiff(baselinePatch: string, resultPatch: string): string {
  const baselineFiles = extractFileContents(baselinePatch)
  const resultFiles = extractFileContents(resultPatch)
  
  // Collect all file paths
  const allFiles = new Set([...Object.keys(baselineFiles), ...Object.keys(resultFiles)])
  
  const diffLines: string[] = []
  
  for (const filePath of Array.from(allFiles).sort()) {
    const baselineContent = baselineFiles[filePath] || ''
    const resultContent = resultFiles[filePath] || ''
    
    if (baselineContent === resultContent) {
      continue // No changes
    }
    
    // File header
    diffLines.push(`diff --git a/${filePath} b/${filePath}`)
    diffLines.push(`--- a/${filePath}`)
    diffLines.push(`+++ b/${filePath}`)
    
    // Simple line-by-line diff
    const baselineLines = baselineContent.split('\n')
    const resultLines = resultContent.split('\n')
    
    // Find differences
    const maxLen = Math.max(baselineLines.length, resultLines.length)
    for (let i = 0; i < maxLen; i++) {
      const baselineLine = baselineLines[i]
      const resultLine = resultLines[i]
      
      if (baselineLine === undefined) {
        diffLines.push(`+${resultLine}`)
      } else if (resultLine === undefined) {
        diffLines.push(`-${baselineLine}`)
      } else if (baselineLine !== resultLine) {
        diffLines.push(`-${baselineLine}`)
        diffLines.push(`+${resultLine}`)
      } else {
        diffLines.push(` ${baselineLine}`)
      }
    }
  }
  
  return diffLines.join('\n')
}

function FileDiffViewer({ patch }: { patch: string }) {
  const parsed = parsePatch(patch)
  const [selectedFile, setSelectedFile] = useState<string | null>(
    parsed.files.length > 0 ? parsed.files[0].path : null
  )

  if (parsed.files.length === 0) {
    return <GitHubDiffViewer patch={patch} />
  }

  if (parsed.files.length === 1) {
    return <GitHubDiffViewer patch={parsed.files[0].content} />
  }

  const selectedFileContent =
    parsed.files.find((f) => f.path === selectedFile)?.content || parsed.files[0].content

  return (
    <div className="space-y-2">
      {/* File tabs */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {parsed.files.map((file) => (
          <button
            key={file.path}
            onClick={() => setSelectedFile(file.path)}
            className={`px-3 py-1.5 text-sm rounded whitespace-nowrap transition-colors ${
              selectedFile === file.path
                ? 'bg-accent text-on-accent font-medium'
                : 'bg-surface-2 text-text-secondary hover:bg-surface-3 hover:text-text-primary'
            }`}
          >
            {file.path.split('/').pop()}
          </button>
        ))}
      </div>
      {/* Diff content */}
      <GitHubDiffViewer patch={selectedFileContent} />
    </div>
  )
}

function ComparisonTable({ results, judgementsByResult }: { results: Result[]; judgementsByResult: Record<number, Judgement | null> }) {
  // Ensure judgementsByResult is never undefined
  const safeJudgements = judgementsByResult || {}
  
  return (
    <div>
      {/* <h2 className="text-lg font-semibold text-text-primary mb-3">Comparison</h2> */}
      <Table>
        <Table.Header>
          <tr>
            <Table.Head>Executor</Table.Head>
            <Table.Head>Status</Table.Head>
            <Table.Head className="text-center">Human</Table.Head>
            <Table.Head className="text-center">Judge</Table.Head>
            <Table.Head className="text-right">Duration</Table.Head>
            <Table.Head className="text-right">+/-</Table.Head>
            <Table.Head className="text-right">Files</Table.Head>
            <Table.Head className="text-right">Cost</Table.Head>
          </tr>
        </Table.Header>
        <Table.Body>
          {results.map((result) => {
            const judgement = safeJudgements[result.id]
            return (
              <Table.Row key={result.id}>
                <Table.Cell mono className="text-xs">
                  <Link to={`/result/${result.id}`} className="text-accent hover:text-accent-hover">
                    {result.harness}:{result.provider}:{result.model}
                  </Link>
                </Table.Cell>
                <Table.Cell>
                  <StatusBadge status={result.status} isStale={result.is_stale} />
                </Table.Cell>
                <Table.Cell className="text-center">
                  <QualityBadge quality={result.quality as 1 | 2 | 3 | 4 | null | undefined} />
                </Table.Cell>
                <Table.Cell className="text-center">
                  {judgement ? (
                    <QualityBadge quality={judgement.quality as 1 | 2 | 3 | 4 | null | undefined} />
                  ) : (
                    <span className="text-text-disabled text-xs">—</span>
                  )}
                </Table.Cell>
                <Table.Cell className="text-right text-text-secondary text-xs">
                  {result.duration_ms ? `${(result.duration_ms / 1000).toFixed(1)}s` : '—'}
                </Table.Cell>
                <Table.Cell className="text-right text-xs">
                  {result.lines_added !== null && result.lines_added !== undefined ? (
                    <span>
                      <span className="text-status-success">+{result.lines_added}</span>
                      <span className="text-text-tertiary">/</span>
                      <span className="text-status-error">-{result.lines_removed || 0}</span>
                    </span>
                  ) : '—'}
                </Table.Cell>
                <Table.Cell className="text-right text-text-secondary text-xs">
                  {result.files_changed !== null && result.files_changed !== undefined ? result.files_changed : '—'}
                </Table.Cell>
                <Table.Cell className="text-right text-text-secondary text-xs">
                  {result.cost_usd ? `$${result.cost_usd.toFixed(4)}` : '—'}
                </Table.Cell>
              </Table.Row>
            )
          })}
        </Table.Body>
      </Table>
    </div>
  )
}

type ViewMode = 'logs' | 'split' | 'files'

function ViewModeSwitcher({ value, onChange }: { value: ViewMode; onChange: (mode: ViewMode) => void }) {
  const options: { value: ViewMode; label: string; icon: React.ReactNode }[] = [
    {
      value: 'logs',
      label: 'Logs',
      icon: (
        <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
          <path d="M5 3.5h6A1.5 1.5 0 0112.5 5v6a1.5 1.5 0 01-1.5 1.5H5A1.5 1.5 0 013.5 11V5A1.5 1.5 0 015 3.5zM5 2A3 3 0 002 5v6a3 3 0 003 3h6a3 3 0 003-3V5a3 3 0 00-3-3H5z"/>
          <path d="M5 6h6v1H5V6zm0 2h6v1H5V8zm0 2h4v1H5v-1z"/>
        </svg>
      ),
    },
    {
      value: 'split',
      label: 'Split',
      icon: (
        <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
          <path d="M14 1a1 1 0 011 1v12a1 1 0 01-1 1H2a1 1 0 01-1-1V2a1 1 0 011-1h12zM2 0a2 2 0 00-2 2v12a2 2 0 002 2h12a2 2 0 002-2V2a2 2 0 00-2-2H2z"/>
          <path d="M7.5 2v12h1V2h-1z"/>
        </svg>
      ),
    },
    {
      value: 'files',
      label: 'Files',
      icon: (
        <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
          <path d="M3.75 1.5a.25.25 0 00-.25.25v12.5c0 .138.112.25.25.25h8.5a.25.25 0 00.25-.25V4.664a.25.25 0 00-.073-.177l-2.914-2.914a.25.25 0 00-.177-.073H3.75zM2 1.75C2 .784 2.784 0 3.75 0h5.586c.464 0 .909.184 1.237.513l2.914 2.914c.329.328.513.773.513 1.237v9.586A1.75 1.75 0 0112.25 16h-8.5A1.75 1.75 0 012 14.25V1.75z"/>
          <path d="M9.5 0v3.5a1 1 0 001 1H14"/>
        </svg>
      ),
    },
  ]

  return (
    <div className="inline-flex items-center bg-surface border border-border rounded-lg p-1 gap-1">
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={`
            flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-150
            ${value === option.value
              ? 'bg-accent text-on-accent shadow-sm'
              : 'text-text-secondary hover:text-text-primary hover:bg-surface-2'
            }
          `}
        >
          {option.icon}
          <span>{option.label}</span>
        </button>
      ))}
    </div>
  )
}

export default function CompareResults() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const ids = useMemo(() => searchParams.get('ids')?.split(',').map(Number).filter(Boolean) || [], [searchParams])
  const scenarioId = searchParams.get('scenario')
  
  const [baselineId, setBaselineId] = useState<number | null>(ids.length > 0 ? ids[0] : null)
  const [groupBy, setGroupBy] = useState<'executor' | 'file'>('executor')
  const [compareTo, setCompareTo] = useState<'parent' | 'baseline'>('parent')
  const [viewMode, setViewMode] = useState<ViewMode>('split')

  const breadcrumbs = scenarioId
    ? [
        { label: 'Scenarios', path: '/scenarios' },
        { label: `Scenario ${scenarioId}`, path: `/scenario/${scenarioId}` },
        { label: 'Compare' },
      ]
    : [{ label: 'Compare' }]

  // Fetch all results and patches
  const resultsQueries = useQueries({
    queries: ids.map((id) => ({
      queryKey: ['result', id],
      queryFn: () => getResult(id),
      // Poll every 2 seconds while result is running/queued
      refetchInterval: (query: any) => {
        const data = query.state.data
        const isActive = data?.status === 'running' || data?.status === 'queued'
        return isActive ? 2000 : false
      },
    })),
  })

  const patchQueries = useQueries({
    queries: ids.map((id, idx) => {
      const result = resultsQueries[idx]?.data
      const isRunning = result?.status === 'running' || result?.status === 'queued'
      return {
        queryKey: ['result-patch', id],
        queryFn: () => getResultPatch(id),
        enabled: !!result && !isRunning,
      }
    }),
  })

  const results = resultsQueries.map((q) => q.data).filter((r): r is Result => !!r)
  const patches = patchQueries.map((q) => q.data?.patch || '')
  
  const isLoading = ids.length >= 2 && results.length !== ids.length
  const hasEnoughIds = ids.length >= 2

  // Get scenario ID from URL or from results
  const effectiveScenarioId = scenarioId ? Number(scenarioId) : results[0]?.scenario_id

  // Fetch judgements for the scenario
  const { data: scenarioJudgements } = useQuery({
    queryKey: ['scenario-judgements', effectiveScenarioId],
    queryFn: () => listScenarioJudgements(effectiveScenarioId!),
    enabled: !!effectiveScenarioId && results.length > 0,
  })

  // Map judgements to results (latest judgement per result)
  const judgementsByResult = useMemo(() => {
    const map: Record<number, Judgement | null> = {}
    for (const id of ids) {
      map[id] = null
    }
    if (scenarioJudgements) {
      // Group by result_id, take the latest one
      const byResultId = new Map<number, Judgement[]>()
      for (const j of scenarioJudgements) {
        if (!byResultId.has(j.result_id)) {
          byResultId.set(j.result_id, [])
        }
        byResultId.get(j.result_id)!.push(j)
      }
      // For each result, take the latest judgement
      for (const [resultId, judgements] of byResultId) {
        if (judgements.length > 0) {
          const sorted = judgements.sort((a, b) => 
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          )
          map[resultId] = sorted[0]
        }
      }
    }
    return map
  }, [scenarioJudgements, ids])

  const baselinePatch = baselineId ? patches[results.findIndex((r) => r.id === baselineId)] || '' : ''

  // Compute display patches based on compareTo mode
  // Must be called unconditionally (before any early returns)
  const displayPatches = useMemo(() => {
    if (!hasEnoughIds || isLoading) return []
    return patches.map((patch, idx) => {
      const result = results[idx]
      if (!result) return patch
      
      const isBaseline = baselineId === result.id
      
      if (compareTo === 'baseline' && baselineId && !isBaseline && baselinePatch) {
        // Compare against baseline - compute diff
        return computePatchDiff(baselinePatch, patch)
      }
      
      // Default: show parent patch (original patch from result)
      return patch
    })
  }, [patches, results, baselineId, baselinePatch, compareTo, hasEnoughIds, isLoading])

  // Group files across all results for "Group by File" mode
  // Must be called unconditionally (before any early returns)
  const filesByPath = useMemo(() => {
    const fileMap = new Map<string, Array<{ result: Result; patch: string; fileContent: string }>>()
    
    if (!hasEnoughIds || isLoading) return fileMap
    
    results.forEach((result, idx) => {
      // Skip baseline when comparing to baseline
      if (compareTo === 'baseline' && baselineId === result.id) {
        return
      }
      
      const patch = displayPatches[idx] || ''
      const parsed = parsePatch(patch)
      
      parsed.files.forEach((file) => {
        // Skip "changes" files that are empty or have minimal content
        if (file.path === 'changes') {
          const trimmedContent = file.content.trim()
          // Skip if empty or only contains whitespace/newlines
          if (!trimmedContent || trimmedContent.split('\n').filter(l => l.trim()).length === 0) {
            return
          }
        }
        
        if (!fileMap.has(file.path)) {
          fileMap.set(file.path, [])
        }
        fileMap.get(file.path)!.push({
          result,
          patch,
          fileContent: file.content,
        })
      })
    })
    
    return fileMap
  }, [results, displayPatches, compareTo, baselineId, hasEnoughIds, isLoading])

  // Early returns AFTER all hooks
  if (!hasEnoughIds) {
    return (
      <div>
        <PageHeader
          breadcrumbs={breadcrumbs}
          title="Compare Results"
        />
        <EmptyState
          title="Select at least 2 results to compare"
          description="Go back and select multiple results from a scenario to compare them side by side."
          action={
            scenarioId ? (
              <Link to={`/scenario/${scenarioId}`}>
                <Button>Back to Scenario</Button>
              </Link>
            ) : (
              <Link to="/runs">
                <Button>View Runs</Button>
              </Link>
            )
          }
        />
      </div>
    )
  }

  if (isLoading) {
    return (
      <div>
        <PageHeader
          breadcrumbs={breadcrumbs}
          title="Compare Results"
        />
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </div>
    )
  }

  // Logs panel content
  function LogsPanel({ result, maxHeight = '500px' }: { result: Result; maxHeight?: string }) {
    const queryClient = useQueryClient()
    const isRunning = result.status === 'running' || result.status === 'queued'
    
    const { data: logsData } = useQuery({
      queryKey: ['result-logs', result.id],
      queryFn: () => getResultLogs(result.id),
      enabled: !isRunning && !!result.id,
    })

    if (isRunning) {
      return (
        <StreamingLogs
          resultId={result.id}
          onStatusChange={(status) => {
            // Invalidate queries when status changes to refresh UI
            if (status === 'completed' || status === 'failed' || status === 'infra_failure') {
              queryClient.invalidateQueries({ queryKey: ['result', result.id] })
              queryClient.invalidateQueries({ queryKey: ['result-logs', result.id] })
              queryClient.invalidateQueries({ queryKey: ['result-patch', result.id] })
            }
          }}
          onComplete={() => {
            queryClient.invalidateQueries({ queryKey: ['result', result.id] })
            queryClient.invalidateQueries({ queryKey: ['result-logs', result.id] })
            queryClient.invalidateQueries({ queryKey: ['result-patch', result.id] })
          }}
        />
      )
    }
    
    if (logsData) {
      return (
        <div className="space-y-4">
          {logsData.stdout && (
            <LogsViewer 
              logs={logsData.stdout} 
              title="stdout" 
              defaultMode="chat"
              maxHeight={maxHeight}
            />
          )}
          {logsData.stderr && logsData.stderr.trim() && (
            <LogsViewer 
              logs={logsData.stderr} 
              title="stderr" 
              defaultMode="raw"
              maxHeight="200px"
            />
          )}
          {!logsData.stdout && !logsData.stderr?.trim() && (
            <div className="py-8 text-center text-text-tertiary text-sm">No output recorded</div>
          )}
        </div>
      )
    }
    
    return <div className="py-8 text-center text-text-tertiary">Loading logs...</div>
  }

  // Files panel content
  function FilesPanel({ patch }: { patch: string }) {
    if (patch) {
      return <FileDiffViewer patch={patch} />
    }
    return <div className="py-8 text-center text-text-tertiary">No patch available</div>
  }

  // Result card component with viewMode support
  function ResultCard({ 
    result, 
    patch, 
    isBaseline 
  }: { 
    result: Result
    patch: string
    isBaseline: boolean
  }) {
    return (
      <Card>
        <Card.Header>
          <div className="flex items-center justify-between">
            <Card.Title className="font-mono text-sm">
              {result.harness}:{result.provider}:{result.model}
              {isBaseline && compareTo === 'baseline' && (
                <span className="ml-2 text-xs text-text-tertiary">(Baseline)</span>
              )}
            </Card.Title>
            <StatusBadge status={result.status} isStale={result.is_stale} />
          </div>
        </Card.Header>
        <Card.Content>
          {viewMode === 'split' ? (
            <div className="grid grid-cols-2 gap-4">
              <div className="min-w-0">
                <div className="text-xs font-medium text-text-tertiary mb-2 flex items-center gap-1.5">
                  <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M5 3.5h6A1.5 1.5 0 0112.5 5v6a1.5 1.5 0 01-1.5 1.5H5A1.5 1.5 0 013.5 11V5A1.5 1.5 0 015 3.5zM5 2A3 3 0 002 5v6a3 3 0 003 3h6a3 3 0 003-3V5a3 3 0 00-3-3H5z"/>
                    <path d="M5 6h6v1H5V6zm0 2h6v1H5V8zm0 2h4v1H5v-1z"/>
                  </svg>
                  Logs
                </div>
                <LogsPanel result={result} maxHeight="400px" />
              </div>
              <div className="min-w-0">
                <div className="text-xs font-medium text-text-tertiary mb-2 flex items-center gap-1.5">
                  <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M3.75 1.5a.25.25 0 00-.25.25v12.5c0 .138.112.25.25.25h8.5a.25.25 0 00.25-.25V4.664a.25.25 0 00-.073-.177l-2.914-2.914a.25.25 0 00-.177-.073H3.75zM2 1.75C2 .784 2.784 0 3.75 0h5.586c.464 0 .909.184 1.237.513l2.914 2.914c.329.328.513.773.513 1.237v9.586A1.75 1.75 0 0112.25 16h-8.5A1.75 1.75 0 012 14.25V1.75z"/>
                  </svg>
                  Files
                </div>
                <FilesPanel patch={patch} />
              </div>
            </div>
          ) : viewMode === 'logs' ? (
            <LogsPanel result={result} maxHeight="600px" />
          ) : (
            <FilesPanel patch={patch} />
          )}
        </Card.Content>
      </Card>
    )
  }

  // Render executor-grouped view (default)
  const renderExecutorGrouped = () => {
    // Filter out baseline when comparing to baseline
    const displayResults = compareTo === 'baseline' && baselineId
      ? results.filter((result) => result.id !== baselineId)
      : results
    
    return (
      <div className="space-y-6">
        {displayResults.map((result) => {
          const idx = results.findIndex((r) => r.id === result.id)
          const patch = displayPatches[idx] || ''
          const isBaseline = baselineId === result.id

          return (
            <ResultCard
              key={result.id}
              result={result}
              patch={patch}
              isBaseline={isBaseline}
            />
          )
        })}
      </div>
    )
  }

  // File card component for file-grouped view
  function FileGroupedCard({ 
    filePath, 
    fileResults 
  }: { 
    filePath: string
    fileResults: Array<{ result: Result; patch: string; fileContent: string }>
  }) {
    const [selectedExecutor, setSelectedExecutor] = useState<string | null>(
      fileResults.length > 0 ? `${fileResults[0].result.harness}:${fileResults[0].result.provider}:${fileResults[0].result.model}` : null
    )

    const selectedResult = fileResults.find(
      (fr) => `${fr.result.harness}:${fr.result.provider}:${fr.result.model}` === selectedExecutor
    ) || fileResults[0]

    return (
      <Card>
        <Card.Header>
          <div className="flex items-center justify-between">
            <Card.Title className="font-mono text-sm">{filePath}</Card.Title>
            {fileResults.length > 1 && (
              <div className="flex gap-2 overflow-x-auto">
                {fileResults.map((fr) => {
                  const executorKey = `${fr.result.harness}:${fr.result.provider}:${fr.result.model}`
                  const isSelected = executorKey === selectedExecutor
                  return (
                    <button
                      key={executorKey}
                      onClick={() => setSelectedExecutor(executorKey)}
                      className={`px-3 py-1.5 text-xs rounded whitespace-nowrap transition-colors ${
                        isSelected
                          ? 'bg-accent text-on-accent font-medium'
                          : 'bg-surface-2 text-text-secondary hover:bg-surface-3 hover:text-text-primary'
                      }`}
                    >
                      {fr.result.harness}:{fr.result.provider}:{fr.result.model}
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        </Card.Header>
        <Card.Content>
          {viewMode === 'split' ? (
            <div className="grid grid-cols-2 gap-4">
              <div className="min-w-0">
                <div className="text-xs font-medium text-text-tertiary mb-2 flex items-center gap-1.5">
                  <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M5 3.5h6A1.5 1.5 0 0112.5 5v6a1.5 1.5 0 01-1.5 1.5H5A1.5 1.5 0 013.5 11V5A1.5 1.5 0 015 3.5zM5 2A3 3 0 002 5v6a3 3 0 003 3h6a3 3 0 003-3V5a3 3 0 00-3-3H5z"/>
                    <path d="M5 6h6v1H5V6zm0 2h6v1H5V8zm0 2h4v1H5v-1z"/>
                  </svg>
                  Logs
                </div>
                {selectedResult && <LogsPanel result={selectedResult.result} maxHeight="400px" />}
              </div>
              <div className="min-w-0">
                <div className="text-xs font-medium text-text-tertiary mb-2 flex items-center gap-1.5">
                  <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M3.75 1.5a.25.25 0 00-.25.25v12.5c0 .138.112.25.25.25h8.5a.25.25 0 00.25-.25V4.664a.25.25 0 00-.073-.177l-2.914-2.914a.25.25 0 00-.177-.073H3.75zM2 1.75C2 .784 2.784 0 3.75 0h5.586c.464 0 .909.184 1.237.513l2.914 2.914c.329.328.513.773.513 1.237v9.586A1.75 1.75 0 0112.25 16h-8.5A1.75 1.75 0 012 14.25V1.75z"/>
                  </svg>
                  Files
                </div>
                {selectedResult ? (
                  <GitHubDiffViewer patch={selectedResult.fileContent} />
                ) : (
                  <div className="py-8 text-center text-text-tertiary">No content available</div>
                )}
              </div>
            </div>
          ) : viewMode === 'logs' ? (
            selectedResult && <LogsPanel result={selectedResult.result} maxHeight="600px" />
          ) : (
            selectedResult ? (
              <GitHubDiffViewer patch={selectedResult.fileContent} />
            ) : (
              <div className="py-8 text-center text-text-tertiary">No content available</div>
            )
          )}
        </Card.Content>
      </Card>
    )
  }

  // Render file-grouped view
  const renderFileGrouped = () => {
    const files = Array.from(filesByPath.keys()).sort()
    
    if (files.length === 0) {
      return (
        <div className="py-8 text-center text-text-tertiary">No files changed</div>
      )
    }

    return (
      <div className="space-y-6">
        {files.map((filePath) => (
          <FileGroupedCard
            key={filePath}
            filePath={filePath}
            fileResults={filesByPath.get(filePath) || []}
          />
        ))}
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        breadcrumbs={breadcrumbs}
        title="Compare Results"
        description={`Comparing ${ids.length} results side by side`}
      />

      {/* Comparison Table + Time vs Score Chart */}
      <div className="flex flex-col xl:flex-row gap-6 mb-6">
        <div className="flex-1 min-w-0">
          <ComparisonTable 
            results={
              compareTo === 'baseline' && baselineId
                ? results.filter((result) => result.id !== baselineId)
                : results
            }
            judgementsByResult={judgementsByResult} 
          />
        </div>
        
        {/* Time vs Score Scatter Plot */}
        <Card className="xl:w-[420px] shrink-0">
          <Card.Header>
            <Card.Title className="text-sm">Time vs Quality</Card.Title>
          </Card.Header>
          <Card.Content className="py-2 overflow-x-auto">
            <TimeVsScoreChart
              results={
                compareTo === 'baseline' && baselineId
                  ? results.filter((result) => result.id !== baselineId)
                  : results
              }
              judgementsByResult={judgementsByResult}
              onPointClick={(resultId) => navigate(`/result/${resultId}`)}
            />
          </Card.Content>
        </Card>
      </div>

      {/* View Controls */}
      <Card className="mb-6">
        <Card.Content>
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-6 flex-wrap">
              <div className="flex items-center gap-3">
                <Select
                  label="Group by"
                  value={groupBy}
                  onChange={(e) => setGroupBy(e.target.value as 'executor' | 'file')}
                  className="w-40"
                  options={[
                    { value: 'executor', label: 'Executor' },
                    { value: 'file', label: 'File' },
                  ]}
                />
              </div>
              <div className="flex items-center gap-3">
                <Select
                  label="Compare to"
                  value={compareTo}
                  onChange={(e) => setCompareTo(e.target.value as 'parent' | 'baseline')}
                  className="w-40"
                  options={[
                    { value: 'parent', label: 'Parent' },
                    { value: 'baseline', label: 'Baseline' },
                  ]}
                />
              </div>
              {compareTo === 'baseline' && (
                <div className="flex items-center gap-3">
                  <Select
                    label="Baseline"
                    value={baselineId?.toString() || (ids.length > 0 ? ids[0].toString() : '')}
                    onChange={(e) => setBaselineId(e.target.value ? Number(e.target.value) : null)}
                    className="w-64"
                    options={results.map((result) => ({
                      value: result.id.toString(),
                      label: `${result.harness}:${result.provider}:${result.model} (Result ${result.id})`,
                    }))}
                  />
                </div>
              )}
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-text-tertiary">View</label>
              <ViewModeSwitcher value={viewMode} onChange={setViewMode} />
            </div>
          </div>
        </Card.Content>
      </Card>

      {/* Diffs */}
      {groupBy === 'file' ? renderFileGrouped() : renderExecutorGrouped()}
    </div>
  )
}
