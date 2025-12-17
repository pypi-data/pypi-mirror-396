import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { listScenarios, deleteScenario } from '../api'
import { PageHeader, Card, Table, EmptyState, Button, ConfirmDialog, DropdownMenu, DropdownItem, OverflowMenuTrigger } from './ui'
import { useState } from 'react'

export default function Scenarios() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [deleteTarget, setDeleteTarget] = useState<{ id: number; resultCount: number } | null>(null)
  
  const { data, isLoading } = useQuery({
    queryKey: ['scenarios'],
    queryFn: listScenarios,
    refetchInterval: (query) => {
      const data = query.state.data
      const hasRunning = Object.values(data?.results_by_scenario || {}).flat().some(
        (r: any) => r.status === 'running' || r.status === 'queued'
      )
      return hasRunning ? 3000 : false
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteScenario(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
      setDeleteTarget(null)
    },
  })

  const formatRelativeTime = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  const getCodeRefDisplay = (scenario: any) => {
    if (!scenario.code_ref) return null
    if (scenario.code_type === 'github') {
      const ref = scenario.code_ref
      return {
        type: 'github',
        display: `${ref.owner}/${ref.repo}`,
        full: `${ref.owner}/${ref.repo}@${ref.commit_sha || ref.branch || 'main'}`,
      }
    } else if (scenario.code_type === 'local') {
      const path = scenario.code_ref.path
      const parts = path.split('/')
      return {
        type: 'local',
        display: parts.length > 2 ? `.../${parts.slice(-2).join('/')}` : path,
        full: path,
      }
    }
    return null
  }

  const getResultStats = (results: any[]) => {
    const completed = results.filter(r => r.status === 'completed').length
    const failed = results.filter(r => r.status === 'failed' || r.status === 'infra_failure').length
    const timeout = results.filter(r => r.status === 'timeout').length
    const running = results.filter(r => (r.status === 'running' || r.status === 'queued') && !r.is_stale).length
    
    // Calculate average quality from completed results that have quality scores
    const qualityScores = results
      .filter(r => r.status === 'completed' && r.quality !== null && r.quality !== undefined)
      .map(r => r.quality)
    const avgQuality = qualityScores.length > 0 
      ? qualityScores.reduce((a, b) => a + b, 0) / qualityScores.length 
      : null
    
    return { total: results.length, completed, failed, timeout, running, avgQuality, qualityCount: qualityScores.length }
  }

  if (isLoading) {
    return (
      <div>
        <PageHeader breadcrumbs={[{ label: 'Scenarios' }]} title="Scenarios" />
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </div>
    )
  }

  const scenarios = data?.scenarios || []
  const resultsByScenario = data?.results_by_scenario || {}
  const judgesByScenario = data?.judges_by_scenario || {}

  return (
    <div>
      <PageHeader
        breadcrumbs={[{ label: 'Scenarios' }]}
        title="Scenarios"
        description={`${scenarios.length} scenario${scenarios.length !== 1 ? 's' : ''} for comparing AI coding agents`}
        actions={
          <Link to="/run/create">
            <Button>New Scenario</Button>
          </Link>
        }
      />

      {scenarios.length === 0 ? (
        <EmptyState
          title="No scenarios yet"
          description="Create your first scenario to get started comparing AI agents."
          action={
            <Link to="/run/create">
              <Button>Create Scenario</Button>
            </Link>
          }
        />
      ) : (
        <Card>
          <Card.Content className="p-0">
            <Table>
              <Table.Header>
                <tr>
                  <Table.Head className="w-[45%]">Scenario</Table.Head>
                  <Table.Head>Code</Table.Head>
                  <Table.Head>Results</Table.Head>
                  <Table.Head>Quality</Table.Head>
                  <Table.Head className="w-[80px]"></Table.Head>
                </tr>
              </Table.Header>
              <Table.Body>
                {scenarios.map((scenario) => {
                  const results = resultsByScenario[scenario.id] || []
                  const stats = getResultStats(results)
                  const codeRef = getCodeRefDisplay(scenario)
                  const judge = judgesByScenario[scenario.id]

                  return (
                    <Table.Row 
                      key={scenario.id}
                      className="cursor-pointer"
                      onClick={() => navigate(`/scenario/${scenario.id}`)}
                    >
                      {/* Scenario info */}
                      <Table.Cell>
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-text-primary">
                              Scenario #{scenario.id}
                            </span>
                            {judge && (
                              <span 
                                className="text-[10px] px-1.5 py-0.5 rounded bg-accent/10 text-accent font-medium"
                                title={`Judge configured${judge.alignment_score ? ` (alignment: ${judge.alignment_score.toFixed(2)})` : ''}`}
                              >
                                ⚖ Judge
                              </span>
                            )}
                            <span className="text-xs text-text-disabled">
                              {formatRelativeTime(scenario.created_at)}
                            </span>
                          </div>
                          <div className="text-sm text-text-secondary line-clamp-2">
                            {scenario.prompt}
                          </div>
                        </div>
                      </Table.Cell>

                      {/* Code reference */}
                      <Table.Cell>
                        {codeRef ? (
                          <div className="flex items-center gap-1.5">
                            {codeRef.type === 'github' && (
                              <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" className="text-text-tertiary shrink-0">
                                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                              </svg>
                            )}
                            {codeRef.type === 'local' && (
                              <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" className="text-text-tertiary shrink-0">
                                <path d="M.54 3.87L.5 3a2 2 0 012-2h3.672a2 2 0 011.414.586l.828.828A2 2 0 009.828 3H14a2 2 0 012 2v1.5H0v-.13zM16 6.5V13a2 2 0 01-2 2H2a2 2 0 01-2-2V6.5h16z"/>
                              </svg>
                            )}
                            <span
                              className="text-xs font-mono text-text-tertiary truncate max-w-[150px]"
                              title={codeRef.full}
                            >
                              {codeRef.display}
                            </span>
                          </div>
                        ) : (
                          <span className="text-xs text-text-disabled">Empty</span>
                        )}
                      </Table.Cell>

                      {/* Results summary */}
                      <Table.Cell>
                        {stats.total === 0 ? (
                          <span className="text-xs text-text-disabled">No runs</span>
                        ) : (
                          <div className="flex items-center gap-2 text-xs">
                            <span className="text-text-secondary font-medium">{stats.total}</span>
                            {stats.completed > 0 && (
                              <span className="text-status-success">✓ {stats.completed}</span>
                            )}
                            {stats.failed > 0 && (
                              <span className="text-status-error">✗ {stats.failed}</span>
                            )}
                            {stats.timeout > 0 && (
                              <span className="text-status-warning">⏱ {stats.timeout}</span>
                            )}
                            {stats.running > 0 && (
                              <span className="text-status-info flex items-center gap-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-status-info animate-pulse" />
                                {stats.running}
                              </span>
                            )}
                          </div>
                        )}
                      </Table.Cell>

                      {/* Quality */}
                      <Table.Cell>
                        {stats.avgQuality !== null ? (
                          <div className="flex items-center gap-1.5">
                            <span className={`text-xs font-medium ${
                              stats.avgQuality >= 3.5 ? 'text-emerald-500' :
                              stats.avgQuality >= 2.5 ? 'text-sky-500' :
                              stats.avgQuality >= 1.5 ? 'text-amber-500' : 'text-rose-500'
                            }`}>
                              {stats.avgQuality >= 3.5 ? '★' :
                               stats.avgQuality >= 2.5 ? '●' :
                               stats.avgQuality >= 1.5 ? '◐' : '✗'} {stats.avgQuality.toFixed(1)}
                            </span>
                            <span className="text-[10px] text-text-disabled">
                              ({stats.qualityCount})
                            </span>
                          </div>
                        ) : (
                          <span className="text-xs text-text-disabled">—</span>
                        )}
                      </Table.Cell>

                      {/* Actions */}
                      <Table.Cell>
                        <div 
                          className="flex items-center justify-end"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <DropdownMenu trigger={<OverflowMenuTrigger />}>
                            <DropdownItem
                              danger
                              onClick={() => setDeleteTarget({ id: scenario.id, resultCount: stats.total })}
                            >
                              Delete scenario
                            </DropdownItem>
                          </DropdownMenu>
                        </div>
                      </Table.Cell>
                    </Table.Row>
                  )
                })}
              </Table.Body>
            </Table>
          </Card.Content>
        </Card>
      )}

      <ConfirmDialog
        open={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => {
          if (deleteTarget) {
            deleteMutation.mutate(deleteTarget.id)
          }
        }}
        title="Delete Scenario"
        description={
          deleteTarget
            ? `Are you sure you want to delete scenario ${deleteTarget.id}? This will permanently delete the scenario and all ${deleteTarget.resultCount} associated results.`
            : ''
        }
        confirmLabel="Delete"
        danger
        loading={deleteMutation.isPending}
      />
    </div>
  )
}
