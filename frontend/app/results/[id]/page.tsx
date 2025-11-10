"use client"

import { useState, useEffect } from "react"
import { FrostedCard } from "@/components/frosted-card"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { useParams } from "next/navigation"

export default function ResultDetailPage() {
  const params = useParams()
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (params.id) {
      fetchResult(params.id as string)
    }
  }, [params.id])

  const fetchResult = async (id: string) => {
    try {
      const response = await fetch(`/api/checklist/results/${id}`)
      if (response.ok) {
        const data = await response.json()
        setResult(data)
      }
    } catch (error) {
      console.error("[v0] Failed to fetch result:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-6 py-12 max-w-5xl">
      <Link href="/results">
        <Button variant="ghost" className="mb-6">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Results
        </Button>
      </Link>

      {loading ? (
        <FrostedCard className="p-8 text-center">
          <p className="text-muted-foreground">Loading result...</p>
        </FrostedCard>
      ) : !result ? (
        <FrostedCard className="p-8 text-center">
          <p className="text-muted-foreground">Result not found</p>
        </FrostedCard>
      ) : (
        <FrostedCard className="p-8">
          <h1 className="text-3xl font-bold mb-4">Execution Result</h1>
          <div className="space-y-4 mb-6">
            <div>
              <span className="text-sm text-muted-foreground">Template:</span>
              <p className="font-medium">{result.template_name || "N/A"}</p>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Executed:</span>
              <p className="font-medium">{result.created_at ? new Date(result.created_at).toLocaleString() : "N/A"}</p>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Status:</span>
              <p className="font-medium">{result.status || "N/A"}</p>
            </div>
          </div>

          <div className="bg-muted/50 rounded-lg p-6">
            <h2 className="font-semibold mb-4">Full Result Data</h2>
            <pre className="text-sm overflow-x-auto">{JSON.stringify(result, null, 2)}</pre>
          </div>
        </FrostedCard>
      )}
    </div>
  )
}
