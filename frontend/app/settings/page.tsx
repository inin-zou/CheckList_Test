"use client"

import { useState, useEffect } from "react"
import { FrostedCard } from "@/components/frosted-card"
import { Button } from "@/components/ui/button"
import { CheckCircle, XCircle, RefreshCw } from "lucide-react"

export default function SettingsPage() {
  const [health, setHealth] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchHealth()
  }, [])

  const fetchHealth = async () => {
    setLoading(true)
    try {
      const response = await fetch("/health")
      if (response.ok) {
        const data = await response.json()
        setHealth(data)
      }
    } catch (error) {
      console.error("[v0] Failed to fetch health:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-6 py-12 max-w-5xl">
      <h1 className="text-4xl font-bold mb-2">Settings</h1>
      <p className="text-muted-foreground mb-8">System configuration and health status</p>

      <div className="space-y-6">
        <FrostedCard className="p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">System Health</h2>
            <Button onClick={fetchHealth} disabled={loading} variant="outline" size="sm">
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
          </div>

          {loading ? (
            <p className="text-muted-foreground">Checking system health...</p>
          ) : health ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <CheckCircle className="h-6 w-6 text-green-500" />
                <div>
                  <p className="font-medium">System Status</p>
                  <p className="text-sm text-muted-foreground">{health.status || "OK"}</p>
                </div>
              </div>
              <div className="bg-muted/50 rounded-lg p-4">
                <pre className="text-sm overflow-x-auto">{JSON.stringify(health, null, 2)}</pre>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <XCircle className="h-6 w-6 text-destructive" />
              <div>
                <p className="font-medium">Unable to connect</p>
                <p className="text-sm text-muted-foreground">Could not reach the backend server</p>
              </div>
            </div>
          )}
        </FrostedCard>

        <FrostedCard className="p-8">
          <h2 className="text-xl font-semibold mb-4">Application Info</h2>
          <div className="space-y-3">
            <div>
              <span className="text-sm text-muted-foreground">Version:</span>
              <p className="font-medium">1.0.0</p>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Frontend:</span>
              <p className="font-medium">React + TypeScript + TailwindCSS</p>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Backend API:</span>
              <p className="font-medium">FastAPI</p>
            </div>
          </div>
        </FrostedCard>
      </div>
    </div>
  )
}
