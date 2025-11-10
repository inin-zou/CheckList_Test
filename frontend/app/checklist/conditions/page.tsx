"use client"

import { useState, useEffect } from "react"
import { FrostedCard } from "@/components/frosted-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Plus, Edit, Trash2, Save, X } from "lucide-react"

interface Condition {
  id: number
  condition_name: string
  condition_logic: string
}

export default function ConditionsPage() {
  const [conditions, setConditions] = useState<Condition[]>([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [showNewForm, setShowNewForm] = useState(false)
  const [formData, setFormData] = useState({
    condition_name: "",
    condition_logic: "",
  })

  useEffect(() => {
    fetchConditions()
  }, [])

  const fetchConditions = async () => {
    try {
      const response = await fetch("/api/checklist/conditions")
      if (response.ok) {
        const data = await response.json()
        setConditions(data)
      }
    } catch (error) {
      console.error("[v0] Failed to fetch conditions:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    try {
      const response = await fetch("/api/checklist/conditions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      })
      if (response.ok) {
        setFormData({ condition_name: "", condition_logic: "" })
        setShowNewForm(false)
        fetchConditions()
      }
    } catch (error) {
      console.error("[v0] Failed to create condition:", error)
    }
  }

  const handleUpdate = async (id: number) => {
    try {
      const response = await fetch(`/api/checklist/conditions/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      })
      if (response.ok) {
        setEditingId(null)
        setFormData({ condition_name: "", condition_logic: "" })
        fetchConditions()
      }
    } catch (error) {
      console.error("[v0] Failed to update condition:", error)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this condition?")) return

    try {
      const response = await fetch(`/api/checklist/conditions/${id}`, {
        method: "DELETE",
      })
      if (response.ok) {
        fetchConditions()
      }
    } catch (error) {
      console.error("[v0] Failed to delete condition:", error)
    }
  }

  const startEdit = (condition: Condition) => {
    setEditingId(condition.id)
    setFormData({
      condition_name: condition.condition_name,
      condition_logic: condition.condition_logic,
    })
  }

  return (
    <div className="container mx-auto px-6 py-12 max-w-5xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Conditions</h1>
          <p className="text-muted-foreground">Define compliance conditions and evaluation logic</p>
        </div>
        <Button
          onClick={() => setShowNewForm(true)}
          className="bg-gradient-to-r from-blue-500 to-cyan-400 hover:from-blue-600 hover:to-cyan-500"
        >
          <Plus className="mr-2 h-4 w-4" />
          New Condition
        </Button>
      </div>

      {showNewForm && (
        <FrostedCard className="p-6 mb-6">
          <h3 className="font-semibold mb-4">Create New Condition</h3>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Condition Name</label>
              <Input
                value={formData.condition_name}
                onChange={(e) => setFormData({ ...formData, condition_name: e.target.value })}
                placeholder="Enter condition name..."
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Condition Logic</label>
              <Textarea
                value={formData.condition_logic}
                onChange={(e) => setFormData({ ...formData, condition_logic: e.target.value })}
                placeholder="Enter evaluation logic..."
                rows={4}
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleCreate}>
                <Save className="mr-2 h-4 w-4" />
                Save
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setShowNewForm(false)
                  setFormData({ condition_name: "", condition_logic: "" })
                }}
              >
                <X className="mr-2 h-4 w-4" />
                Cancel
              </Button>
            </div>
          </div>
        </FrostedCard>
      )}

      <div className="space-y-4">
        {loading ? (
          <FrostedCard className="p-8 text-center">
            <p className="text-muted-foreground">Loading conditions...</p>
          </FrostedCard>
        ) : conditions.length === 0 ? (
          <FrostedCard className="p-8 text-center">
            <p className="text-muted-foreground">No conditions created yet</p>
          </FrostedCard>
        ) : (
          conditions.map((condition) => (
            <FrostedCard key={condition.id} className="p-6">
              {editingId === condition.id ? (
                <div className="space-y-4">
                  <Input
                    value={formData.condition_name}
                    onChange={(e) => setFormData({ ...formData, condition_name: e.target.value })}
                  />
                  <Textarea
                    value={formData.condition_logic}
                    onChange={(e) => setFormData({ ...formData, condition_logic: e.target.value })}
                    rows={4}
                  />
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => handleUpdate(condition.id)}>
                      <Save className="mr-2 h-4 w-4" />
                      Save
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setEditingId(null)
                        setFormData({ condition_name: "", condition_logic: "" })
                      }}
                    >
                      <X className="mr-2 h-4 w-4" />
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold mb-2">{condition.condition_name}</h3>
                    <pre className="text-sm text-muted-foreground bg-muted/50 p-3 rounded-lg overflow-x-auto">
                      {condition.condition_logic}
                    </pre>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <Button variant="ghost" size="icon" onClick={() => startEdit(condition)}>
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(condition.id)}>
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              )}
            </FrostedCard>
          ))
        )}
      </div>
    </div>
  )
}
