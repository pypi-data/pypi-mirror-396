import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { listAllJudgements, listPendingJudgements, judgeResult } from '../api'
import { PageHeader, Table, EmptyState, Card, QualityBadge, Button } from './ui'
import { useMemo, useState } from 'react'

// Stats card component
function StatsCard({ label, value, color }: { label: string; value: number | string; color: string }) {
  return (
    <div className="bg-surface border border-border rounded-lg p-4">
      <div className={`text-2xl font-semibold ${color}`}>{value}</div>
      <div className="text-xs text-text-tertiary mt-1">{label}</div>
    </div>
  )
}

// Tab button component
function TabButton({ 
  active, 
  onClick, 
  children,
  badge,
}: { 
  active: boolean
  onClick: () => void 
  children: React.ReactNode
  badge?: number
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 flex items-center gap-2 ${
        active
          ? 'border-accent text-text-primary'
          : 'border-transparent text-text-tertiary hover:text-text-secondary'
      }`}
    >
      {children}
      {badge !== undefined && badge > 0 && (
        <span className={`px-1.5 py-0.5 text-xs rounded-full ${
          active ? 'bg-accent text-on-accent' : 'bg-surface-3 text-text-secondary'
        }`}>
          {badge}
        </span>
      )}
    </button>
  )
}

export default function Judgements() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'pending' | 'completed'>('pending')
  const [runningResultIds, setRunningResultIds] = useState<Set<number>>(new Set())
  
  const { data: judgements, isLoading } = useQuery({
    queryKey: ['judgements', 'all'],
    queryFn: () => listAllJudgements(),
    refetchInterval: (query) => {
      const data = query.state.data
      const hasInProgress = data?.some((j: any) => 
        j.result && (j.result.status === 'running' || j.result.status === 'queued')
      )
      // Also poll if we have running judge requests
      return hasInProgress || runningResultIds.size > 0 ? 3000 : false
    },
  })

  const { data: pendingJudgements, isLoading: pendingLoading } = useQuery({
    queryKey: ['judgements', 'pending'],
    queryFn: () => listPendingJudgements(),
    refetchInterval: runningResultIds.size > 0 ? 2000 : 5000, // Poll faster when judging
  })

  // Non-blocking judge runner
  const runJudge = async (judgeId: number, resultId: number) => {
    // Add to running set
    setRunningResultIds(prev => new Set(prev).add(resultId))
    
    try {
      await judgeResult(judgeId, resultId)
      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['judgements'] })
    } catch (error) {
      console.error(`Failed to judge result ${resultId}:`, error)
    } finally {
      // Remove from running set
      setRunningResultIds(prev => {
        const next = new Set(prev)
        next.delete(resultId)
        return next
      })
    }
  }

  // Separate judgements into completed only
  const completedJudgements = judgements?.filter((j: any) => 
    j.result && j.result.status === 'completed'
  ) || []

  // Group completed judgements by scenario
  const completedByScenario = useMemo(() => {
    const map = new Map<number, any[]>()
    
    completedJudgements.forEach((j: any) => {
      const scenarioId = j.result?.scenario_id
      if (!scenarioId) return
      
      if (!map.has(scenarioId)) {
        map.set(scenarioId, [])
      }
      map.get(scenarioId)!.push(j)
    })
    
    return Array.from(map.entries())
      .sort((a, b) => a[0] - b[0])
      .map(([scenarioId, judgements]) => ({ scenarioId, judgements }))
  }, [completedJudgements])

  // Group pending by scenario
  const pendingByScenario = useMemo(() => {
    const map = new Map<number, any[]>()
    
    pendingJudgements?.forEach((item: any) => {
      const scenarioId = item.result?.scenario_id
      if (!scenarioId) return
      
      if (!map.has(scenarioId)) {
        map.set(scenarioId, [])
      }
      map.get(scenarioId)!.push(item)
    })
    
    return Array.from(map.entries())
      .sort((a, b) => a[0] - b[0])
      .map(([scenarioId, items]) => ({ scenarioId, items }))
  }, [pendingJudgements])

  // Compute aggregate stats
  const stats = useMemo(() => {
    const total = completedJudgements.length
    const byQuality = { 4: 0, 3: 0, 2: 0, 1: 0, unrated: 0 }
    let alignedCount = 0
    
    completedJudgements.forEach((j: any) => {
      if (j.quality === null || j.quality === undefined) {
        byQuality.unrated++
      } else {
        byQuality[j.quality as 1|2|3|4]++
      }
      
      if (j.quality !== null && j.result?.quality !== null && j.quality === j.result.quality) {
        alignedCount++
      }
    })

    const alignmentRate = total > 0 ? ((alignedCount / total) * 100).toFixed(1) : '0'
    
    return { 
      total, 
      byQuality, 
      alignedCount, 
      alignmentRate, 
      pending: pendingJudgements?.length || 0,
      scenarioCount: completedByScenario.length,
    }
  }, [completedJudgements, pendingJudgements, completedByScenario])

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (isLoading || pendingLoading) {
    return (
      <div>
        <PageHeader
          breadcrumbs={[{ label: 'Judgements' }]}
          title="Judgements"
        />
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        breadcrumbs={[{ label: 'Judgements' }]}
        title="Judgements"
        description="LLM judge assessments across all scenarios"
      />

      {/* Stats Overview */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-4 mb-6">
        <StatsCard label="Scenarios" value={stats.scenarioCount} color="text-text-primary" />
        <StatsCard label="Completed" value={stats.total} color="text-text-primary" />
        <StatsCard label="Perfect (4)" value={stats.byQuality[4]} color="text-emerald-500" />
        <StatsCard label="Good (3)" value={stats.byQuality[3]} color="text-sky-500" />
        <StatsCard label="Workable (2)" value={stats.byQuality[2]} color="text-amber-500" />
        <StatsCard label="Bad (1)" value={stats.byQuality[1]} color="text-rose-500" />
        <StatsCard label="Alignment" value={`${stats.alignmentRate}%`} color="text-accent" />
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 border-b border-border mb-6">
        <TabButton 
          active={activeTab === 'pending'} 
          onClick={() => setActiveTab('pending')}
          badge={stats.pending}
        >
          Pending
        </TabButton>
        <TabButton 
          active={activeTab === 'completed'} 
          onClick={() => setActiveTab('completed')}
          badge={stats.total}
        >
          Completed
        </TabButton>
      </div>

      {/* Pending Tab */}
      {activeTab === 'pending' && (
        <>
          {pendingByScenario.length === 0 ? (
            <EmptyState
              title="No pending judgements"
              description="All completed results have been judged, or no judges are configured yet."
              action={
                <Link to="/scenarios">
                  <Button>View Scenarios</Button>
                </Link>
              }
            />
          ) : (
            <div className="space-y-4">
              {pendingByScenario.map(({ scenarioId, items }) => {
                const scenarioRunningCount = items.filter((i: any) => runningResultIds.has(i.result.id)).length
                const allRunning = scenarioRunningCount === items.length
                
                return (
                <Card key={scenarioId}>
                  <Card.Header>
                    <div className="flex items-center justify-between">
                      <Link 
                        to={`/scenario/${scenarioId}`}
                        className="text-base font-semibold text-text-primary hover:text-accent transition-colors"
                      >
                        Scenario #{scenarioId}
                      </Link>
                      <div className="flex items-center gap-3">
                        <span className="text-sm text-text-tertiary">
                          {scenarioRunningCount > 0 
                            ? `${scenarioRunningCount}/${items.length} judging...` 
                            : `${items.length} pending`}
                        </span>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => {
                            items.forEach((item: any) => {
                              if (!runningResultIds.has(item.result.id)) {
                                runJudge(item.judge.id, item.result.id)
                              }
                            })
                          }}
                          disabled={allRunning}
                        >
                          {allRunning ? 'Judging All...' : 'Run All'}
                        </Button>
                      </div>
                    </div>
                  </Card.Header>
                  <Card.Content className="p-0">
                    <Table>
                      <Table.Header>
                        <tr>
                          <Table.Head>Result</Table.Head>
                          <Table.Head>Executor</Table.Head>
                          <Table.Head>Human Quality</Table.Head>
                          <Table.Head>Judge</Table.Head>
                          <Table.Head></Table.Head>
                        </tr>
                      </Table.Header>
                      <Table.Body>
                        {items.map((item: any) => (
                          <Table.Row
                            key={`pending-${item.result.id}`}
                            className="cursor-pointer"
                            onClick={() => navigate(`/result/${item.result.id}`)}
                          >
                            <Table.Cell>
                              <span className="text-sm font-medium text-text-primary">
                                Result {item.result.id}
                              </span>
                            </Table.Cell>
                            <Table.Cell mono className="text-text-tertiary text-xs">
                              {item.result.harness}:{item.result.provider}:{item.result.model}
                            </Table.Cell>
                            <Table.Cell>
                              <QualityBadge quality={item.result.quality} />
                            </Table.Cell>
                            <Table.Cell className="text-text-tertiary text-xs">
                              Judge #{item.judge.id}
                              {item.judge.alignment_score !== null && (
                                <span className="ml-1 text-text-disabled">
                                  ({item.judge.alignment_score.toFixed(2)})
                                </span>
                              )}
                            </Table.Cell>
                            <Table.Cell className="text-right">
                              <Button 
                                variant="primary" 
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  runJudge(item.judge.id, item.result.id)
                                }}
                                disabled={runningResultIds.has(item.result.id)}
                              >
                                {runningResultIds.has(item.result.id) 
                                  ? 'Judging...' 
                                  : 'Run Judge'}
                              </Button>
                            </Table.Cell>
                          </Table.Row>
                        ))}
                      </Table.Body>
                    </Table>
                  </Card.Content>
                </Card>
              )})}
            </div>
          )}
        </>
      )}

      {/* Completed Tab */}
      {activeTab === 'completed' && (
        <>
          {completedByScenario.length === 0 ? (
            <EmptyState
              title="No completed judgements"
              description="Run judges on completed results to see judgements here."
              action={
                <Button onClick={() => setActiveTab('pending')}>View Pending</Button>
              }
            />
          ) : (
            <div className="space-y-4">
              {completedByScenario.map(({ scenarioId, judgements: scenarioJudgements }) => {
                // Calculate stats for this scenario
                let aligned = 0
                scenarioJudgements.forEach((j: any) => {
                  if (j.quality !== null && j.result?.quality !== null && j.quality === j.result.quality) {
                    aligned++
                  }
                })
                const alignmentRate = scenarioJudgements.length > 0 
                  ? ((aligned / scenarioJudgements.length) * 100).toFixed(0) 
                  : '—'

                return (
                  <Card key={scenarioId}>
                    <Card.Header>
                      <div className="flex items-center justify-between">
                        <div>
                          <Link 
                            to={`/scenario/${scenarioId}`}
                            className="text-base font-semibold text-text-primary hover:text-accent transition-colors"
                          >
                            Scenario #{scenarioId}
                          </Link>
                          {scenarioJudgements[0]?.judge && (
                            <div className="text-xs text-text-tertiary mt-0.5">
                              Judge #{scenarioJudgements[0].judge.id}
                              {scenarioJudgements[0].judge.alignment_score !== null && (
                                <span className="ml-2">
                                  • Trained alignment: {scenarioJudgements[0].judge.alignment_score.toFixed(2)}
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                        <div className="flex items-center gap-4 text-sm">
                          <span className="text-text-secondary">{scenarioJudgements.length} judged</span>
                          <span className="text-text-tertiary">{alignmentRate}% aligned</span>
                        </div>
                      </div>
                    </Card.Header>
                    <Card.Content className="p-0">
                      <Table>
                        <Table.Header>
                          <tr>
                            <Table.Head>Result</Table.Head>
                            <Table.Head>Executor</Table.Head>
                            <Table.Head>Judge Quality</Table.Head>
                            <Table.Head>Human Quality</Table.Head>
                            <Table.Head>Match</Table.Head>
                            <Table.Head>Created</Table.Head>
                          </tr>
                        </Table.Header>
                        <Table.Body>
                          {scenarioJudgements.map((judgement: any) => {
                            const isAligned = judgement.quality !== null && 
                              judgement.result?.quality !== null && 
                              judgement.quality === judgement.result.quality
                            
                            return (
                              <Table.Row
                                key={judgement.id}
                                className="cursor-pointer"
                                onClick={() => navigate(`/result/${judgement.result_id}`)}
                              >
                                <Table.Cell>
                                  <span className="text-sm text-text-primary">
                                    Result {judgement.result_id}
                                  </span>
                                </Table.Cell>
                                <Table.Cell mono className="text-text-tertiary text-xs">
                                  {judgement.result?.model}
                                </Table.Cell>
                                <Table.Cell>
                                  <QualityBadge quality={judgement.quality} />
                                </Table.Cell>
                                <Table.Cell>
                                  <QualityBadge quality={judgement.result?.quality} />
                                </Table.Cell>
                                <Table.Cell>
                                  {judgement.quality !== null && judgement.result?.quality !== null ? (
                                    isAligned ? (
                                      <span className="text-status-success text-sm">✓</span>
                                    ) : (
                                      <span className="text-status-error text-sm">✗</span>
                                    )
                                  ) : (
                                    <span className="text-text-disabled">—</span>
                                  )}
                                </Table.Cell>
                                <Table.Cell className="text-text-tertiary text-xs">
                                  {formatDate(judgement.created_at)}
                                </Table.Cell>
                              </Table.Row>
                            )
                          })}
                        </Table.Body>
                      </Table>
                    </Card.Content>
                  </Card>
                )
              })}
            </div>
          )}
        </>
      )}
    </div>
  )
}
