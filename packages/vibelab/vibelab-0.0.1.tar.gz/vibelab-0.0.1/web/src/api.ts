const API_BASE = '/api'

export interface Scenario {
  id: number
  code_type: string
  code_ref: any
  prompt: string
  created_at: string
}

export interface Result {
  id: number
  scenario_id: number
  harness: string
  provider: string
  model: string
  status: string
  created_at: string
  updated_at?: string
  started_at?: string
  finished_at?: string
  duration_ms?: number
  lines_added?: number
  lines_removed?: number
  files_changed?: number
  tokens_used?: number
  cost_usd?: number
  harness_metrics?: any
  annotations?: any
  timeout_seconds?: number
  driver?: string
  is_stale?: boolean
  error_message?: string
  notes?: string
  quality?: number  // 1=Bad, 2=Workable, 3=Good, 4=Perfect
}

export interface ExecutorInfo {
  id: string
  name: string
  providers: string[]
}

export interface DriverInfo {
  id: string
  name: string
}

export interface ProviderDetail {
  id: string
  models: Array<{ id: string; name: string }>
}

export interface HarnessDetail {
  harness: string
  providers: ProviderDetail[]
}

export async function listScenarios(): Promise<{ 
  scenarios: Scenario[], 
  results_by_scenario: Record<string, Result[]>,
  judges_by_scenario: Record<string, { id: number, alignment_score: number | null }> 
}> {
  const response = await fetch(`${API_BASE}/scenarios`)
  if (!response.ok) throw new Error('Failed to fetch scenarios')
  return response.json()
}

export async function getScenario(id: number): Promise<{ scenario: Scenario, results: Result[] }> {
  const response = await fetch(`${API_BASE}/scenarios/${id}`)
  if (!response.ok) throw new Error('Failed to fetch scenario')
  return response.json()
}

export async function createScenario(data: { code_type: string, code_ref?: any, prompt: string }): Promise<Scenario> {
  const response = await fetch(`${API_BASE}/scenarios`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to create scenario')
  return response.json()
}

export async function listResults(filters?: { scenario_id?: number, executor?: string, status?: string }): Promise<Result[]> {
  const params = new URLSearchParams()
  if (filters?.scenario_id) params.append('scenario_id', String(filters.scenario_id))
  if (filters?.executor) params.append('executor', filters.executor)
  if (filters?.status) params.append('status', filters.status)
  const response = await fetch(`${API_BASE}/results?${params}`)
  if (!response.ok) throw new Error('Failed to fetch results')
  return response.json()
}

export async function getResult(id: number): Promise<Result> {
  const response = await fetch(`${API_BASE}/results/${id}`)
  if (!response.ok) throw new Error('Failed to fetch result')
  return response.json()
}

export async function getResultPatch(id: number): Promise<{ patch: string }> {
  const response = await fetch(`${API_BASE}/results/${id}/patch`)
  if (!response.ok) throw new Error('Failed to fetch patch')
  return response.json()
}

export async function getResultLogs(id: number): Promise<{ stdout: string, stderr: string }> {
  const response = await fetch(`${API_BASE}/results/${id}/logs`)
  if (!response.ok) throw new Error('Failed to fetch logs')
  return response.json()
}

export async function createRun(data: { scenario_id: number, executor_spec: string, timeout_seconds?: number, driver?: string }): Promise<{ status: string, scenario_id: number, executor_spec: string, result_id: number }> {
  const response = await fetch(`${API_BASE}/runs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to create run')
  return response.json()
}

export async function listExecutors(): Promise<{ harnesses: ExecutorInfo[] }> {
  const response = await fetch(`${API_BASE}/executors`)
  if (!response.ok) throw new Error('Failed to fetch executors')
  return response.json()
}

export async function getExecutorModels(harness: string, provider: string): Promise<{ models: Array<{ id: string, name: string }> }> {
  const response = await fetch(`${API_BASE}/executors/${harness}/${provider}`)
  if (!response.ok) throw new Error('Failed to fetch models')
  return response.json()
}

export async function getHarnessDetail(harness: string): Promise<HarnessDetail> {
  const response = await fetch(`${API_BASE}/executors/${harness}`)
  if (!response.ok) throw new Error('Failed to fetch harness detail')
  return response.json()
}

export async function listDrivers(): Promise<{ drivers: DriverInfo[] }> {
  const response = await fetch(`${API_BASE}/executors/drivers/list`)
  if (!response.ok) throw new Error('Failed to fetch drivers')
  return response.json()
}

export async function deleteScenario(id: number): Promise<{ status: string, scenario_id: number }> {
  const response = await fetch(`${API_BASE}/scenarios/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) throw new Error('Failed to delete scenario')
  return response.json()
}

export async function deleteResult(id: number): Promise<{ status: string, result_id: number }> {
  const response = await fetch(`${API_BASE}/results/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) throw new Error('Failed to delete result')
  return response.json()
}

export async function rerunResult(id: number): Promise<{ result_id: number, status: string, scenario_id: number, executor_spec: string, original_result_id: number }> {
  const response = await fetch(`${API_BASE}/results/${id}/rerun`, {
    method: 'POST',
  })
  if (!response.ok) throw new Error('Failed to rerun result')
  return response.json()
}

export async function updateResultNotes(id: number, notes: string | null): Promise<Result> {
  const response = await fetch(`${API_BASE}/results/${id}/notes`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ notes }),
  })
  if (!response.ok) throw new Error('Failed to update result notes')
  return response.json()
}

export async function updateResultQuality(id: number, quality: number | null): Promise<Result> {
  const response = await fetch(`${API_BASE}/results/${id}/quality`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quality }),
  })
  if (!response.ok) throw new Error('Failed to update result quality')
  return response.json()
}

export async function updateResultNotesAndQuality(id: number, notes: string | null, quality: number | null): Promise<Result> {
  const response = await fetch(`${API_BASE}/results/${id}/notes-quality`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ notes, quality }),
  })
  if (!response.ok) throw new Error('Failed to update result notes and quality')
  return response.json()
}

// Streaming types
export interface StreamEvent {
  type: 'connected' | 'status' | 'output' | 'patch' | 'done' | 'error'
  data: any
}

export interface StreamCallbacks {
  onConnect?: (resultId: number) => void
  onStatus?: (status: string) => void
  onOutput?: (data: string, offset?: number) => void
  onPatch?: (patch: string) => void
  onDone?: (status: string) => void
  onError?: (error: string) => void
}

/**
 * Subscribe to streaming logs for a result.
 * Returns a function to close the connection.
 */
export function subscribeToResultStream(
  resultId: number,
  callbacks: StreamCallbacks
): () => void {
  const url = `${API_BASE}/results/${resultId}/stream`
  console.log('[Streaming] Connecting to:', url)
  const eventSource = new EventSource(url)

  eventSource.addEventListener('connected', (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('[Streaming] Connected:', data)
      callbacks.onConnect?.(data.result_id)
    } catch (e) {
      console.error('[Streaming] Error parsing connected event:', e)
    }
  })

  eventSource.addEventListener('status', (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('[Streaming] Status update:', data.status)
      callbacks.onStatus?.(data.status)
    } catch (e) {
      console.error('[Streaming] Error parsing status event:', e)
    }
  })

  eventSource.addEventListener('output', (event) => {
    try {
      const data = JSON.parse(event.data)
      callbacks.onOutput?.(data.data, data.offset)
    } catch (e) {
      console.error('[Streaming] Error parsing output event:', e)
    }
  })

  eventSource.addEventListener('patch', (event) => {
    try {
      const data = JSON.parse(event.data)
      callbacks.onPatch?.(data.patch)
    } catch (e) {
      console.error('[Streaming] Error parsing patch event:', e)
    }
  })

  eventSource.addEventListener('done', (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('[Streaming] Done:', data.status)
      callbacks.onDone?.(data.status)
      eventSource.close()
    } catch (e) {
      console.error('[Streaming] Error parsing done event:', e)
      eventSource.close()
    }
  })

  eventSource.addEventListener('error', (event) => {
    // Check if it's a real error or just a connection close
    if (eventSource.readyState === EventSource.CLOSED) {
      return
    }
    try {
      const data = JSON.parse((event as MessageEvent).data)
      console.error('[Streaming] Error event:', data.error)
      callbacks.onError?.(data.error)
    } catch {
      console.error('[Streaming] Connection error')
      callbacks.onError?.('Connection error')
    }
  })

  eventSource.onerror = (error) => {
    console.error('[Streaming] EventSource error:', error, 'readyState:', eventSource.readyState)
    if (eventSource.readyState === EventSource.CLOSED) {
      return
    }
    // Don't call onError here if we're just waiting for connection
    // Only call if it's a real error after connection
    if (eventSource.readyState === EventSource.CONNECTING) {
      // Still connecting, might be normal
      return
    }
    callbacks.onError?.('Connection lost')
  }

  return () => {
    console.log('[Streaming] Closing connection')
    eventSource.close()
  }
}

export async function getStreamStatus(id: number): Promise<{ status: string, streaming: boolean }> {
  const response = await fetch(`${API_BASE}/results/${id}/stream/status`)
  if (!response.ok) throw new Error('Failed to fetch stream status')
  return response.json()
}

// Dataset types and functions
export interface Dataset {
  id: number
  name: string
  description?: string
  created_at: string
}

export async function listDatasets(): Promise<{ datasets: Array<Dataset & { scenario_count: number }> }> {
  const response = await fetch(`${API_BASE}/datasets`)
  if (!response.ok) throw new Error('Failed to fetch datasets')
  return response.json()
}

export async function getDataset(id: number): Promise<{ dataset: Dataset, scenarios: Scenario[] }> {
  const response = await fetch(`${API_BASE}/datasets/${id}`)
  if (!response.ok) throw new Error('Failed to fetch dataset')
  return response.json()
}

export async function createDataset(data: { name: string, description?: string }): Promise<Dataset> {
  const response = await fetch(`${API_BASE}/datasets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to create dataset')
  return response.json()
}

export async function deleteDataset(id: number): Promise<{ status: string, dataset_id: number }> {
  const response = await fetch(`${API_BASE}/datasets/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) throw new Error('Failed to delete dataset')
  return response.json()
}

export async function addScenarioToDataset(datasetId: number, scenarioId: number): Promise<{ status: string, dataset_id: number, scenario_id: number }> {
  const response = await fetch(`${API_BASE}/datasets/${datasetId}/scenarios`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario_id: scenarioId }),
  })
  if (!response.ok) throw new Error('Failed to add scenario to dataset')
  return response.json()
}

export async function removeScenarioFromDataset(datasetId: number, scenarioId: number): Promise<{ status: string, dataset_id: number, scenario_id: number }> {
  const response = await fetch(`${API_BASE}/datasets/${datasetId}/scenarios/${scenarioId}`, {
    method: 'DELETE',
  })
  if (!response.ok) throw new Error('Failed to remove scenario from dataset')
  return response.json()
}

export async function createDatasetRun(data: {
  dataset_id: number,
  executor_specs: string[],
  trials?: number,
  minimal?: boolean,
  timeout_seconds?: number,
  driver?: string
}): Promise<{ status: string, dataset_id: number, pairs_run: number, result_ids: number[] }> {
  const response = await fetch(`${API_BASE}/datasets/${data.dataset_id}/runs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      executor_specs: data.executor_specs,
      trials: data.trials ?? 1,
      minimal: data.minimal ?? false,
      timeout_seconds: data.timeout_seconds ?? 1800,
      driver: data.driver ?? 'local',
    }),
  })
  if (!response.ok) throw new Error('Failed to create dataset run')
  return response.json()
}

export async function getDatasetAnalytics(id: number): Promise<{
  dataset: Dataset,
  executors: string[],
  matrix: Array<{
    scenario_id: number,
    scenario_prompt: string,
    cells: Record<string, {
      status: string,
      total: number,
      completed: number,
      failed: number,
      timeout: number,
      running: number,
      queued: number,
      result_ids?: number[],
      avg_quality?: number | null,
      quality_count?: number,
      avg_duration_ms?: number | null,
      duration_count?: number
    }>
  }>
}> {
  const response = await fetch(`${API_BASE}/datasets/${id}/analytics`)
  if (!response.ok) throw new Error('Failed to fetch dataset analytics')
  return response.json()
}

export interface GlobalAnalytics {
  title: string
  description: string
  scenario_count: number
  executors: string[]
  matrix: Array<{
    scenario_id: number
    scenario_prompt: string
    cells: Record<string, {
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
    }>
  }>
}

export async function getGlobalAnalytics(): Promise<GlobalAnalytics> {
  const response = await fetch(`${API_BASE}/scenarios/analytics/global`)
  if (!response.ok) throw new Error('Failed to fetch global analytics')
  return response.json()
}

// Judge types and functions
export interface LLMScenarioJudge {
  id: number
  scenario_id: number
  guidance: string
  training_sample_ids: number[]
  test_sample_ids: number[]
  alignment_score?: number | null
  created_at: string
}

export interface Judgement {
  id: number
  result_id: number
  judge_id: number
  notes?: string | null
  quality?: number | null
  created_at: string
}

export async function listJudges(scenarioId?: number): Promise<LLMScenarioJudge[]> {
  const params = scenarioId ? `?scenario_id=${scenarioId}` : ''
  const response = await fetch(`${API_BASE}/judges${params}`)
  if (!response.ok) throw new Error('Failed to fetch judges')
  return response.json()
}

export async function getJudge(id: number): Promise<LLMScenarioJudge> {
  const response = await fetch(`${API_BASE}/judges/${id}`)
  if (!response.ok) throw new Error('Failed to fetch judge')
  return response.json()
}

export async function createJudge(data: {
  scenario_id: number,
  guidance: string,
  training_sample_ids: number[],
  test_sample_ids: number[]
}): Promise<LLMScenarioJudge> {
  const response = await fetch(`${API_BASE}/judges`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to create judge')
  return response.json()
}

export async function updateJudge(judgeId: number, data: {
  scenario_id: number,
  guidance: string,
  training_sample_ids: number[],
  test_sample_ids: number[]
}): Promise<LLMScenarioJudge> {
  const response = await fetch(`${API_BASE}/judges/${judgeId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to update judge')
  return response.json()
}

export async function trainJudge(id: number, judge_provider?: string, judge_model?: string): Promise<{ status: string, judge_id: number }> {
  const response = await fetch(`${API_BASE}/judges/${id}/train`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      judge_provider: judge_provider || 'anthropic',
      judge_model: judge_model || 'claude-sonnet-4-20250514',
    }),
  })
  if (!response.ok) throw new Error('Failed to train judge')
  return response.json()
}

export async function deleteJudge(id: number): Promise<{ status: string, judge_id: number }> {
  const response = await fetch(`${API_BASE}/judges/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) throw new Error('Failed to delete judge')
  return response.json()
}

export async function listJudgeJudgements(judgeId: number): Promise<Judgement[]> {
  const response = await fetch(`${API_BASE}/judges/${judgeId}/judgements`)
  if (!response.ok) throw new Error('Failed to fetch judgements')
  return response.json()
}

export interface EnrichedJudgement extends Judgement {
  result?: Result
  judge?: LLMScenarioJudge
}

export async function listAllJudgements(): Promise<EnrichedJudgement[]> {
  const response = await fetch(`${API_BASE}/judges/judgements/all`)
  if (!response.ok) throw new Error('Failed to fetch judgements')
  return response.json()
}

export async function listPendingJudgements(): Promise<Array<{ result: Result, judge: LLMScenarioJudge }>> {
  const response = await fetch(`${API_BASE}/judges/judgements/pending`)
  if (!response.ok) throw new Error('Failed to fetch pending judgements')
  return response.json()
}

export interface ScenarioJudgement extends Judgement {
  result?: Result
  judge?: LLMScenarioJudge
  is_latest_judge?: boolean
}

export async function listScenarioJudgements(scenarioId: number): Promise<ScenarioJudgement[]> {
  const response = await fetch(`${API_BASE}/judges/scenarios/${scenarioId}/judgements`)
  if (!response.ok) throw new Error('Failed to fetch scenario judgements')
  return response.json()
}

export async function acceptJudgement(judgementId: number): Promise<Result> {
  const response = await fetch(`${API_BASE}/judges/judgements/${judgementId}/accept`, {
    method: 'POST',
  })
  if (!response.ok) throw new Error('Failed to accept judgement')
  return response.json()
}

export async function applyJudge(judgeId: number, resultId: number, judgeProvider?: string, judgeModel?: string): Promise<Judgement> {
  const response = await fetch(`${API_BASE}/judges/${judgeId}/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      result_ids: [resultId], // Single result only
      judge_provider: judgeProvider || 'anthropic',
      judge_model: judgeModel || 'claude-sonnet-4-20250514',
    }),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to apply judge' }))
    throw new Error(error.detail || 'Failed to apply judge')
  }
  return response.json()
}

export async function judgeResult(judgeId: number, resultId: number, judgeProvider?: string, judgeModel?: string): Promise<Judgement> {
  const response = await fetch(`${API_BASE}/judges/${judgeId}/judge-result/${resultId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      judge_provider: judgeProvider || 'anthropic',
      judge_model: judgeModel || 'claude-sonnet-4-20250514',
    }),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to judge result' }))
    throw new Error(error.detail || 'Failed to judge result')
  }
  return response.json()
}
