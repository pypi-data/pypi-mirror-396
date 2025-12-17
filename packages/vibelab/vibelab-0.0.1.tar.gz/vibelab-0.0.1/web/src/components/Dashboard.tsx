import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { listScenarios, listDatasets, listExecutors, Result } from '../api'
import { PageHeader, Card, StatusBadge, Button } from './ui'
import { useMemo } from 'react'

// Stat card component
function StatCard({
  label,
  value,
  subValue,
  color = 'text-text-primary',
  icon,
}: {
  label: string
  value: string | number
  subValue?: string
  color?: string
  icon: React.ReactNode
}) {
  return (
    <div className="bg-surface border border-border rounded-lg p-4 flex items-start gap-3">
      <div className="p-2 rounded-lg bg-surface-2 text-text-tertiary">{icon}</div>
      <div className="flex-1 min-w-0">
        <div className={`text-2xl font-semibold ${color}`}>{value}</div>
        <div className="text-xs text-text-tertiary">{label}</div>
        {subValue && <div className="text-xs text-text-disabled mt-0.5">{subValue}</div>}
      </div>
    </div>
  )
}

// Quick action button
function QuickAction({
  to,
  icon,
  label,
  description,
}: {
  to: string
  icon: React.ReactNode
  label: string
  description: string
}) {
  return (
    <Link
      to={to}
      className="flex items-start gap-3 p-4 bg-surface border border-border rounded-lg hover:border-accent hover:bg-surface-2 transition-all group"
    >
      <div className="p-2 rounded-lg bg-accent/10 text-accent group-hover:bg-accent group-hover:text-on-accent transition-colors">
        {icon}
      </div>
      <div>
        <div className="font-medium text-text-primary group-hover:text-accent transition-colors">
          {label}
        </div>
        <div className="text-xs text-text-tertiary">{description}</div>
      </div>
    </Link>
  )
}

// Recent result row
function RecentResultRow({ result }: { result: Result }) {
  const executorParts = [result.harness, result.provider, result.model].filter(Boolean)
  const executor = executorParts.join(':')

  const formatTime = (dateStr: string) => {
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

  return (
    <Link
      to={`/result/${result.id}`}
      className="flex items-center gap-3 py-3 px-4 hover:bg-surface-2 transition-colors rounded-lg -mx-4"
    >
      <StatusBadge status={result.status} isStale={result.is_stale} />
      <div className="flex-1 min-w-0">
        <div className="text-sm text-text-primary truncate">
          Scenario #{result.scenario_id}
        </div>
        <div className="text-xs text-text-tertiary font-mono truncate">{executor}</div>
      </div>
      <div className="text-xs text-text-disabled shrink-0">
        {formatTime(result.updated_at || result.created_at)}
      </div>
    </Link>
  )
}

// Active run indicator
function ActiveRunCard({ result }: { result: Result }) {
  const executorParts = [result.harness, result.provider, result.model].filter(Boolean)
  const executor = executorParts.join(':')

  return (
    <Link
      to={`/result/${result.id}`}
      className="flex items-center gap-3 p-3 bg-status-info-muted border border-status-info/30 rounded-lg hover:border-status-info transition-colors"
    >
      <div className="w-2 h-2 rounded-full bg-status-info animate-pulse" />
      <div className="flex-1 min-w-0">
        <div className="text-sm text-text-primary">Scenario #{result.scenario_id}</div>
        <div className="text-xs text-text-tertiary font-mono truncate">{executor}</div>
      </div>
      <StatusBadge status={result.status} />
    </Link>
  )
}

// Icons
function PlayIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path d="M6.271 5.055a.5.5 0 0 1 .52.038l4.5 3a.5.5 0 0 1 0 .814l-4.5 3A.5.5 0 0 1 6 11.5v-6a.5.5 0 0 1 .271-.445z" />
    </svg>
  )
}

function FolderIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path d="M.54 3.87.5 3a2 2 0 0 1 2-2h3.672a2 2 0 0 1 1.414.586l.828.828A2 2 0 0 0 9.828 3H14a2 2 0 0 1 2 2v1.5H0v-.13z" />
      <path d="M16 6.5V13a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V6.5h16z" />
    </svg>
  )
}

function LayersIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path d="M8.235 1.559a.5.5 0 0 0-.47 0l-7.5 4a.5.5 0 0 0 0 .882L8 10.559l7.735-4.118a.5.5 0 0 0 0-.882l-7.5-4zM8 9.441 1.421 5.5 8 1.559 14.579 5.5 8 9.441zm-7.735.993a.5.5 0 0 0-.265.658l.033.085a.5.5 0 0 0 .232.232L8 15.441l7.735-4.118a.5.5 0 0 0 .265-.943l-.033-.085a.5.5 0 0 0-.232-.232L8 14.181 .265 10.063a.5.5 0 0 0-.265.371z" />
    </svg>
  )
}

function CpuIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path d="M5 0a.5.5 0 0 1 .5.5V2h1V.5a.5.5 0 0 1 1 0V2h1V.5a.5.5 0 0 1 1 0V2h1V.5a.5.5 0 0 1 1 0V2A2.5 2.5 0 0 1 14 4.5h1.5a.5.5 0 0 1 0 1H14v1h1.5a.5.5 0 0 1 0 1H14v1h1.5a.5.5 0 0 1 0 1H14v1h1.5a.5.5 0 0 1 0 1H14a2.5 2.5 0 0 1-2.5 2.5v1.5a.5.5 0 0 1-1 0V14h-1v1.5a.5.5 0 0 1-1 0V14h-1v1.5a.5.5 0 0 1-1 0V14h-1v1.5a.5.5 0 0 1-1 0V14A2.5 2.5 0 0 1 2 11.5H.5a.5.5 0 0 1 0-1H2v-1H.5a.5.5 0 0 1 0-1H2v-1H.5a.5.5 0 0 1 0-1H2v-1H.5a.5.5 0 0 1 0-1H2A2.5 2.5 0 0 1 4.5 2V.5A.5.5 0 0 1 5 0zm-.5 3A1.5 1.5 0 0 0 3 4.5v7A1.5 1.5 0 0 0 4.5 13h7a1.5 1.5 0 0 0 1.5-1.5v-7A1.5 1.5 0 0 0 11.5 3h-7zM5 6.5A1.5 1.5 0 0 1 6.5 5h3A1.5 1.5 0 0 1 11 6.5v3A1.5 1.5 0 0 1 9.5 11h-3A1.5 1.5 0 0 1 5 9.5v-3zM6.5 6a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3z" />
    </svg>
  )
}

function DollarIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path d="M4 10.781c.148 1.667 1.513 2.85 3.591 3.003V15h1.043v-1.216c2.27-.179 3.678-1.438 3.678-3.3 0-1.59-.947-2.51-2.956-3.028l-.722-.187V3.467c1.122.11 1.879.714 2.07 1.616h1.47c-.166-1.6-1.54-2.748-3.54-2.875V1H7.591v1.233c-1.939.23-3.27 1.472-3.27 3.156 0 1.454.966 2.483 2.661 2.917l.61.162v4.031c-1.149-.17-1.94-.8-2.131-1.718H4zm3.391-3.836c-1.043-.263-1.6-.825-1.6-1.616 0-.944.704-1.641 1.8-1.828v3.495l-.2-.05zm1.591 1.872c1.287.323 1.852.859 1.852 1.769 0 1.097-.826 1.828-2.2 1.939V8.73l.348.086z" />
    </svg>
  )
}

function CheckIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z" />
    </svg>
  )
}

function ClockIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z" />
      <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z" />
    </svg>
  )
}

function StarIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>
    </svg>
  )
}

function ScaleIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path d="M5.5 3a.5.5 0 0 1 .5.5v1.854l4.424-2.653A.5.5 0 0 1 11 3.146v5.708a.5.5 0 0 1-.576.499L6 6.5v1.854l4.424-2.653A.5.5 0 0 1 11 6.146v5.708a.5.5 0 0 1-.576.499L6 9.5V12.5a.5.5 0 0 1-1 0v-9a.5.5 0 0 1 .5-.5z"/>
      <path d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 1 8 0a8 8 0 0 1 0 16z"/>
    </svg>
  )
}

function ChartIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path d="M4 11H2v3h2v-3zm5-4H7v7h2V7zm5-5h-2v12h2V2zm-2-1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1h-2zM6 7a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7zm-5 4a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1v-3z"/>
    </svg>
  )
}

export default function Dashboard() {
  const { data: scenariosData, isLoading: scenariosLoading } = useQuery({
    queryKey: ['scenarios'],
    queryFn: listScenarios,
    refetchInterval: (query) => {
      const data = query.state.data
      const hasRunning = Object.values(data?.results_by_scenario || {})
        .flat()
        .some((r: any) => r.status === 'running' || r.status === 'queued')
      return hasRunning ? 3000 : false
    },
  })

  const { data: datasetsData, isLoading: datasetsLoading } = useQuery({
    queryKey: ['datasets'],
    queryFn: listDatasets,
  })

  const { data: executorsData } = useQuery({
    queryKey: ['executors'],
    queryFn: listExecutors,
  })

  // Compute stats
  const stats = useMemo(() => {
    const allResults = Object.values(scenariosData?.results_by_scenario || {}).flat() as Result[]
    const completed = allResults.filter((r) => r.status === 'completed').length
    const failed = allResults.filter(
      (r) => r.status === 'failed' || r.status === 'infra_failure'
    ).length
    const timeout = allResults.filter((r) => r.status === 'timeout').length
    const running = allResults.filter(
      (r) => (r.status === 'running' || r.status === 'queued') && !r.is_stale
    ).length
    const totalCost = allResults.reduce((sum, r) => sum + (r.cost_usd || 0), 0)
    const successRate = allResults.length > 0 ? Math.round((completed / allResults.length) * 100) : 0

    // Calculate quality stats
    const qualityScores = allResults
      .filter((r) => r.status === 'completed' && r.quality !== null && r.quality !== undefined)
      .map((r) => r.quality as number)
    const avgQuality = qualityScores.length > 0
      ? qualityScores.reduce((a, b) => a + b, 0) / qualityScores.length
      : null
    const ratedCount = qualityScores.length

    // Count scenarios with judges
    const scenariosWithJudges = Object.keys(scenariosData?.judges_by_scenario || {}).length

    return {
      scenarios: scenariosData?.scenarios.length || 0,
      results: allResults.length,
      completed,
      failed,
      timeout,
      running,
      totalCost,
      successRate,
      datasets: datasetsData?.datasets.length || 0,
      executors: executorsData?.harnesses.length || 0,
      avgQuality,
      ratedCount,
      scenariosWithJudges,
    }
  }, [scenariosData, datasetsData, executorsData])

  // Get recent results
  const recentResults = useMemo(() => {
    const allResults = Object.values(scenariosData?.results_by_scenario || {}).flat() as Result[]
    return allResults
      .sort(
        (a, b) =>
          new Date(b.updated_at || b.created_at).getTime() -
          new Date(a.updated_at || a.created_at).getTime()
      )
      .slice(0, 8)
  }, [scenariosData])

  // Get active runs
  const activeRuns = useMemo(() => {
    const allResults = Object.values(scenariosData?.results_by_scenario || {}).flat() as Result[]
    return allResults.filter(
      (r) => (r.status === 'running' || r.status === 'queued') && !r.is_stale
    )
  }, [scenariosData])

  const isLoading = scenariosLoading || datasetsLoading

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Dashboard" description="Welcome to VibeLab" />
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </div>
    )
  }

  const isEmpty = stats.scenarios === 0 && stats.datasets === 0

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="AI coding agent evaluation & comparison"
      />

      {isEmpty ? (
        // Empty state for new users
        <div className="mt-8">
          <Card>
            <Card.Content className="py-12">
              <div className="text-center max-w-md mx-auto">
                <div className="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-4">
                  <PlayIcon />
                </div>
                <h2 className="text-xl font-semibold text-text-primary mb-2">
                  Welcome to VibeLab
                </h2>
                <p className="text-text-secondary mb-6">
                  Compare AI coding agents side-by-side. Create your first run to get started.
                </p>
                <div className="flex gap-3 justify-center">
                  <Link to="/run/create">
                    <Button>Create First Run</Button>
                  </Link>
                  <Link to="/datasets/create">
                    <Button variant="secondary">Create Dataset</Button>
                  </Link>
                </div>
              </div>
            </Card.Content>
          </Card>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Active Runs Alert */}
          {activeRuns.length > 0 && (
            <Card>
              <Card.Header>
                <Card.Title className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-status-info animate-pulse" />
                  Active Runs ({activeRuns.length})
                </Card.Title>
              </Card.Header>
              <Card.Content>
                <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
                  {activeRuns.slice(0, 6).map((result) => (
                    <ActiveRunCard key={result.id} result={result} />
                  ))}
                </div>
                {activeRuns.length > 6 && (
                  <div className="mt-3 text-center">
                    <Link to="/runs" className="text-sm text-accent hover:text-accent-hover">
                      View all {activeRuns.length} active runs →
                    </Link>
                  </div>
                )}
              </Card.Content>
            </Card>
          )}

          {/* Stats Overview */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
            <StatCard
              icon={<LayersIcon />}
              label="Scenarios"
              value={stats.scenarios}
              subValue={stats.scenariosWithJudges > 0 ? `${stats.scenariosWithJudges} with judges` : undefined}
              color="text-text-primary"
            />
            <StatCard
              icon={<CpuIcon />}
              label="Total Runs"
              value={stats.results}
              color="text-text-primary"
            />
            <StatCard
              icon={<CheckIcon />}
              label="Success Rate"
              value={`${stats.successRate}%`}
              subValue={`${stats.completed} completed`}
              color="text-status-success"
            />
            <StatCard
              icon={<ClockIcon />}
              label="Failed / Timeout"
              value={stats.failed + stats.timeout}
              color={stats.failed + stats.timeout > 0 ? 'text-status-error' : 'text-text-tertiary'}
            />
            <StatCard
              icon={<StarIcon />}
              label="Avg Quality"
              value={stats.avgQuality !== null ? stats.avgQuality.toFixed(1) : '—'}
              subValue={stats.ratedCount > 0 ? `${stats.ratedCount} rated` : 'No ratings yet'}
              color={
                stats.avgQuality === null ? 'text-text-tertiary' :
                stats.avgQuality >= 3.5 ? 'text-emerald-500' :
                stats.avgQuality >= 2.5 ? 'text-sky-500' :
                stats.avgQuality >= 1.5 ? 'text-amber-500' : 'text-rose-500'
              }
            />
            <StatCard
              icon={<FolderIcon />}
              label="Datasets"
              value={stats.datasets}
              color="text-text-primary"
            />
            <StatCard
              icon={<DollarIcon />}
              label="Total Cost"
              value={`$${stats.totalCost.toFixed(2)}`}
              color="text-text-primary"
            />
          </div>

          {/* Main Content Grid */}
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Quick Actions */}
            <Card className="lg:col-span-1">
              <Card.Header>
                <Card.Title>Quick Actions</Card.Title>
              </Card.Header>
              <Card.Content className="space-y-3">
                <QuickAction
                  to="/run/create"
                  icon={<PlayIcon />}
                  label="New Run"
                  description="Create a new evaluation run"
                />
                <QuickAction
                  to="/datasets/create"
                  icon={<FolderIcon />}
                  label="Create Dataset"
                  description="Group scenarios for batch evaluation"
                />
                <QuickAction
                  to="/scenarios"
                  icon={<LayersIcon />}
                  label="Browse Scenarios"
                  description="View and manage all scenarios"
                />
                <QuickAction
                  to="/executors"
                  icon={<CpuIcon />}
                  label="View Executors"
                  description="See available AI agents"
                />
                <QuickAction
                  to="/judgements"
                  icon={<ScaleIcon />}
                  label="View Judgements"
                  description="LLM judge assessments"
                />
                <QuickAction
                  to="/report"
                  icon={<ChartIcon />}
                  label="Global Report"
                  description="Quality matrix across all scenarios"
                />
              </Card.Content>
            </Card>

            {/* Recent Activity */}
            <Card className="lg:col-span-2">
              <Card.Header>
                <div className="flex items-center justify-between">
                  <Card.Title>Recent Activity</Card.Title>
                  <Link to="/runs" className="text-sm text-accent hover:text-accent-hover">
                    View all →
                  </Link>
                </div>
              </Card.Header>
              <Card.Content>
                {recentResults.length === 0 ? (
                  <div className="text-center py-8 text-text-tertiary">
                    No results yet. Create a run to get started.
                  </div>
                ) : (
                  <div className="divide-y divide-border-muted">
                    {recentResults.map((result) => (
                      <RecentResultRow key={result.id} result={result} />
                    ))}
                  </div>
                )}
              </Card.Content>
            </Card>
          </div>

          {/* Datasets Section */}
          {datasetsData && datasetsData.datasets.length > 0 && (
            <Card>
              <Card.Header>
                <div className="flex items-center justify-between">
                  <Card.Title>Datasets</Card.Title>
                  <Link to="/datasets" className="text-sm text-accent hover:text-accent-hover">
                    View all →
                  </Link>
                </div>
              </Card.Header>
              <Card.Content>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {datasetsData.datasets.slice(0, 6).map((dataset) => (
                    <Link
                      key={dataset.id}
                      to={`/dataset/${dataset.id}`}
                      className="p-4 bg-surface-2 rounded-lg hover:bg-surface-3 transition-colors"
                    >
                      <div className="font-medium text-text-primary">{dataset.name}</div>
                      <div className="text-xs text-text-tertiary mt-1">
                        {dataset.scenario_count} scenarios
                      </div>
                      {dataset.description && (
                        <div className="text-xs text-text-disabled mt-2 line-clamp-2">
                          {dataset.description}
                        </div>
                      )}
                    </Link>
                  ))}
                </div>
              </Card.Content>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
