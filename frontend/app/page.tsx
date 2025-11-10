"use client"

import { useEffect, useState } from "react"
import { FrostedCard } from "@/components/frosted-card"
import { Button } from "@/components/ui/button"
import { CheckCircle, FileText, Clock, AlertCircle } from "lucide-react"
import Link from "next/link"

interface ChecklistResult {
  id: number
  checklist_name: string
  created_at: string
  compliance_score?: number
}

export default function Dashboard() {
  const [recentResults, setRecentResults] = useState<ChecklistResult[]>([])
  const [templatesCount, setTemplatesCount] = useState<number>(0)
  const [documentsCount, setDocumentsCount] = useState<number>(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchRecentResults()
    fetchTemplatesCount()
    fetchDocumentsCount()
  }, [])

  const fetchRecentResults = async () => {
    try {
      const response = await fetch("/api/checklist/results")
      console.log("[DEBUG] Response status:", response.status)
      if (response.ok) {
        const data = await response.json()
        console.log("[DEBUG] Fetched data:", data)
        console.log("[DEBUG] Data length:", data.length)
        setRecentResults(data.slice(0, 5))
      }
    } catch (error) {
      console.error("[v0] Failed to fetch recent results:", error)
    } finally {
      setLoading(false)
    }
  }

  const fetchTemplatesCount = async () => {
    try {
      const response = await fetch("/api/files/list/checklist")
      if (response.ok) {
        const data = await response.json()
        setTemplatesCount(data.count || 0)
      }
    } catch (error) {
      console.error("[v0] Failed to fetch templates count:", error)
    }
  }

  const fetchDocumentsCount = async () => {
    try {
      const response = await fetch("/api/files/list/user")
      if (response.ok) {
        const data = await response.json()
        setDocumentsCount(data.count || 0)
      }
    } catch (error) {
      console.error("[v0] Failed to fetch documents count:", error)
    }
  }

  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-6 py-12 max-w-7xl">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
            Document Checklist
          </h1>
          <p className="text-lg text-muted-foreground">Manage procurement compliance with AI-powered verification</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <FrostedCard className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Total Checks</p>
                <p className="text-3xl font-bold">{recentResults.length}</p>
              </div>
              <CheckCircle className="h-10 w-10 text-blue-500" />
            </div>
          </FrostedCard>

          <FrostedCard className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Templates</p>
                <p className="text-3xl font-bold">{templatesCount}</p>
              </div>
              <FileText className="h-10 w-10 text-cyan-500" />
            </div>
          </FrostedCard>

          <FrostedCard className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Documents</p>
                <p className="text-3xl font-bold">{documentsCount}</p>
              </div>
              <FileText className="h-10 w-10 text-blue-400" />
            </div>
          </FrostedCard>

          <FrostedCard className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Avg. Compliance</p>
                <p className="text-3xl font-bold">-</p>
              </div>
              <AlertCircle className="h-10 w-10 text-cyan-400" />
            </div>
          </FrostedCard>
        </div>

        {/* Recent Results */}
        <div className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold">Recent Executions</h2>
            <Link href="/results">
              <Button variant="ghost" className="text-blue-500 hover:text-blue-600">
                View All
              </Button>
            </Link>
          </div>

          {loading ? (
            <FrostedCard className="p-8 text-center">
              <p className="text-muted-foreground">Loading recent results...</p>
            </FrostedCard>
          ) : recentResults.length === 0 ? (
            <FrostedCard className="p-8 text-center">
              <Clock className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground mb-4">No checklist executions yet</p>
              <Link href="/checklist/run">
                <Button className="bg-gradient-to-r from-blue-500 to-cyan-400 hover:from-blue-600 hover:to-cyan-500">
                  Run Your First Checklist
                </Button>
              </Link>
            </FrostedCard>
          ) : (
            <div className="space-y-4">
              {recentResults.map((result) => (
                <FrostedCard key={result.id} className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold mb-1">{result.checklist_name}</h3>
                      <p className="text-sm text-muted-foreground">{new Date(result.created_at).toLocaleString()}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      <Link href={`/results/${result.id}`}>
                        <Button variant="ghost" size="sm">
                          View
                        </Button>
                      </Link>
                    </div>
                  </div>
                </FrostedCard>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-2xl font-semibold mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link href="/documents/checklist">
              <FrostedCard className="p-6 hover:scale-105 transition-transform cursor-pointer">
                <FileText className="h-8 w-8 text-blue-500 mb-4" />
                <h3 className="font-semibold mb-2">Upload Template</h3>
                <p className="text-sm text-muted-foreground">Add checklist template documents</p>
              </FrostedCard>
            </Link>

            <Link href="/checklist/templates">
              <FrostedCard className="p-6 hover:scale-105 transition-transform cursor-pointer">
                <CheckCircle className="h-8 w-8 text-cyan-500 mb-4" />
                <h3 className="font-semibold mb-2">Create Template</h3>
                <p className="text-sm text-muted-foreground">Define questions and conditions</p>
              </FrostedCard>
            </Link>

            <Link href="/rag">
              <FrostedCard className="p-6 hover:scale-105 transition-transform cursor-pointer">
                <AlertCircle className="h-8 w-8 text-blue-400 mb-4" />
                <h3 className="font-semibold mb-2">RAG Query</h3>
                <p className="text-sm text-muted-foreground">Ask questions about your documents</p>
              </FrostedCard>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
