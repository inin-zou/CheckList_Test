"use client"

import { useState } from "react"
import { FrostedCard } from "@/components/frosted-card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Send, RefreshCw, Loader2 } from "lucide-react"

export default function RAGPage() {
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [loading, setLoading] = useState(false)
  const [rebuilding, setRebuilding] = useState(false)

  const handleAsk = async () => {
    if (!question.trim()) return

    setLoading(true)
    setAnswer("")

    try {
      const response = await fetch("/api/rag/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      })
      if (response.ok) {
        const data = await response.json()
        setAnswer(data.answer || JSON.stringify(data, null, 2))
      }
    } catch (error) {
      console.error("[v0] Failed to ask question:", error)
      setAnswer("Error: Failed to get answer")
    } finally {
      setLoading(false)
    }
  }

  const handleRebuildIndex = async () => {
    if (!confirm("Are you sure you want to rebuild the RAG index?")) return

    setRebuilding(true)

    try {
      const response = await fetch("/api/rag/rebuild-index", {
        method: "POST",
      })
      if (response.ok) {
        alert("Index rebuilt successfully")
      }
    } catch (error) {
      console.error("[v0] Failed to rebuild index:", error)
    } finally {
      setRebuilding(false)
    }
  }

  return (
    <div className="container mx-auto px-6 py-12 max-w-5xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">RAG Query</h1>
          <p className="text-muted-foreground">Ask questions about your uploaded documents</p>
        </div>
        <Button onClick={handleRebuildIndex} disabled={rebuilding} variant="outline">
          {rebuilding ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Rebuilding...
            </>
          ) : (
            <>
              <RefreshCw className="mr-2 h-4 w-4" />
              Rebuild Index
            </>
          )}
        </Button>
      </div>

      <FrostedCard className="p-8 mb-6">
        <h2 className="text-xl font-semibold mb-4">Ask a Question</h2>
        <div className="space-y-4">
          <Textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What would you like to know about your documents?"
            rows={4}
          />
          <Button
            onClick={handleAsk}
            disabled={!question.trim() || loading}
            className="w-full bg-gradient-to-r from-blue-500 to-cyan-400 hover:from-blue-600 hover:to-cyan-500"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Ask Question
              </>
            )}
          </Button>
        </div>
      </FrostedCard>

      {answer && (
        <FrostedCard className="p-8">
          <h2 className="text-xl font-semibold mb-4">Answer</h2>
          <div className="bg-muted/50 rounded-lg p-6">
            <pre className="text-sm whitespace-pre-wrap">{answer}</pre>
          </div>
        </FrostedCard>
      )}
    </div>
  )
}
