"use client"

import { useState, useEffect } from "react"
import { FileUploader } from "@/components/file-uploader"
import { FrostedCard } from "@/components/frosted-card"
import { Button } from "@/components/ui/button"
import { FileText, Download, Trash2 } from "lucide-react"

interface FileItem {
  filename: string
  pdf_uuid: string
  created_at: string
  size?: number
}

export default function UserDocumentsPage() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchFiles()
  }, [])

  const fetchFiles = async () => {
    try {
      const response = await fetch("/api/files/list/user")
      if (response.ok) {
        const data = await response.json()
        setFiles(data)
      }
    } catch (error) {
      console.error("[v0] Failed to fetch files:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (filename: string) => {
    if (!confirm("Are you sure you want to delete this file?")) return

    try {
      const response = await fetch(`/api/files/user/${filename}`, {
        method: "DELETE",
      })
      if (response.ok) {
        fetchFiles()
      }
    } catch (error) {
      console.error("[v0] Failed to delete file:", error)
    }
  }

  const handleDownload = (pdfUuid: string, filename: string) => {
    window.open(`/api/files/download/user/${pdfUuid}`, "_blank")
  }

  return (
    <div className="container mx-auto px-6 py-12 max-w-5xl">
      <h1 className="text-4xl font-bold mb-2">User Documents</h1>
      <p className="text-muted-foreground mb-8">Upload and manage user documents for verification</p>

      <div className="mb-8">
        <FileUploader collectionType="user" onUploadSuccess={fetchFiles} />
      </div>

      <div>
        <h2 className="text-2xl font-semibold mb-4">Uploaded Files</h2>
        {loading ? (
          <FrostedCard className="p-8 text-center">
            <p className="text-muted-foreground">Loading files...</p>
          </FrostedCard>
        ) : files.length === 0 ? (
          <FrostedCard className="p-8 text-center">
            <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground">No files uploaded yet</p>
          </FrostedCard>
        ) : (
          <div className="space-y-3">
            {files.map((file) => (
              <FrostedCard key={file.pdf_uuid} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileText className="h-8 w-8 text-cyan-500" />
                    <div>
                      <p className="font-medium">{file.filename}</p>
                      <p className="text-sm text-muted-foreground">{new Date(file.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="icon" onClick={() => handleDownload(file.pdf_uuid, file.filename)}>
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(file.filename)}>
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </FrostedCard>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
