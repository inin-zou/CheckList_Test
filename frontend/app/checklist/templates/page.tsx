"use client"

import { useState, useEffect } from "react"
import { FrostedCard } from "@/components/frosted-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Trash2, Save, X } from "lucide-react"

interface Template {
  id: string
  name: string
  description?: string
  created_at: string
}

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [showNewForm, setShowNewForm] = useState(false)
  const [templateName, setTemplateName] = useState("")

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
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    try {
      const response = await fetch("/api/checklist/templates", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: templateName }),
      })
      if (response.ok) {
        setTemplateName("")
        setShowNewForm(false)
        fetchTemplates()
      }
    } catch (error) {
      console.error("[v0] Failed to create template:", error)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this template?")) return

    try {
      const response = await fetch(`/api/checklist/templates/${id}`, {
        method: "DELETE",
      })
      if (response.ok) {
        fetchTemplates()
      }
    } catch (error) {
      console.error("[v0] Failed to delete template:", error)
    }
  }

  return (
    <div className="container mx-auto px-6 py-12 max-w-5xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Checklist Templates</h1>
          <p className="text-muted-foreground">Create and manage verification templates</p>
        </div>
        <Button
          onClick={() => setShowNewForm(true)}
          className="bg-gradient-to-r from-blue-500 to-cyan-400 hover:from-blue-600 hover:to-cyan-500"
        >
          <Plus className="mr-2 h-4 w-4" />
          New Template
        </Button>
      </div>

      {showNewForm && (
        <FrostedCard className="p-6 mb-6">
          <h3 className="font-semibold mb-4">Create New Template</h3>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Template Name</label>
              <Input
                value={templateName}
                onChange={(e) => setTemplateName(e.target.value)}
                placeholder="Enter template name..."
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleCreate}>
                <Save className="mr-2 h-4 w-4" />
                Create
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setShowNewForm(false)
                  setTemplateName("")
                }}
              >
                <X className="mr-2 h-4 w-4" />
                Cancel
              </Button>
            </div>
          </div>
        </FrostedCard>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {loading ? (
          <FrostedCard className="p-8 text-center col-span-full">
            <p className="text-muted-foreground">Loading templates...</p>
          </FrostedCard>
        ) : templates.length === 0 ? (
          <FrostedCard className="p-8 text-center col-span-full">
            <p className="text-muted-foreground">No templates created yet</p>
          </FrostedCard>
        ) : (
          templates.map((template) => (
            <FrostedCard key={template.id} className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold mb-2">{template.name}</h3>
                  {template.description && (
                    <p className="text-sm text-muted-foreground mb-2">{template.description}</p>
                  )}
                  <p className="text-sm text-muted-foreground">
                    Created: {new Date(template.created_at).toLocaleDateString()}
                  </p>
                </div>
                <Button variant="ghost" size="icon" onClick={() => handleDelete(template.id)}>
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              </div>
            </FrostedCard>
          ))
        )}
      </div>
    </div>
  )
}
