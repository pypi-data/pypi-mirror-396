import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getScenario, listScenarios, listJudges } from '../api'
import { Card, Select, Textarea, Checkbox } from './ui'

interface ScenarioFormProps {
  selectedScenarioId: string
  onScenarioIdChange: (id: string) => void
  codeType: string
  onCodeTypeChange: (type: string) => void
  codeRef: string
  onCodeRefChange: (ref: string) => void
  prompt: string
  onPromptChange: (prompt: string) => void
  showLoadFromExisting?: boolean
  excludeScenarioIds?: number[]
  // Judge settings (optional)
  showJudgeSettings?: boolean
  enableJudge?: boolean
  onEnableJudgeChange?: (enabled: boolean) => void
  judgeGuidance?: string
  onJudgeGuidanceChange?: (guidance: string) => void
  autoJudge?: boolean
  onAutoJudgeChange?: (auto: boolean) => void
}

export function ScenarioForm({
  selectedScenarioId,
  onScenarioIdChange,
  codeType,
  onCodeTypeChange,
  codeRef,
  onCodeRefChange,
  prompt,
  onPromptChange,
  showLoadFromExisting = true,
  excludeScenarioIds = [],
  // Judge settings
  showJudgeSettings = false,
  enableJudge = false,
  onEnableJudgeChange,
  judgeGuidance = '',
  onJudgeGuidanceChange,
  autoJudge = true,
  onAutoJudgeChange,
}: ScenarioFormProps) {
  const { data: scenariosData } = useQuery({
    queryKey: ['scenarios'],
    queryFn: listScenarios,
  })

  const { data: scenarioData } = useQuery({
    queryKey: ['scenario', selectedScenarioId],
    queryFn: () => getScenario(Number(selectedScenarioId!)),
    enabled: !!selectedScenarioId,
  })

  // Get existing judge for selected scenario
  const { data: existingJudges } = useQuery({
    queryKey: ['judges', selectedScenarioId],
    queryFn: () => listJudges(Number(selectedScenarioId!)),
    enabled: !!selectedScenarioId && showJudgeSettings,
  })

  // Load scenario data when selected
  useEffect(() => {
    if (scenarioData?.scenario) {
      const s = scenarioData.scenario
      onPromptChange(s.prompt)
      onCodeTypeChange(s.code_type)
      if (s.code_ref) {
        if (s.code_type === 'github') {
          const ref = s.code_ref
          onCodeRefChange(`${ref.owner}/${ref.repo}@${ref.commit_sha || ref.branch || 'main'}`)
        } else if (s.code_type === 'local') {
          onCodeRefChange(s.code_ref.path)
        }
      }
    }
  }, [scenarioData, onPromptChange, onCodeTypeChange, onCodeRefChange])

  // Load existing judge guidance when scenario has a judge
  useEffect(() => {
    if (existingJudges && existingJudges.length > 0 && onJudgeGuidanceChange && onEnableJudgeChange) {
      const latestJudge = existingJudges[0]
      onEnableJudgeChange(true)
      onJudgeGuidanceChange(latestJudge.guidance || '')
    }
  }, [existingJudges, onJudgeGuidanceChange, onEnableJudgeChange])

  const getCodeRefDisplay = (scenario: any) => {
    if (!scenario.code_ref) return 'Empty'
    if (scenario.code_type === 'github') {
      return `${scenario.code_ref.owner}/${scenario.code_ref.repo}`
    } else if (scenario.code_type === 'local') {
      return scenario.code_ref.path
    }
    return '—'
  }

  const availableScenarios = scenariosData?.scenarios.filter(
    s => !excludeScenarioIds.includes(s.id)
  ) || []

  return (
    <>
    <Card>
      <Card.Header>
        <Card.Title>Scenario Details</Card.Title>
      </Card.Header>
      <Card.Content className="space-y-4">
        {showLoadFromExisting && (
          <Select
            label="Load from existing scenario (optional)"
            value={selectedScenarioId}
            onChange={(e) => {
              onScenarioIdChange(e.target.value)
              if (!e.target.value) {
                onPromptChange('')
                onCodeRefChange('')
                onCodeTypeChange('github')
              }
            }}
          >
            <option value="">Create new scenario</option>
            {availableScenarios.slice(0, 20).map((scenario: any) => (
              <option key={scenario.id} value={scenario.id}>
                #{scenario.id}: {scenario.prompt.substring(0, 50)}
                {scenario.prompt.length > 50 ? '...' : ''} ({getCodeRefDisplay(scenario)})
              </option>
            ))}
          </Select>
        )}

        <Select
          label="Code Type"
          value={codeType}
          onChange={(e) => onCodeTypeChange(e.target.value)}
          options={[
            { value: 'github', label: 'GitHub' },
            { value: 'local', label: 'Local' },
            { value: 'empty', label: 'Empty' },
          ]}
        />

        {codeType !== 'empty' && (
          <div className="space-y-1.5">
            <label className="block text-sm text-text-secondary">
              Code Reference {codeType === 'github' && '(owner/repo@sha)'}
            </label>
            <input
              type="text"
              value={codeRef}
              onChange={(e) => onCodeRefChange(e.target.value)}
              className="w-full px-3 py-2 bg-surface border border-border rounded text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-border-focus focus:ring-1 focus:ring-border-focus"
              placeholder={codeType === 'github' ? 'owner/repo@sha' : '/path/to/repo'}
            />
          </div>
        )}

        <Textarea
          label="Prompt"
          value={prompt}
          onChange={(e) => onPromptChange(e.target.value)}
          rows={6}
          mono
          placeholder="Task instructions for the agent..."
          required
        />
      </Card.Content>
    </Card>

    {/* Judge Settings Card (optional) */}
    {showJudgeSettings && (
      <Card className="mt-4">
        <Card.Header>
          <div className="flex items-center justify-between">
            <Card.Title>LLM Judge</Card.Title>
            <Checkbox
              checked={enableJudge}
              onChange={(e) => onEnableJudgeChange?.(e.target.checked)}
              label="Enable"
            />
          </div>
        </Card.Header>
        {enableJudge && (
          <Card.Content className="space-y-4">
            <div>
              <Textarea
                label="Judge Guidance"
                value={judgeGuidance}
                onChange={(e) => onJudgeGuidanceChange?.(e.target.value)}
                placeholder="Describe what makes a successful result. E.g., 'The code should compile without errors, all tests should pass, and the feature should work as described in the prompt.'"
                rows={4}
              />
              <p className="mt-1 text-xs text-text-tertiary">
                Provide criteria for the LLM judge to evaluate results. Clear, specific criteria work best.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                checked={autoJudge}
                onChange={(e) => onAutoJudgeChange?.(e.target.checked)}
                label="Auto-judge when run completes"
              />
            </div>
            {existingJudges && existingJudges.length > 0 && (
              <div className="p-3 bg-accent-muted rounded-lg text-xs text-text-secondary">
                <strong className="text-text-primary">Note:</strong> This scenario already has a judge configured. 
                Updating the guidance will update the existing judge.
              </div>
            )}
            {(!existingJudges || existingJudges.length === 0) && (
              <div className="p-3 bg-surface-2 rounded-lg text-xs text-text-secondary">
                <strong className="text-text-primary">Note:</strong> New judges without training samples may have lower alignment with human judgment. 
                For best results, rate a few results manually first, then train the judge.
              </div>
            )}
          </Card.Content>
        )}
      </Card>
    )}
    </>
  )
}

