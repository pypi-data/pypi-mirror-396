import { Link } from 'react-router-dom'

// Shared types for analytics matrix
export interface CellData {
  status: string
  total: number
  completed: number
  failed: number
  timeout: number
  running: number
  queued: number
  result_ids?: number[]
  avg_quality?: number | null
  quality_count?: number
  avg_duration_ms?: number | null
  duration_count?: number
}

export interface MatrixRow {
  scenario_id: number
  scenario_prompt: string
  cells: Record<string, CellData>
}

export interface Aggregations {
  global: {
    quality: { avg: number | null; count: number }
    duration: { avg: number | null; count: number }
  }
  byScenario: Record<number, {
    quality: { avg: number | null; count: number }
    duration: { avg: number | null; count: number }
  }>
  byExecutor: Record<string, {
    quality: { avg: number | null; count: number }
    duration: { avg: number | null; count: number }
  }>
}

// Quality score badge
export function MatrixQualityBadge({ 
  value, 
  count,
  size = 'md',
}: { 
  value: number | null | undefined
  count?: number
  size?: 'sm' | 'md' | 'lg'
}) {
  if (value === null || value === undefined) {
    return <span className="text-text-disabled text-xs">—</span>
  }
  
  let color = 'text-text-secondary bg-surface-2'
  let label = ''
  
  if (value >= 3.5) { color = 'text-emerald-400 bg-emerald-500/15'; label = 'Perfect' }
  else if (value >= 2.5) { color = 'text-sky-400 bg-sky-500/15'; label = 'Good' }
  else if (value >= 1.5) { color = 'text-amber-400 bg-amber-500/15'; label = 'Workable' }
  else { color = 'text-rose-400 bg-rose-500/15'; label = 'Bad' }
  
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 min-w-[52px]',
    md: 'text-sm px-2.5 py-1 min-w-[60px]',
    lg: 'text-xl px-4 py-2 min-w-[80px]',
  }
  
  return (
    <div className={`inline-flex flex-col items-center rounded-md ${color} ${sizeClasses[size]}`}>
      <span className="font-semibold">{value.toFixed(2)}</span>
      {size !== 'sm' && (
        <span className="text-[9px] opacity-70">
          {label}{count !== undefined && count > 0 ? ` (${count})` : ''}
        </span>
      )}
    </div>
  )
}

// Format duration nicely
export function formatDuration(ms: number | null | undefined): string {
  if (ms === null || ms === undefined) return '—'
  if (ms < 1000) return `${Math.round(ms)}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  const mins = Math.floor(ms / 60000)
  const secs = Math.round((ms % 60000) / 1000)
  return `${mins}m${secs}s`
}

// Compact status line
export function StatusLine({ cell }: { cell: CellData }) {
  if (cell.total === 0) return null
  
  return (
    <div className="flex flex-col items-center gap-0.5 mt-1">
      <div className="flex items-center justify-center gap-1 text-[10px] font-medium">
        {cell.running > 0 && (
          <span className="text-status-info flex items-center gap-0.5">
            <span className="w-1 h-1 rounded-full bg-current animate-pulse" />
            {cell.running}
          </span>
        )}
        {cell.completed > 0 && <span className="text-status-success">✓{cell.completed}</span>}
        {cell.failed > 0 && <span className="text-status-error">✗{cell.failed}</span>}
        {cell.timeout > 0 && <span className="text-status-warning">⏱{cell.timeout}</span>}
      </div>
      {cell.avg_duration_ms != null && (
        <div className="text-[9px] text-text-tertiary">
          {formatDuration(cell.avg_duration_ms)}
        </div>
      )}
    </div>
  )
}

// Cell content
export function MatrixCellContent({
  cell,
  onCellClick,
  onRunClick,
  isStartingRun,
}: {
  cell: CellData
  onCellClick?: (e: React.MouseEvent) => void
  onRunClick?: (e: React.MouseEvent) => void
  isStartingRun?: boolean
}) {
  if (cell.total === 0) {
    return (
      <button
        onClick={onRunClick}
        disabled={isStartingRun}
        className="text-xs text-text-tertiary hover:text-accent transition-colors disabled:opacity-50"
        title="Start a run"
      >
        {isStartingRun ? '...' : '▶ Run'}
      </button>
    )
  }

  const hasResults = cell.result_ids && cell.result_ids.length > 0

  return (
    <div
      className={`flex flex-col items-center ${hasResults ? 'cursor-pointer hover:opacity-70 transition-opacity' : ''}`}
      onClick={hasResults ? onCellClick : undefined}
    >
      <MatrixQualityBadge value={cell.avg_quality} count={cell.quality_count} size="sm" />
      <StatusLine cell={cell} />
    </div>
  )
}

// Scenario row title with compare button
export function ScenarioRowTitle({
  scenarioId,
  prompt,
  hasResults,
  onCompare,
}: {
  scenarioId: number
  prompt: string
  hasResults: boolean
  onCompare?: () => void
}) {
  return (
    <div className="flex items-start gap-1.5">
      <div className="min-w-0 flex-1">
        <Link to={`/scenario/${scenarioId}`} className="font-medium text-text-primary hover:text-accent">
          #{scenarioId}
        </Link>
        <div className="text-xs text-text-tertiary line-clamp-1 mt-0.5" title={prompt}>
          {prompt}
        </div>
      </div>
      {hasResults && onCompare && (
        <button 
          onClick={onCompare} 
          className="p-1 rounded text-text-tertiary hover:text-accent hover:bg-surface-2 transition-colors shrink-0"
          title="Compare all results"
        >
          <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
            <path d="M9.573.677L7.177 3.073a.25.25 0 000 .354l2.396 2.396a.25.25 0 00.427-.177V4.25a6.002 6.002 0 015.166 4.08.75.75 0 101.438-.432A7.503 7.503 0 0010 2.25V.854a.25.25 0 00-.427-.177zM6.427 15.323l2.396-2.396a.25.25 0 000-.354L6.427 10.177a.25.25 0 00-.427.177v1.396a6.002 6.002 0 01-5.166-4.08.75.75 0 10-1.438.432A7.503 7.503 0 006 13.75v1.396a.25.25 0 00.427.177z"/>
          </svg>
        </button>
      )}
    </div>
  )
}

// Compute aggregations from matrix data
export function computeAggregations(matrix: MatrixRow[], executors: string[]): Aggregations {
  let gQSum = 0, gQCount = 0, gDSum = 0, gDCount = 0
  const byScenario: Aggregations['byScenario'] = {}
  const byExec: Record<string, { qSum: number; qCount: number; dSum: number; dCount: number }> = {}
  executors.forEach((e) => byExec[e] = { qSum: 0, qCount: 0, dSum: 0, dCount: 0 })

  matrix.forEach((row) => {
    let sQSum = 0, sQCount = 0, sDSum = 0, sDCount = 0
    executors.forEach((exec) => {
      const c = row.cells[exec]
      // Quality aggregation
      if (c?.avg_quality != null && c.quality_count) {
        const q = c.avg_quality * c.quality_count
        gQSum += q; gQCount += c.quality_count
        sQSum += q; sQCount += c.quality_count
        byExec[exec].qSum += q; byExec[exec].qCount += c.quality_count
      }
      // Duration aggregation
      if (c?.avg_duration_ms != null && c.duration_count) {
        const d = c.avg_duration_ms * c.duration_count
        gDSum += d; gDCount += c.duration_count
        sDSum += d; sDCount += c.duration_count
        byExec[exec].dSum += d; byExec[exec].dCount += c.duration_count
      }
    })
    byScenario[row.scenario_id] = {
      quality: { avg: sQCount > 0 ? sQSum / sQCount : null, count: sQCount },
      duration: { avg: sDCount > 0 ? sDSum / sDCount : null, count: sDCount }
    }
  })

  const byExecutor: Aggregations['byExecutor'] = {}
  Object.entries(byExec).forEach(([k, v]) => {
    byExecutor[k] = {
      quality: { avg: v.qCount > 0 ? v.qSum / v.qCount : null, count: v.qCount },
      duration: { avg: v.dCount > 0 ? v.dSum / v.dCount : null, count: v.dCount }
    }
  })

  return { 
    global: { 
      quality: { avg: gQCount > 0 ? gQSum / gQCount : null, count: gQCount },
      duration: { avg: gDCount > 0 ? gDSum / gDCount : null, count: gDCount }
    }, 
    byScenario, 
    byExecutor 
  }
}

// Compute stats from matrix data
export function computeStats(matrix: MatrixRow[]): { completed: number; failed: number; running: number } {
  let completed = 0, failed = 0, running = 0
  matrix.forEach((row) => {
    Object.values(row.cells).forEach((c) => {
      completed += c.completed
      failed += c.failed + c.timeout
      running += c.running + c.queued
    })
  })
  return { completed, failed, running }
}

// Matrix legend
export function MatrixLegend() {
  return (
    <div className="mt-3 flex items-center gap-4 text-xs text-text-tertiary">
      <span className="text-emerald-400">≥3.5 Perfect</span>
      <span className="text-sky-400">≥2.5 Good</span>
      <span className="text-amber-400">≥1.5 Workable</span>
      <span className="text-rose-400">&lt;1.5 Bad</span>
      <span className="border-l border-border pl-4 text-status-success">✓ Done</span>
      <span className="text-status-error">✗ Failed</span>
      <span className="text-status-warning">⏱ Timeout</span>
    </div>
  )
}

