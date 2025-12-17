import { useState, useEffect, useCallback } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { createScenario, createRun, listExecutors, getExecutorModels, getHarnessDetail, listDrivers, ExecutorInfo, createJudge, listJudges, updateJudge, judgeResult, getResult } from '../api'
import { PageHeader, Card, Select, Button } from './ui'
import { ScenarioForm } from './ScenarioForm'

export default function RunCreate() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const urlScenarioId = searchParams.get('scenario')
  const urlExecutors = searchParams.get('executors')
  
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>(urlScenarioId || '')
  const [codeType, setCodeType] = useState('github')
  const [codeRef, setCodeRef] = useState('')
  const [prompt, setPrompt] = useState('')
  const [executors, setExecutors] = useState<string[]>(
    urlExecutors ? urlExecutors.split(',').filter(Boolean) : ['']
  )
  const [driver, setDriver] = useState<string>('local')
  
  // Judge settings
  const [enableJudge, setEnableJudge] = useState(false)
  const [judgeGuidance, setJudgeGuidance] = useState('')
  const [autoJudge, setAutoJudge] = useState(true) // Auto-judge when run completes

  const { data: executorsData } = useQuery({
    queryKey: ['executors'],
    queryFn: listExecutors,
  })

  const { data: driversData } = useQuery({
    queryKey: ['drivers'],
    queryFn: listDrivers,
  })

  useEffect(() => {
    if (urlScenarioId) {
      setSelectedScenarioId(urlScenarioId)
    }
  }, [urlScenarioId])

  useEffect(() => {
    if (urlExecutors) {
      const executorList = urlExecutors.split(',').filter(Boolean)
      if (executorList.length > 0) {
        setExecutors(executorList)
      }
    }
  }, [urlExecutors])

  const createScenarioMutation = useMutation({
    mutationFn: createScenario,
    onSuccess: async (scenario) => {
      // Create or update judge if enabled
      let judgeId: number | null = null
      if (enableJudge && judgeGuidance.trim()) {
        try {
          // Check if scenario already has a judge
          const existingJudges = await listJudges(scenario.id)
          if (existingJudges.length > 0) {
            // Update existing judge
            const updated = await updateJudge(existingJudges[0].id, {
              scenario_id: scenario.id,
              guidance: judgeGuidance.trim(),
              training_sample_ids: existingJudges[0].training_sample_ids,
              test_sample_ids: existingJudges[0].test_sample_ids,
            })
            judgeId = updated.id
          } else {
            // Create new judge
            const newJudge = await createJudge({
              scenario_id: scenario.id,
              guidance: judgeGuidance.trim(),
              training_sample_ids: [],
              test_sample_ids: [],
            })
            judgeId = newJudge.id
          }
        } catch (error) {
          console.error('Failed to create/update judge:', error)
        }
      }

      const validExecutors = executors.filter((e) => e.trim())
      if (validExecutors.length === 0) {
        navigate(`/scenario/${scenario.id}`)
        return
      }

      // Create all runs and collect result IDs
      const resultIds: number[] = []
      for (const executorSpec of validExecutors) {
        try {
          const response = await createRun({
            scenario_id: scenario.id,
            executor_spec: executorSpec.trim(),
            driver: driver,
          })
          resultIds.push(response.result_id)
        } catch (error) {
          console.error('Failed to create run:', error)
        }
      }

      // If auto-judge is enabled, poll for completion and judge
      if (autoJudge && judgeId && resultIds.length > 0) {
        // Start background polling for each result
        resultIds.forEach((resultId) => {
          pollAndJudge(resultId, judgeId!)
        })
      }

      // Navigate based on number of executors
      if (resultIds.length === 1) {
        navigate(`/result/${resultIds[0]}`)
      } else if (resultIds.length > 1) {
        navigate(`/compare?ids=${resultIds.join(',')}&scenario=${scenario.id}`)
      } else {
        navigate(`/scenario/${scenario.id}`)
      }
    },
  })

  // Poll for result completion and then judge
  const pollAndJudge = async (resultId: number, judgeId: number) => {
    const maxAttempts = 360 // 30 minutes at 5s intervals
    let attempts = 0
    
    const poll = async () => {
      attempts++
      if (attempts > maxAttempts) {
        console.log(`[Auto-judge] Gave up polling for result ${resultId} after ${maxAttempts} attempts`)
        return
      }
      
      try {
        const result = await getResult(resultId)
        if (result.status === 'completed') {
          console.log(`[Auto-judge] Result ${resultId} completed, running judge...`)
          try {
            await judgeResult(judgeId, resultId)
            console.log(`[Auto-judge] Successfully judged result ${resultId}`)
          } catch (error) {
            console.error(`[Auto-judge] Failed to judge result ${resultId}:`, error)
          }
        } else if (result.status === 'failed' || result.status === 'timeout' || result.status === 'infra_failure') {
          console.log(`[Auto-judge] Result ${resultId} ended with status ${result.status}, skipping judge`)
        } else {
          // Still running, poll again
          setTimeout(poll, 5000)
        }
      } catch (error) {
        console.error(`[Auto-judge] Failed to poll result ${resultId}:`, error)
        // Retry anyway
        setTimeout(poll, 5000)
      }
    }
    
    // Start polling after a short delay
    setTimeout(poll, 2000)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    let code_ref: any = null
    if (codeType === 'github') {
      const [owner, repo] = codeRef.split('/')
      const parts = repo.split('@')
      code_ref = { owner, repo: parts[0], commit_sha: parts[1] || 'main' }
    } else if (codeType === 'local') {
      code_ref = { path: codeRef }
    }

    createScenarioMutation.mutate({
      code_type: codeType,
      code_ref,
      prompt,
    })
  }

  const breadcrumbs = selectedScenarioId
    ? [
        { label: 'Scenarios', path: '/scenarios' },
        { label: `Scenario ${selectedScenarioId}`, path: `/scenario/${selectedScenarioId}` },
        { label: 'New Run' },
      ]
    : [{ label: 'New Run' }]

  return (
    <div className="max-w-2xl mx-auto">
      <PageHeader
        breadcrumbs={breadcrumbs}
        title="Create Run"
        description="Define a scenario and select executors to run it"
      />

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Scenario Details with integrated Judge Settings */}
        <ScenarioForm
          selectedScenarioId={selectedScenarioId}
          onScenarioIdChange={setSelectedScenarioId}
          codeType={codeType}
          onCodeTypeChange={setCodeType}
          codeRef={codeRef}
          onCodeRefChange={setCodeRef}
          prompt={prompt}
          onPromptChange={setPrompt}
          showLoadFromExisting={true}
          // Judge settings
          showJudgeSettings={true}
          enableJudge={enableJudge}
          onEnableJudgeChange={setEnableJudge}
          judgeGuidance={judgeGuidance}
          onJudgeGuidanceChange={setJudgeGuidance}
          autoJudge={autoJudge}
          onAutoJudgeChange={setAutoJudge}
        />

        {/* Executors */}
        <Card>
          <Card.Header>
            <Card.Title>Executors</Card.Title>
          </Card.Header>
          <Card.Content className="space-y-3">
            {executors.map((executor, idx) => (
              <ExecutorSelector
                key={idx}
                index={idx}
                value={executor}
                executorsData={executorsData}
                onExecutorChange={setExecutors}
                canRemove={executors.length > 1}
              />
            ))}
            <button
              type="button"
              onClick={() => setExecutors([...executors, ''])}
              className="text-sm text-accent hover:text-accent-hover"
            >
              + Add Executor
            </button>
          </Card.Content>
        </Card>

        {/* Driver Selection */}
        <Card>
          <Card.Header>
            <Card.Title>Execution Driver</Card.Title>
          </Card.Header>
          <Card.Content>
            <Select
              label="Driver"
              value={driver}
              onChange={(e) => setDriver(e.target.value)}
              options={(driversData?.drivers || []).map(d => ({ value: d.id, label: d.name }))}
            />
            <p className="mt-2 text-xs text-text-tertiary">
              Select the execution environment. Local uses git worktrees, Docker/OrbStack use containers, Modal uses cloud execution.
            </p>
          </Card.Content>
        </Card>

        <Button
          type="submit"
          disabled={createScenarioMutation.isPending || !prompt.trim()}
          className="w-full"
        >
          {createScenarioMutation.isPending ? 'Creating...' : 'Create Run'}
        </Button>
      </form>
    </div>
  )
}

interface ExecutorSelectorProps {
  index: number
  value: string
  executorsData: { harnesses: ExecutorInfo[] } | undefined
  onExecutorChange: React.Dispatch<React.SetStateAction<string[]>>
  canRemove: boolean
}

function ExecutorSelector({ index, value, executorsData, onExecutorChange, canRemove }: ExecutorSelectorProps) {
  const [harness, setHarness] = useState('')
  const [provider, setProvider] = useState('')
  const [model, setModel] = useState('')

  // Parse initial value
  useEffect(() => {
    if (value) {
      const parts = value.split(':')
      if (parts.length >= 3) {
        setHarness(parts[0])
        setProvider(parts[1])
        setModel(parts[2])
      }
    }
  }, [value])

  // Load harness details to get providers and models
  const { data: harnessDetailData } = useQuery({
    queryKey: ['harness-detail', harness],
    queryFn: () => getHarnessDetail(harness),
    enabled: !!harness,
  })

  // Auto-select first provider when harness is selected
  useEffect(() => {
    if (harness && harnessDetailData && !provider) {
      const firstProvider = harnessDetailData.providers[0]
      if (firstProvider) {
        setProvider(firstProvider.id)
      }
    }
  }, [harness, harnessDetailData, provider])

  // Load models for selected harness/provider
  const { data: modelsData } = useQuery({
    queryKey: ['executor-models', harness, provider],
    queryFn: () => getExecutorModels(harness, provider),
    enabled: !!harness && !!provider,
  })

  // Auto-select first model when provider is selected
  useEffect(() => {
    if (provider && modelsData?.models && modelsData.models.length > 0 && !model) {
      const firstModel = modelsData.models[0]
      if (firstModel) {
        setModel(firstModel.id)
      }
    }
  }, [provider, modelsData, model])

  // Stable callback to update parent
  const updateParent = useCallback((newValue: string) => {
    onExecutorChange(prev => {
      const newExecutors = [...prev]
      newExecutors[index] = newValue
      return newExecutors
    })
  }, [index, onExecutorChange])

  // Sync local state to parent - compare before calling to prevent infinite loops
  useEffect(() => {
    const newValue = harness && provider && model ? `${harness}:${provider}:${model}` : ''
    if (newValue !== value) {
      updateParent(newValue)
    }
  }, [harness, provider, model, value, updateParent])

  const handleRemove = useCallback(() => {
    onExecutorChange(prev => prev.filter((_, i) => i !== index))
  }, [index, onExecutorChange])

  const selectedProviderModels = modelsData?.models || []

  return (
    <div className="flex gap-2 items-end">
      <div className="flex-1">
        <label className="block mb-1 text-xs text-text-tertiary">Harness</label>
        <select
          value={harness}
          onChange={(e) => {
            setHarness(e.target.value)
            setProvider('')
            setModel('')
          }}
          className="w-full px-3 py-2 bg-surface border border-border rounded text-sm text-text-primary focus:outline-none focus:border-border-focus focus:ring-1 focus:ring-border-focus"
        >
          <option value="">Select...</option>
          {executorsData?.harnesses.map((h) => (
            <option key={h.id} value={h.id}>
              {h.name}
            </option>
          ))}
        </select>
      </div>

      {harness && (
        <div className="flex-1">
          <label className="block mb-1 text-xs text-text-tertiary">Provider</label>
          <select
            value={provider}
            onChange={(e) => {
              setProvider(e.target.value)
              setModel('')
            }}
            className="w-full px-3 py-2 bg-surface border border-border rounded text-sm text-text-primary focus:outline-none focus:border-border-focus focus:ring-1 focus:ring-border-focus"
          >
            <option value="">Select...</option>
            {harnessDetailData?.providers.map((p) => (
              <option key={p.id} value={p.id}>
                {p.id}
              </option>
            ))}
          </select>
        </div>
      )}

      {provider && (
        <div className="flex-1">
          <label className="block mb-1 text-xs text-text-tertiary">Model</label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full px-3 py-2 bg-surface border border-border rounded text-sm text-text-primary focus:outline-none focus:border-border-focus focus:ring-1 focus:ring-border-focus"
          >
            <option value="">Select...</option>
            {selectedProviderModels.map((m: any) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {canRemove && (
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={handleRemove}
          className="text-status-error hover:text-status-error"
        >
          Remove
        </Button>
      )}
    </div>
  )
}
