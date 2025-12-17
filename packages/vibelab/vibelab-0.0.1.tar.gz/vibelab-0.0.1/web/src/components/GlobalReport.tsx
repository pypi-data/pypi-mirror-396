import { Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getGlobalAnalytics, listPendingJudgements, judgeResult, createRun } from '../api'
import { PageHeader, Card, EmptyState, Button } from './ui'
import { useMemo, useState } from 'react'
import {
  CellData,
  MatrixRow,
  MatrixQualityBadge,
  MatrixCellContent,
  ScenarioRowTitle,
  computeAggregations,
  computeStats,
  formatDuration,
  MatrixLegend,
} from './AnalyticsMatrix'

export default function GlobalReport() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [judgingResultIds, setJudgingResultIds] = useState<Set<number>>(new Set())

  const { data, isLoading } = useQuery({
    queryKey: ['global-analytics'],
    queryFn: getGlobalAnalytics,
    refetchInterval: (query) => {
      const d = query.state.data
      if (d?.matrix.some((row: MatrixRow) =>
        Object.values(row.cells).some((cell) => cell.status === 'running' || cell.status === 'queued')
      )) {
        return 3000
      }
      return judgingResultIds.size > 0 ? 2000 : false
    },
  })

  const { data: pendingJudgements } = useQuery({
    queryKey: ['judgements', 'pending'],
    queryFn: listPendingJudgements,
    refetchInterval: judgingResultIds.size > 0 ? 2000 : 10000,
  })

  const runMutation = useMutation({
    mutationFn: (params: { scenario_id: number; executor_spec: string }) => createRun(params),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['global-analytics'] }),
  })

  const runJudge = async (judgeId: number, resultId: number) => {
    setJudgingResultIds(prev => new Set(prev).add(resultId))
    try {
      await judgeResult(judgeId, resultId)
      queryClient.invalidateQueries({ queryKey: ['judgements'] })
      queryClient.invalidateQueries({ queryKey: ['global-analytics'] })
    } catch (e) {
      console.error(`Failed to judge result ${resultId}:`, e)
    } finally {
      setJudgingResultIds(prev => { const n = new Set(prev); n.delete(resultId); return n })
    }
  }

  const runAllJudges = () => {
    pendingJudgements?.forEach((item: any) => {
      if (!judgingResultIds.has(item.result.id)) runJudge(item.judge.id, item.result.id)
    })
  }

  // Aggregations
  const agg = useMemo(() => {
    if (!data) return { 
      global: { quality: { avg: null, count: 0 }, duration: { avg: null, count: 0 } },
      byScenario: {},
      byExecutor: {}
    }
    return computeAggregations(data.matrix, data.executors)
  }, [data])

  const stats = useMemo(() => {
    if (!data) return { completed: 0, failed: 0, running: 0, pendingJudges: 0 }
    const base = computeStats(data.matrix)
    return { ...base, pendingJudges: pendingJudgements?.length || 0 }
  }, [data, pendingJudgements])

  const breadcrumbs = [{ label: 'Global Report' }]

  if (isLoading) {
    return (
      <div>
        <PageHeader breadcrumbs={breadcrumbs} title="Global Report" />
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div>
        <PageHeader breadcrumbs={breadcrumbs} title="Global Report" />
        <EmptyState title="No data" description="Could not load global analytics." />
      </div>
    )
  }

  const { executors, matrix } = data

  if (matrix.length === 0) {
    return (
      <div>
        <PageHeader breadcrumbs={breadcrumbs} title="Global Report" />
        <EmptyState
          title="No scenarios yet"
          description="Create scenarios and run them to see the global report."
          action={<Link to="/run/create"><Button>Create Run</Button></Link>}
        />
      </div>
    )
  }

  const handleCellClick = (cell: CellData, e: React.MouseEvent) => {
    e.stopPropagation()
    if (cell.result_ids?.length === 1) navigate(`/result/${cell.result_ids[0]}`)
    else if (cell.result_ids && cell.result_ids.length > 1) navigate(`/compare?ids=${cell.result_ids.join(',')}`)
  }

  const handleRowCompare = (row: MatrixRow) => {
    const ids = Object.values(row.cells).flatMap(c => c.result_ids || [])
    if (ids.length > 0) navigate(`/compare?ids=${ids.join(',')}&scenario=${row.scenario_id}`)
  }

  const handleStartRun = (scenarioId: number, executor: string, e: React.MouseEvent) => {
    e.stopPropagation()
    runMutation.mutate({ scenario_id: scenarioId, executor_spec: executor })
  }

  const isStartingRun = (scenarioId: number, executor: string) =>
    runMutation.isPending && runMutation.variables?.scenario_id === scenarioId && runMutation.variables?.executor_spec === executor

  return (
    <div>
      <PageHeader
        breadcrumbs={breadcrumbs}
        title="Global Report"
        description={`Quality matrix across all ${data.scenario_count} scenarios`}
        actions={
          <Link to="/run/create">
            <Button>New Run</Button>
          </Link>
        }
      />

      {/* Summary Bar */}
      <div className="mb-5 flex flex-wrap items-center gap-6 p-4 bg-surface border border-border rounded-lg">
        <div className="flex items-center gap-3">
          <span className="text-xs text-text-tertiary uppercase tracking-wide">Global</span>
          <MatrixQualityBadge value={agg.global.quality.avg} count={agg.global.quality.count} size="lg" />
        </div>
        <div className="flex items-center gap-5 ml-auto text-sm">
          <div><span className="text-xl font-semibold text-text-primary">{agg.global.quality.count}</span> <span className="text-text-tertiary">rated</span></div>
          {agg.global.duration.avg != null && (
            <div><span className="text-xl font-semibold text-text-secondary">{formatDuration(agg.global.duration.avg)}</span> <span className="text-text-tertiary">avg time</span></div>
          )}
          <div><span className="text-xl font-semibold text-status-success">{stats.completed}</span> <span className="text-text-tertiary">completed</span></div>
          {stats.failed > 0 && <div><span className="text-xl font-semibold text-status-error">{stats.failed}</span> <span className="text-text-tertiary">failed</span></div>}
          {stats.running > 0 && <div><span className="text-xl font-semibold text-status-info">{stats.running}</span> <span className="text-text-tertiary">running</span></div>}
        </div>
      </div>

      {/* Pending Judges */}
      {stats.pendingJudges > 0 && (
        <div className="mb-5 flex items-center justify-between p-3 bg-status-warning/10 border border-status-warning/20 rounded-lg">
          <div className="flex items-center gap-2 text-sm">
            <span className="w-2 h-2 rounded-full bg-status-warning animate-pulse" />
            <span className="text-text-primary font-medium">{stats.pendingJudges}</span>
            <span className="text-text-secondary">result{stats.pendingJudges !== 1 ? 's' : ''} awaiting judgement</span>
            {judgingResultIds.size > 0 && <span className="text-status-info ml-2">({judgingResultIds.size} running...)</span>}
          </div>
          <Button size="sm" onClick={runAllJudges} disabled={judgingResultIds.size === stats.pendingJudges}>
            {judgingResultIds.size > 0 ? `${judgingResultIds.size}/${stats.pendingJudges} judging...` : `Run All Judges`}
          </Button>
        </div>
      )}

      {/* Matrix */}
      <Card>
        <Card.Header>
          <Card.Title>
            Quality Matrix
            <span className="ml-2 text-sm font-normal text-text-tertiary">{matrix.length} scenarios × {executors.length} executors</span>
          </Card.Title>
        </Card.Header>
        <Card.Content className="p-0 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-surface-2 border-b border-border">
                <th className="sticky left-0 z-10 bg-surface-2 text-left px-4 py-2 font-medium text-text-tertiary w-[180px] min-w-[180px]">
                  Scenario
                </th>
                {executors.map((exec: string) => {
                  const model = exec.split(':')[2] || exec
                  const eq = agg.byExecutor[exec]
                  return (
                    <th key={exec} className="px-2 py-2 text-center font-medium min-w-[90px]">
                      <div className="text-xs text-text-primary truncate" title={exec}>{model}</div>
                      <div className="mt-1">
                        <MatrixQualityBadge value={eq?.quality.avg} size="sm" />
                      </div>
                      {eq?.duration.avg != null && (
                        <div className="text-[9px] text-text-tertiary mt-0.5">{formatDuration(eq.duration.avg)}</div>
                      )}
                    </th>
                  )
                })}
                <th className="px-3 py-2 text-center font-medium text-text-tertiary bg-surface-3 min-w-[80px]">
                  <div className="text-[10px] uppercase tracking-wide">Scenario</div>
                  <div className="text-[10px]">Avg</div>
                </th>
              </tr>
            </thead>
            <tbody>
              {matrix.map((row: MatrixRow) => {
                const hasResults = Object.values(row.cells).some(c => c.result_ids && c.result_ids.length > 0)
                const sq = agg.byScenario[row.scenario_id]

                return (
                  <tr key={row.scenario_id} className="border-b border-border-muted hover:bg-surface-2/50 transition-colors">
                    <td className="sticky left-0 z-10 bg-surface px-4 py-3">
                      <ScenarioRowTitle
                        scenarioId={row.scenario_id}
                        prompt={row.scenario_prompt}
                        hasResults={hasResults}
                        onCompare={() => handleRowCompare(row)}
                      />
                    </td>
                    {executors.map((exec: string) => {
                      const cell = row.cells[exec] || { status: 'pending', total: 0, completed: 0, failed: 0, timeout: 0, running: 0, queued: 0, result_ids: [] }
                      return (
                        <td key={exec} className="px-2 py-2 text-center">
                          <MatrixCellContent
                            cell={cell}
                            onCellClick={(e) => handleCellClick(cell, e)}
                            onRunClick={(e) => handleStartRun(row.scenario_id, exec, e)}
                            isStartingRun={isStartingRun(row.scenario_id, exec)}
                          />
                        </td>
                      )
                    })}
                    <td className="px-3 py-2 text-center bg-surface-3/30">
                      <MatrixQualityBadge value={sq?.quality.avg} count={sq?.quality.count} size="sm" />
                      {sq?.duration.avg != null && (
                        <div className="text-[9px] text-text-tertiary mt-0.5">{formatDuration(sq.duration.avg)}</div>
                      )}
                    </td>
                  </tr>
                )
              })}
              {/* Footer */}
              <tr className="bg-surface-3/50 border-t-2 border-border">
                <td className="sticky left-0 z-10 bg-surface-3 px-4 py-2 font-medium text-text-secondary text-xs">
                  Executor Avg
                </td>
                {executors.map((exec: string) => {
                  const eq = agg.byExecutor[exec]
                  return (
                    <td key={exec} className="px-2 py-2 text-center">
                      <MatrixQualityBadge value={eq?.quality.avg} count={eq?.quality.count} size="sm" />
                      {eq?.duration.avg != null && (
                        <div className="text-[9px] text-text-tertiary mt-0.5">{formatDuration(eq.duration.avg)}</div>
                      )}
                    </td>
                  )
                })}
                <td className="px-3 py-2 text-center bg-accent/10">
                  <div className="text-[9px] text-text-tertiary uppercase mb-0.5">Global</div>
                  <MatrixQualityBadge value={agg.global.quality.avg} count={agg.global.quality.count} size="sm" />
                  {agg.global.duration.avg != null && (
                    <div className="text-[9px] text-text-tertiary mt-0.5">{formatDuration(agg.global.duration.avg)}</div>
                  )}
                </td>
              </tr>
            </tbody>
          </table>
        </Card.Content>
      </Card>

      <MatrixLegend />
    </div>
  )
}
