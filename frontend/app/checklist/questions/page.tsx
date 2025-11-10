"use client"

import { useState, useEffect } from "react"
import { FrostedCard } from "@/components/frosted-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Plus, Edit, Trash2, Save, X } from "lucide-react"

interface Question {
  id: string
  question: string
  question_type?: string
  context?: string
  required?: boolean
}

export default function QuestionsPage() {
  const [questions, setQuestions] = useState<Question[]>([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [showNewForm, setShowNewForm] = useState(false)
  const [formData, setFormData] = useState({
    question: "",
    question_type: "text",
    context: "",
    required: true,
  })

  useEffect(() => {
    fetchQuestions()
  }, [])

  const fetchQuestions = async () => {
    try {
      const response = await fetch("/api/checklist/questions")
      if (response.ok) {
        const data = await response.json()
        setQuestions(data)
      }
    } catch (error) {
      console.error("[v0] Failed to fetch questions:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    try {
      const response = await fetch("/api/checklist/questions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      })
      if (response.ok) {
        setFormData({ question: "", question_type: "text", context: "", required: true })
        setShowNewForm(false)
        fetchQuestions()
      }
    } catch (error) {
      console.error("[v0] Failed to create question:", error)
    }
  }

  const handleUpdate = async (id: string) => {
    try {
      const response = await fetch(`/api/checklist/questions/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      })
      if (response.ok) {
        setEditingId(null)
        setFormData({ question: "", question_type: "text", context: "", required: true })
        fetchQuestions()
      }
    } catch (error) {
      console.error("[v0] Failed to update question:", error)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this question?")) return

    try {
      const response = await fetch(`/api/checklist/questions/${id}`, {
        method: "DELETE",
      })
      if (response.ok) {
        fetchQuestions()
      }
    } catch (error) {
      console.error("[v0] Failed to delete question:", error)
    }
  }

  const startEdit = (question: Question) => {
    setEditingId(question.id)
    setFormData({
      question: question.question,
      question_type: question.question_type || "text",
      context: question.context || "",
      required: question.required ?? true,
    })
  }

  return (
    <div className="container mx-auto px-6 py-12 max-w-5xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Questions</h1>
          <p className="text-muted-foreground">Manage checklist verification questions</p>
        </div>
        <Button
          onClick={() => setShowNewForm(true)}
          className="bg-gradient-to-r from-blue-500 to-cyan-400 hover:from-blue-600 hover:to-cyan-500"
        >
          <Plus className="mr-2 h-4 w-4" />
          New Question
        </Button>
      </div>

      {showNewForm && (
        <FrostedCard className="p-6 mb-6">
          <h3 className="font-semibold mb-4">Create New Question</h3>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Question Text</label>
              <Textarea
                value={formData.question}
                onChange={(e) => setFormData({ ...formData, question: e.target.value })}
                placeholder="Enter your question..."
                rows={3}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Context</label>
              <Textarea
                value={formData.context}
                onChange={(e) => setFormData({ ...formData, context: e.target.value })}
                placeholder="Provide context for answering this question..."
                rows={2}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Question Type</label>
              <Input
                value={formData.question_type}
                onChange={(e) => setFormData({ ...formData, question_type: e.target.value })}
                placeholder="text, date, number, etc."
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
                  setFormData({ question: "", question_type: "text", context: "", required: true })
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
            <p className="text-muted-foreground">Loading questions...</p>
          </FrostedCard>
        ) : questions.length === 0 ? (
          <FrostedCard className="p-8 text-center">
            <p className="text-muted-foreground">No questions created yet</p>
          </FrostedCard>
        ) : (
          questions.map((question) => (
            <FrostedCard key={question.id} className="p-6">
              {editingId === question.id ? (
                <div className="space-y-4">
                  <Textarea
                    value={formData.question}
                    onChange={(e) => setFormData({ ...formData, question: e.target.value })}
                    rows={3}
                  />
                  <Textarea
                    value={formData.context}
                    onChange={(e) => setFormData({ ...formData, context: e.target.value })}
                    rows={2}
                  />
                  <Input
                    value={formData.question_type}
                    onChange={(e) => setFormData({ ...formData, question_type: e.target.value })}
                  />
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => handleUpdate(question.id)}>
                      <Save className="mr-2 h-4 w-4" />
                      Save
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setEditingId(null)
                        setFormData({ question: "", question_type: "text", context: "", required: true })
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
                    <p className="font-medium mb-2">{question.question}</p>
                    {question.context && (
                      <p className="text-sm text-muted-foreground mb-1">Context: {question.context}</p>
                    )}
                    <p className="text-sm text-muted-foreground">Type: {question.question_type || "text"}</p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="icon" onClick={() => startEdit(question)}>
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(question.id)}>
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
