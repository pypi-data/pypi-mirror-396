import { useState, useEffect } from 'react'
import { AlertTriangle, CheckCircle, Shield, AlertOctagon } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

function App() {
  const [metrics, setMetrics] = useState<any[]>([])
  const [selectedMetric, setSelectedMetric] = useState<any>(null)
  const [validationResult, setValidationResult] = useState<any>(null)

  useEffect(() => {
    fetch('http://localhost:8000/api/metrics')
      .then(res => res.json())
      .then(data => {
        setMetrics(data)
      })
  }, [])

  const validateMetric = async (metric: any) => {
    const res = await fetch('http://localhost:8000/api/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(metric)
    })
    const data = await res.json()
    setValidationResult(data)
  }

  const handleSave = async (metric: any) => {
    // Save logic here
    await fetch('http://localhost:8000/api/metrics/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ metric_id: metric.metric_id, content: metric })
    })
    alert("Saved!")
    setMetrics(metrics.map(m => m.metric_id === metric.metric_id ? metric : m))
    validateMetric(metric)
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-2">
            <Shield className="h-8 w-8 text-blue-600" />
            ODGS Explorer
          </h1>
          <p className="text-slate-500">AI Safety & Governance Protocol</p>
        </div>
        <div className="flex gap-4">
          <div className="bg-white p-3 rounded-lg shadow-sm border flex items-center gap-3">
            <div className="text-right">
              <p className="text-xs text-slate-400 uppercase font-bold">Protocol Status</p>
              <p className="text-sm font-semibold text-green-600">EU AI Act Compliant</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500" />
          </div>
        </div>
      </header>

      <div className="grid grid-cols-12 gap-6">
        {/* Sidebar: Metrics List */}
        <div className="col-span-3">
          <Card className="h-[calc(100vh-12rem)] overflow-hidden flex flex-col">
            <CardHeader className="bg-slate-100 border-b py-3">
              <CardTitle className="text-sm font-medium">Standard Metrics ({metrics.length})</CardTitle>
            </CardHeader>
            <div className="flex-1 overflow-y-auto p-2 space-y-2">
              {metrics.map(m => (
                <div
                  key={m.metric_id}
                  onClick={() => { setSelectedMetric(m); validateMetric(m); }}
                  className={`p-3 rounded-md cursor-pointer border hover:border-blue-300 transition-colors ${selectedMetric?.metric_id === m.metric_id ? 'bg-blue-50 border-blue-200' : 'bg-white border-transparent'}`}
                >
                  <p className="font-semibold text-sm">{m.name}</p>
                  <p className="text-xs text-slate-500">{m.metric_id}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Main: Editor */}
        <div className="col-span-6 space-y-6">
          {selectedMetric ? (
            <MetricEditor metric={selectedMetric} onSave={handleSave} validation={validationResult} />
          ) : (
            <div className="h-full flex items-center justify-center text-slate-400">
              Select a metric to edit
            </div>
          )}
        </div>

        {/* Right: Code Preview */}
        <div className="col-span-3">
          <CodePreview metric={selectedMetric} />
        </div>
      </div>
    </div>
  )
}

function MetricEditor({ metric, onSave, validation }: any) {
  const [localMetric, setLocalMetric] = useState(metric)

  useEffect(() => { setLocalMetric(metric) }, [metric])

  const isHallucinating = validation && validation.issues.length > 0

  return (
    <Card className="border-t-4 border-t-blue-600 shadow-md">
      <CardHeader>
        <CardTitle className="flex justify-between items-center">
          {localMetric.name}
          {isHallucinating ? (
            <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-xs flex items-center gap-1">
              <AlertTriangle className="h-3 w-3" /> Potential Hallucination
            </span>
          ) : (
            <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs flex items-center gap-1">
              <CheckCircle className="h-3 w-3" /> AI Safe
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-xs font-bold text-slate-500 uppercase">Definition (Human Truth)</label>
          <textarea
            className="w-full mt-1 p-2 border rounded-md text-sm min-h-[80px]"
            value={localMetric.definition}
            onChange={e => setLocalMetric({ ...localMetric, definition: e.target.value })}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-bold text-slate-500 uppercase">Abstract Logic</label>
            <input
              className={`w-full mt-1 p-2 border rounded-md text-sm font-mono ${isHallucinating && !localMetric.calculation_logic?.abstract ? 'border-red-500 bg-red-50' : ''}`}
              value={localMetric.calculation_logic?.abstract || ''}
              onChange={e => setLocalMetric({
                ...localMetric,
                calculation_logic: { ...localMetric.calculation_logic, abstract: e.target.value }
              })}
            />
            {isHallucinating && !localMetric.calculation_logic?.abstract && (
              <p className="text-xs text-red-600 mt-1">Required to prevent hallucination.</p>
            )}
          </div>
          <div>
            <label className="text-xs font-bold text-slate-500 uppercase">SQL Standard</label>
            <input
              className="w-full mt-1 p-2 border rounded-md text-sm font-mono"
              value={localMetric.calculation_logic?.sql_standard || ''}
              onChange={e => setLocalMetric({
                ...localMetric,
                calculation_logic: { ...localMetric.calculation_logic, sql_standard: e.target.value }
              })}
            />
          </div>
        </div>

        <Button className="w-full" onClick={() => onSave(localMetric)}>
          Save & Validate
        </Button>

        {validation?.issues?.length > 0 && (
          <div className="bg-red-50 p-4 rounded-md border border-red-200">
            <h4 className="text-red-800 font-bold text-sm mb-2 flex items-center gap-2">
              <AlertOctagon className="h-4 w-4" /> Safety Violations
            </h4>
            <ul className="text-xs text-red-700 list-disc list-inside">
              {validation.issues.map((issue: string, i: number) => (
                <li key={i}>{issue}</li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function CodePreview({ metric }: any) {
  if (!metric) return null
  return (
    <Card className="bg-slate-900 text-slate-300 h-full">
      <CardHeader>
        <CardTitle className="text-slate-100 text-sm">Compiled Output</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-xs font-bold text-slate-500 uppercase block mb-1">dbt (SQL)</label>
          <pre className="bg-black p-3 rounded-md text-xs font-mono overflow-x-auto text-green-400">
            {`SELECT \n  ${metric.calculation_logic?.sql_standard || '-- Missing Logic'} \nAS ${metric.name}`}
          </pre>
        </div>
        <div>
          <label className="text-xs font-bold text-slate-500 uppercase block mb-1">Power BI (DAX)</label>
          <pre className="bg-black p-3 rounded-md text-xs font-mono overflow-x-auto text-yellow-400">
            {`${metric.name} = \n${metric.calculation_logic?.dax_pattern || '-- Missing Logic'}`}
          </pre>
        </div>
      </CardContent>
    </Card>
  )
}

export default App
