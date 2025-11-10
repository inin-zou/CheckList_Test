"use client"

import { useState, useEffect } from "react"
import { FrostedCard } from "@/components/frosted-card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Play, Loader2, CheckCircle } from "lucide-react"

interface Template {
  id: number
  template_name: string
}

export default function RunChecklistPage() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null)
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState<any>(null)

  useEffect(() => {
    fetchTemplates()
  }, [])

  const fetchTemplates = async () => {
    try {
      const response = await fetch("/api/checklist/templates")
      if (response.ok) {
        const data = await response.json()
        setTemplates(data)
      }
    } catch (error) {
      console.error("[v0] Failed to fetch templates:", error)
    }
  }

  const handleRun = async () => {
    if (!selectedTemplate) return

    setRunning(true)
    setResult(null)

    try {
      const response = await fetch("/api/checklist/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ template_id: selectedTemplate }),
      })
      if (response.ok) {
        const data = await response.json()
        setResult(data)
      }
    } catch (error) {
      console.error("[v0] Failed to run checklist:", error)
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="container mx-auto px-6 py-12 max-w-5xl">
      <h1 className="text-4xl font-bold mb-2">Run Checklist</h1>
      <p className="text-muted-foreground mb-8">Execute a checklist template and view AI-extracted results</p>

      <FrostedCard className="p-8 mb-6">
        <h2 className="text-xl font-semibold mb-4">Select Template</h2>
        <div className="space-y-4">
          <Select
            value={selectedTemplate?.toString()}
            onValueChange={(value) => setSelectedTemplate(Number.parseInt(value))}
          >
            <SelectTrigger>
              <SelectValue placeholder="Choose a checklist template..." />
            </SelectTrigger>
            <SelectContent>
              {templates.map((template) => (
                <SelectItem key={template.id} value={template.id.toString()}>
                  {template.template_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button
            onClick={handleRun}
            disabled={!selectedTemplate || running}
            className="w-full bg-gradient-to-r from-blue-500 to-cyan-400 hover:from-blue-600 hover:to-cyan-500"
          >
            {running ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Running Checklist...
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Run Checklist
              </>
            )}
          </Button>
        </div>
      </FrostedCard>

      {result && (
        <FrostedCard className="p-8">
          <div className="flex items-center gap-3 mb-6">
            <CheckCircle className="h-8 w-8 text-green-500" />
            <div>
              <h2 className="text-xl font-semibold">Checklist Complete</h2>
              <p className="text-sm text-muted-foreground">Results have been generated successfully</p>
            </div>
          </div>

          <div className="bg-muted/50 rounded-lg p-6">
            <pre className="text-sm overflow-x-auto">{JSON.stringify(result, null, 2)}</pre>
          </div>
        </FrostedCard>
      )}
    </div>
  )
}
