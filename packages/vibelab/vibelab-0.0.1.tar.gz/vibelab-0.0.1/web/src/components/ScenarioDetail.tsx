import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, useMemo } from 'react'
import { getScenario, deleteScenario, rerunResult, listJudges, listScenarioJudgements, judgeResult, Result } from '../api'
import { PageHeader, Card, Table, StatusBadge, Button, Checkbox, ConfirmDialog, EmptyState, DropdownMenu, DropdownItem, OverflowMenuTrigger, QualityBadge } from './ui'
import JudgeForm from './JudgeForm'

// Quality color mapping
function getQualityColor(quality: number | null | undefined): string {
  if (quality === null || quality === undefined) return '#6b7280' // text-tertiary gray
  if (quality >= 3.5) return '#34d399' // emerald
  if (quality >= 2.5) return '#38bdf8' // sky
  if (quality >= 1.5) return '#fbbf24' // amber
  return '#f87171' // rose
}

// Scatter Plot component for time vs score tradeoff
interface ScatterPlotProps {
  results: Result[]
  judgementsByResultId: Map<number, any>
  onPointClick?: (resultId: number) => void
}

function TimeVsScoreChart({ results, judgementsByResultId, onPointClick }: ScatterPlotProps) {
  const [hoveredPoint, setHoveredPoint] = useState<number | null>(null)
  
  // Collect data points (completed results with duration and quality)
  const dataPoints = useMemo(() => {
    return results
      .filter(r => r.status === 'completed' && r.duration_ms != null)
      .map(r => {
        // Get quality score - prefer human, fall back to judge
        let quality = r.quality
        if (quality === null || quality === undefined) {
          const judgement = judgementsByResultId.get(r.id)
          quality = judgement?.quality ?? null
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
  }, [results, judgementsByResultId])

  if (dataPoints.length === 0) {
    return (
      <div className="flex items-center justify-center h-[200px] text-text-tertiary text-sm">
        No completed results with quality scores yet
      </div>
    )
  }

  // Chart dimensions
  const width = 400
  const height = 200
  const padding = { top: 20, right: 20, bottom: 40, left: 50 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom

  // Calculate scales
  const durations = dataPoints.map(p => p.duration)
  const minDuration = Math.min(...durations)
  const maxDuration = Math.max(...durations)
  const durationRange = maxDuration - minDuration || 1

  // X scale: duration (log scale would be better for large ranges, but linear is fine for now)
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
              y={height - padding.bottom + 16}
              textAnchor="middle"
              className="text-[10px] fill-text-tertiary"
            >
              {formatDuration(tick)}
            </text>
          </g>
        ))}
        <text
          x={padding.left + chartWidth / 2}
          y={height - 4}
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

export default function ScenarioDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedResults, setSelectedResults] = useState<Set<number>>(new Set())
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showJudgeDialog, setShowJudgeDialog] = useState(false)
  const [activeTab, setActiveTab] = useState<'details' | 'judge'>('details')
  
  const { data, isLoading } = useQuery({
    queryKey: ['scenario', id],
    queryFn: () => getScenario(Number(id!)),
    refetchInterval: (query) => {
      const data = query.state.data
      if (data && data.results.some((r: any) => r.status === 'running' || r.status === 'queued')) {
        return 3000
      }
      return false
    },
  })

  // Get judge for this scenario
  const { data: judges } = useQuery({
    queryKey: ['judges', id],
    queryFn: () => listJudges(Number(id!)),
  })
  const latestJudge = judges?.[0]

  // Get all judgements for this scenario (from all judges)
  const { data: allJudgements } = useQuery({
    queryKey: ['scenario-judgements', id],
    queryFn: () => listScenarioJudgements(Number(id!)),
    enabled: !!id,
  })

  // Create a map of result_id -> latest judgement for quick lookup
  // Prefer judgements from the latest judge, but show any judgement
  const judgementsByResultId = useMemo(() => {
    if (!allJudgements) return new Map()
    const map = new Map()
    // Sort by is_latest_judge first, then by created_at desc
    const sorted = [...allJudgements].sort((a, b) => {
      if (a.is_latest_judge && !b.is_latest_judge) return -1
      if (!a.is_latest_judge && b.is_latest_judge) return 1
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    })
    // Use the first (best) judgement for each result
    sorted.forEach((j: any) => {
      if (!map.has(j.result_id)) {
        map.set(j.result_id, j)
      }
    })
    return map
  }, [allJudgements])

  // Get judgements count for latest judge (for display in judge tab)
  const latestJudgeJudgements = useMemo(() => {
    if (!allJudgements || !latestJudge) return []
    return allJudgements.filter((j: any) => j.judge_id === latestJudge.id)
  }, [allJudgements, latestJudge])

  // Get outdated judgements (judgements from older judge versions) for completed results
  const outdatedJudgements = useMemo(() => {
    if (!allJudgements || !latestJudge || !data?.results) return []
    const completedResultIds = new Set(
      data.results.filter(r => r.status === 'completed').map(r => r.id)
    )
    // Find results that have judgements but NOT from the latest judge
    const resultsWithLatestJudge = new Set(
      allJudgements.filter((j: any) => j.judge_id === latestJudge.id).map((j: any) => j.result_id)
    )
    // Get unique outdated result IDs (completed results with judgements but not from latest judge)
    const outdatedResultIds: number[] = []
    allJudgements.forEach((j: any) => {
      if (
        completedResultIds.has(j.result_id) &&
        !resultsWithLatestJudge.has(j.result_id) &&
        !outdatedResultIds.includes(j.result_id)
      ) {
        outdatedResultIds.push(j.result_id)
      }
    })
    return outdatedResultIds
  }, [allJudgements, latestJudge, data?.results])

  // State for batch re-judging
  const [isRejudging, setIsRejudging] = useState(false)
  const [rejudgeProgress, setRejudgeProgress] = useState<{ current: number; total: number } | null>(null)

  const deleteMutation = useMutation({
    mutationFn: () => deleteScenario(Number(id!)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
      navigate('/scenarios')
    },
  })

  const rerunMutation = useMutation({
    mutationFn: (resultId: number) => rerunResult(resultId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['results'] })
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
    },
  })

  const judgeResultMutation = useMutation({
    mutationFn: ({ resultId }: { resultId: number }) => {
      if (!latestJudge) throw new Error('No judge available')
      return judgeResult(latestJudge.id, resultId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenario-judgements', id] })
      queryClient.invalidateQueries({ queryKey: ['judgements', 'all'] })
      queryClient.invalidateQueries({ queryKey: ['results'] })
    },
  })

  // Re-judge all outdated judgements
  const handleRejudgeAllOutdated = async () => {
    if (!latestJudge || outdatedJudgements.length === 0) return

    setIsRejudging(true)
    setRejudgeProgress({ current: 0, total: outdatedJudgements.length })

    try {
      for (let i = 0; i < outdatedJudgements.length; i++) {
        const resultId = outdatedJudgements[i]
        setRejudgeProgress({ current: i + 1, total: outdatedJudgements.length })
        await judgeResult(latestJudge.id, resultId)
      }
      
      // Invalidate queries after all done
      queryClient.invalidateQueries({ queryKey: ['scenario-judgements', id] })
      queryClient.invalidateQueries({ queryKey: ['judgements', 'all'] })
      queryClient.invalidateQueries({ queryKey: ['results'] })
    } catch (error) {
      console.error('Failed to re-judge:', error)
      alert(`Failed to re-judge: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsRejudging(false)
      setRejudgeProgress(null)
    }
  }

  const runningCount = useMemo(() => {
    if (!data?.results) return 0
    return data.results.filter(r => r.status === 'running' || r.status === 'queued').length
  }, [data?.results])

  if (isLoading) {
    return (
      <div>
        <PageHeader
          breadcrumbs={[{ label: 'Scenarios', path: '/scenarios' }, { label: `Scenario ${id}` }]}
          title={`Scenario ${id}`}
        />
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div>
        <PageHeader
          breadcrumbs={[{ label: 'Scenarios', path: '/scenarios' }, { label: 'Not Found' }]}
          title="Scenario Not Found"
        />
        <EmptyState title="Scenario not found" description="The scenario you're looking for doesn't exist." />
      </div>
    )
  }

  const { scenario, results } = data

  const toggleResult = (resultId: number) => {
    const newSelected = new Set(selectedResults)
    if (newSelected.has(resultId)) {
      newSelected.delete(resultId)
    } else {
      newSelected.add(resultId)
    }
    setSelectedResults(newSelected)
  }

  const toggleAll = () => {
    if (selectedResults.size === results.length) {
      setSelectedResults(new Set())
    } else {
      setSelectedResults(new Set(results.map(r => r.id)))
    }
  }

  const handleCompare = () => {
    if (selectedResults.size >= 2) {
      const ids = Array.from(selectedResults).join(',')
      navigate(`/compare?ids=${ids}&scenario=${scenario.id}`)
    }
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div>
      <PageHeader
        breadcrumbs={[
          { label: 'Scenarios', path: '/scenarios' },
          { label: `Scenario ${scenario.id}` },
        ]}
        title={`Scenario ${scenario.id}`}
        actions={
          <>
            <Button variant="ghost" onClick={() => setShowJudgeDialog(true)}>
              {latestJudge ? 'Update Judge' : 'Create Judge'}
            </Button>
            <Link to={`/run/create?scenario=${scenario.id}`}>
              <Button>New Run</Button>
            </Link>
            <DropdownMenu trigger={<OverflowMenuTrigger />}>
              <DropdownItem danger onClick={() => setShowDeleteDialog(true)}>
                Delete scenario
              </DropdownItem>
            </DropdownMenu>
          </>
        }
      />

      {/* Scenario Details with Tabs */}
      <Card className="mb-6">
        <Card.Header>
          <div className="flex items-center gap-2 border-b border-border -mx-6 -mt-6 mb-6 px-6 pt-6">
            <button
              onClick={() => setActiveTab('details')}
              className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 ${
                activeTab === 'details'
                  ? 'border-accent text-text-primary'
                  : 'border-transparent text-text-tertiary hover:text-text-secondary'
              }`}
            >
              Details
            </button>
            {latestJudge && (
              <button
                onClick={() => setActiveTab('judge')}
                className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 ${
                  activeTab === 'judge'
                    ? 'border-accent text-text-primary'
                    : 'border-transparent text-text-tertiary hover:text-text-secondary'
                }`}
              >
                Judge
              </button>
            )}
            {!latestJudge && (
              <button
                onClick={() => {
                  setActiveTab('judge')
                  setShowJudgeDialog(true)
                }}
                className="px-4 py-2 text-sm font-medium transition-colors border-b-2 border-transparent text-text-tertiary hover:text-text-secondary"
              >
                Judge (Create)
              </button>
            )}
          </div>
        </Card.Header>
        <Card.Content>
          {activeTab === 'details' && (
            <>
              <div className="mb-4">
                <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-wide mb-2">Prompt</h3>
                <p className="text-text-primary whitespace-pre-wrap text-sm">{scenario.prompt}</p>
              </div>
              
              <div className="border-t border-border pt-4">
                <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-wide mb-3">Code Reference</h3>
                <dl className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  <div>
                    <dt className="text-text-tertiary inline">Type:</dt>
                    <dd className="inline ml-2 text-text-primary font-medium capitalize">{scenario.code_type}</dd>
                  </div>
                  
                  {scenario.code_ref && scenario.code_type === 'github' && scenario.code_ref.owner && (
                    <>
                      <div>
                        <dt className="text-text-tertiary inline">Repository:</dt>
                        <dd className="inline ml-2">
                          <a
                            href={`https://github.com/${scenario.code_ref.owner}/${scenario.code_ref.repo}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-accent hover:text-accent-hover"
                          >
                            {scenario.code_ref.owner}/{scenario.code_ref.repo}
                          </a>
                        </dd>
                      </div>
                      <div>
                        <dt className="text-text-tertiary inline">Commit:</dt>
                        <dd className="inline ml-2 font-mono text-xs text-text-secondary">
                          {scenario.code_ref.commit_sha?.substring(0, 7) || scenario.code_ref.branch || 'main'}
                        </dd>
                      </div>
                    </>
                  )}
                  
                  {scenario.code_ref && scenario.code_type === 'local' && scenario.code_ref.path && (
                    <div>
                      <dt className="text-text-tertiary inline">Path:</dt>
                      <dd className="inline ml-2 font-mono text-xs text-text-secondary">{scenario.code_ref.path}</dd>
                    </div>
                  )}
                  
                  <div>
                    <dt className="text-text-tertiary inline">Created:</dt>
                    <dd className="inline ml-2 text-text-secondary">{formatDate(scenario.created_at)}</dd>
                  </div>
                </dl>
              </div>
            </>
          )}

          {activeTab === 'judge' && (
            <>
              {latestJudge ? (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-semibold text-text-primary mb-1">LLM Judge</h3>
                      <p className="text-xs text-text-tertiary">Automated quality assessment for this scenario</p>
                    </div>
                    <div className="flex gap-2">
                      {/* Note: Judgements are triggered one at a time from individual results */}
                      <Button variant="ghost" size="sm" onClick={() => setShowJudgeDialog(true)}>
                        Update
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <div className="text-text-tertiary text-xs mb-1">Alignment Score</div>
                      <div className="text-lg font-semibold text-text-primary">
                        {latestJudge.alignment_score !== null && latestJudge.alignment_score !== undefined
                          ? latestJudge.alignment_score.toFixed(3)
                          : 'Not trained'}
                      </div>
                    </div>
                    <div>
                      <div className="text-text-tertiary text-xs mb-1">Training Samples</div>
                      <div className="text-text-primary font-medium">{latestJudge.training_sample_ids.length}</div>
                    </div>
                    <div>
                      <div className="text-text-tertiary text-xs mb-1">Test Samples</div>
                      <div className="text-text-primary font-medium">{latestJudge.test_sample_ids.length}</div>
                    </div>
                  </div>

                  {latestJudge.guidance && (
                    <div className="pt-4 border-t border-border">
                      <div className="text-text-tertiary text-xs uppercase tracking-wide mb-2">Guidance</div>
                      <p className="text-text-secondary text-sm whitespace-pre-wrap">{latestJudge.guidance}</p>
                    </div>
                  )}

                  {latestJudgeJudgements && latestJudgeJudgements.length > 0 && (
                    <div className="pt-4 border-t border-border">
                      <div className="text-text-tertiary text-xs uppercase tracking-wide mb-2">Judgements Made</div>
                      <div className="text-text-primary font-medium">{latestJudgeJudgements.length} of {results.filter(r => r.status === 'completed').length} completed results</div>
                      {allJudgements && allJudgements.length > latestJudgeJudgements.length && (
                        <div className="text-text-tertiary text-xs mt-1">
                          ({allJudgements.length - latestJudgeJudgements.length} from older judge versions)
                        </div>
                      )}
                    </div>
                  )}

                  {/* Re-judge outdated section */}
                  {outdatedJudgements.length > 0 && (
                    <div className="pt-4 border-t border-border">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-status-warning text-xs uppercase tracking-wide mb-1 flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-status-warning" />
                            Outdated Judgements
                          </div>
                          <div className="text-text-secondary text-sm">
                            {outdatedJudgements.length} result{outdatedJudgements.length !== 1 ? 's have' : ' has'} judgements from older judge versions
                          </div>
                        </div>
                        <Button
                          size="sm"
                          onClick={handleRejudgeAllOutdated}
                          disabled={isRejudging}
                        >
                          {isRejudging && rejudgeProgress
                            ? `Re-judging ${rejudgeProgress.current}/${rejudgeProgress.total}...`
                            : `Re-judge All (${outdatedJudgements.length})`}
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-text-secondary mb-4">No judge configured for this scenario</p>
                  <Button onClick={() => setShowJudgeDialog(true)}>Create Judge</Button>
                </div>
              )}
            </>
          )}
        </Card.Content>
      </Card>

      {/* Time vs Score Chart */}
      {results.some(r => r.status === 'completed' && r.duration_ms != null) && (
        <Card className="mb-6">
          <Card.Header>
            <Card.Title>Time vs Quality Tradeoff</Card.Title>
          </Card.Header>
          <Card.Content>
            <TimeVsScoreChart
              results={results}
              judgementsByResultId={judgementsByResultId}
              onPointClick={(resultId) => navigate(`/result/${resultId}`)}
            />
          </Card.Content>
        </Card>
      )}

      {/* Results Section */}
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold text-text-primary">Results ({results.length})</h2>
          {runningCount > 0 && (
            <div className="flex items-center gap-2 px-2.5 py-1 bg-accent-muted rounded-full">
              <div className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
              <span className="text-xs text-accent font-medium">{runningCount} running</span>
            </div>
          )}
        </div>
        <Button 
          onClick={handleCompare}
          disabled={selectedResults.size < 2}
        >
          Compare{selectedResults.size > 0 ? ` (${selectedResults.size})` : ''}
        </Button>
      </div>

      {results.length === 0 ? (
        <EmptyState
          title="No results yet"
          description="Run this scenario with different executors to see results."
          action={
            <Link to={`/run/create?scenario=${scenario.id}`}>
              <Button>Run Scenario</Button>
            </Link>
          }
        />
      ) : (
        <Table>
          <Table.Header>
            <tr>
              <Table.Head className="w-10">
                <Checkbox
                  checked={selectedResults.size === results.length && results.length > 0}
                  onChange={toggleAll}
                />
              </Table.Head>
              <Table.Head>Executor</Table.Head>
              <Table.Head>Driver</Table.Head>
              <Table.Head>Status</Table.Head>
              <Table.Head>Human Quality</Table.Head>
              {latestJudge && <Table.Head>Judge Quality</Table.Head>}
              <Table.Head>Duration</Table.Head>
              <Table.Head>Changes</Table.Head>
              <Table.Head>Files</Table.Head>
              <Table.Head>Cost</Table.Head>
              <Table.Head>Finished</Table.Head>
              <Table.Head></Table.Head>
            </tr>
          </Table.Header>
          <Table.Body>
            {results.map((result) => (
              <Table.Row 
                key={result.id} 
                selected={selectedResults.has(result.id)}
                className="cursor-pointer"
                onClick={() => navigate(`/result/${result.id}`)}
              >
                <Table.Cell>
                  <div onClick={(e) => e.stopPropagation()}>
                    <Checkbox
                      checked={selectedResults.has(result.id)}
                      onChange={() => toggleResult(result.id)}
                    />
                  </div>
                </Table.Cell>
                <Table.Cell mono className="text-text-secondary text-xs">
                  {result.harness}:{result.provider}:{result.model}
                </Table.Cell>
                <Table.Cell className="text-text-tertiary text-xs">
                  {result.driver || 'local'}
                </Table.Cell>
                <Table.Cell>
                  <div className="flex items-center gap-2">
                    {(result.status === 'running' || result.status === 'queued') && (
                      <div className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
                    )}
                    <StatusBadge status={result.status} isStale={result.is_stale} />
                  </div>
                </Table.Cell>
                <Table.Cell>
                  <QualityBadge quality={result.quality as 1|2|3|4|null} />
                </Table.Cell>
                {judges && judges.length > 0 && (
                  <Table.Cell>
                    {judgementsByResultId.has(result.id) ? (
                      (() => {
                        const judgement = judgementsByResultId.get(result.id)
                        const isOutdated = !judgement.is_latest_judge
                        return (
                          <div className="flex items-center gap-2">
                            <QualityBadge quality={judgement.quality as 1|2|3|4|null} />
                            {isOutdated && latestJudge && (
                              <button
                                className="text-xs text-status-warning hover:text-status-warning/80"
                                      title="Re-run with latest judge"
                                      onClick={(e) => {
                                        e.stopPropagation()
                                        judgeResultMutation.mutate({ resultId: result.id })
                                      }}
                                disabled={judgeResultMutation.isPending}
                              >
                                ↻
                              </button>
                            )}
                          </div>
                        )
                      })()
                    ) : (
                      <span className="text-text-disabled text-sm">—</span>
                    )}
                  </Table.Cell>
                )}
                <Table.Cell className="text-text-tertiary text-sm">
                  {result.duration_ms ? `${(result.duration_ms / 1000).toFixed(1)}s` : '—'}
                </Table.Cell>
                <Table.Cell className="text-sm">
                  {result.lines_added !== null && result.lines_removed !== null ? (
                    <span>
                      <span className="text-status-success">+{result.lines_added}</span>
                      <span className="text-text-tertiary">/</span>
                      <span className="text-status-error">-{result.lines_removed}</span>
                    </span>
                  ) : (
                    <span className="text-text-disabled">—</span>
                  )}
                </Table.Cell>
                <Table.Cell className="text-text-tertiary text-sm">
                  {typeof result.files_changed === 'number' ? result.files_changed : '—'}
                </Table.Cell>
                <Table.Cell className="text-text-tertiary text-sm">
                  {result.cost_usd ? `$${result.cost_usd.toFixed(4)}` : '—'}
                </Table.Cell>
                <Table.Cell className="text-text-tertiary text-xs">
                  {result.finished_at ? formatDate(result.finished_at) : '—'}
                </Table.Cell>
                <Table.Cell>
                  <div 
                    className="flex items-center justify-end"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <DropdownMenu trigger={<OverflowMenuTrigger />}>
                      <DropdownItem
                        onClick={() => rerunMutation.mutate(result.id)}
                        disabled={rerunMutation.isPending}
                      >
                        Rerun
                      </DropdownItem>
                    </DropdownMenu>
                  </div>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      )}

      <JudgeForm
        scenarioId={scenario.id}
        results={results}
        open={showJudgeDialog}
        onClose={() => setShowJudgeDialog(false)}
      />

      <ConfirmDialog
        open={showDeleteDialog}
        onClose={() => setShowDeleteDialog(false)}
        onConfirm={() => {
          deleteMutation.mutate()
          setShowDeleteDialog(false)
        }}
        title="Delete Scenario"
        description={`Are you sure you want to delete scenario ${scenario.id}? This will permanently delete the scenario and all ${results.length} associated results.`}
        confirmLabel="Delete"
        danger
        loading={deleteMutation.isPending}
      />
    </div>
  )
}
