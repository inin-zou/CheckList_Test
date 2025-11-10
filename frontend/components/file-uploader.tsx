"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { Upload, X, FileText, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { FrostedCard } from "./frosted-card"

interface FileUploaderProps {
  collectionType: "checklist" | "user"
  onUploadSuccess?: () => void
}

export function FileUploader({ collectionType, onUploadSuccess }: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true)
    } else if (e.type === "dragleave") {
      setIsDragging(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files && files[0] && files[0].type === "application/pdf") {
      setSelectedFile(files[0])
    }
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files[0]) {
      setSelectedFile(files[0])
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setUploading(true)
    const formData = new FormData()
    formData.append("file", selectedFile)

    try {
      const response = await fetch(`/api/files/upload/${collectionType}`, {
        method: "POST",
        body: formData,
      })

      if (response.ok) {
        setSelectedFile(null)
        onUploadSuccess?.()
      } else {
        console.error("[v0] Upload failed:", await response.text())
      }
    } catch (error) {
      console.error("[v0] Upload error:", error)
    } finally {
      setUploading(false)
    }
  }

  return (
    <FrostedCard className="p-8">
      <div
        className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
          isDragging ? "border-blue-500 bg-blue-500/10" : "border-border hover:border-blue-400"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {selectedFile ? (
          <div className="space-y-4">
            <div className="flex items-center justify-center gap-3">
              <FileText className="h-8 w-8 text-blue-500" />
              <div className="text-left">
                <p className="font-medium">{selectedFile.name}</p>
                <p className="text-sm text-muted-foreground">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setSelectedFile(null)} disabled={uploading}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            <Button
              onClick={handleUpload}
              disabled={uploading}
              className="bg-gradient-to-r from-blue-500 to-cyan-400 hover:from-blue-600 hover:to-cyan-500"
            >
              {uploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload File
                </>
              )}
            </Button>
          </div>
        ) : (
          <>
            <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-lg font-medium mb-2">Drop your PDF file here or click to browse</p>
            <p className="text-sm text-muted-foreground mb-4">Supports PDF files up to 50MB</p>
            <input type="file" accept=".pdf" onChange={handleFileSelect} className="hidden" id="file-upload" />
            <label htmlFor="file-upload">
              <Button variant="outline" asChild>
                <span>Select File</span>
              </Button>
            </label>
          </>
        )}
      </div>
    </FrostedCard>
  )
}
