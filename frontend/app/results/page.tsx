"use client"

import { useState, useEffect } from "react"
import { FrostedCard } from "@/components/frosted-card"
import { Button } from "@/components/ui/button"
import { Eye } from "lucide-react"
import Link from "next/link"

interface Result {
  id: number
  template_name: string
  created_at: string
  status: string
}

export default function ResultsPage() {
  const [results, setResults] = useState<Result[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchResults()
  }, [])

  const fetchResults = async () => {
    try {
      const response = await fetch("/api/checklist/results")
      if (response.ok) {
        const data = await response.json()
        setResults(data)
      }
    } catch (error) {
      console.error("[v0] Failed to fetch results:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-6 py-12 max-w-5xl">
      <h1 className="text-4xl font-bold mb-2">Execution Results</h1>
      <p className="text-muted-foreground mb-8">View historical checklist execution results</p>

      <div className="space-y-4">
        {loading ? (
          <FrostedCard className="p-8 text-center">
            <p className="text-muted-foreground">Loading results...</p>
          </FrostedCard>
        ) : results.length === 0 ? (
          <FrostedCard className="p-8 text-center">
            <p className="text-muted-foreground mb-4">No results yet</p>
            <Link href="/checklist/run">
              <Button className="bg-gradient-to-r from-blue-500 to-cyan-400 hover:from-blue-600 hover:to-cyan-500">
                Run Your First Checklist
              </Button>
            </Link>
          </FrostedCard>
        ) : (
          results.map((result) => (
            <FrostedCard key={result.id} className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold mb-1">{result.template_name}</h3>
                  <p className="text-sm text-muted-foreground">{new Date(result.created_at).toLocaleString()}</p>
                </div>
                <div className="flex items-center gap-4">
                  <span
                    className={`px-3 py-1 rounded-full text-sm ${
                      result.status === "completed"
                        ? "bg-green-500/20 text-green-600"
                        : "bg-yellow-500/20 text-yellow-600"
                    }`}
                  >
                    {result.status}
                  </span>
                  <Link href={`/results/${result.id}`}>
                    <Button variant="ghost" size="sm">
                      <Eye className="mr-2 h-4 w-4" />
                      View
                    </Button>
                  </Link>
                </div>
              </div>
            </FrostedCard>
          ))
        )}
      </div>
    </div>
  )
}
