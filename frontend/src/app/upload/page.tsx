'use client'

import { useState } from 'react'
import { api } from '@/lib/api'

export default function UploadPage() {
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<{[key: string]: number}>({})
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([])
  const [error, setError] = useState<string>('')
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const newFiles = Array.from(e.dataTransfer.files)
      setFiles(prev => [...prev, ...newFiles])
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files)
      setFiles(prev => [...prev, ...newFiles])
    }
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const uploadFiles = async () => {
    if (files.length === 0) return
    
    setUploading(true)
    setError('')
    const newUploadedFiles: string[] = []
    
    for (const file of files) {
      try {
        setUploadProgress(prev => ({ ...prev, [file.name]: 0 }))
        
        const response = await api.uploadFile(file, (progress) => {
          setUploadProgress(prev => ({ ...prev, [file.name]: progress }))
        })
        
        newUploadedFiles.push(file.name)
        setUploadProgress(prev => ({ ...prev, [file.name]: 100 }))
      } catch (err) {
        setError(`Failed to upload ${file.name}: ${err instanceof Error ? err.message : 'Unknown error'}`)
        console.error('Upload error:', err)
      }
    }
    
    setUploadedFiles(prev => [...prev, ...newUploadedFiles])
    setFiles([])
    setUploading(false)
    setUploadProgress({})
  }

  return (
    <div className="container mx-auto p-8 max-w-5xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Upload Documents</h1>
              <p className="text-gray-300">Upload your documents for intelligent analysis</p>
          </div>
        </div>
      </div>
      
      {/* Upload Area */}
      <div
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
          dragActive 
            ? 'border-blue-400 glass-dark scale-105' 
            : 'border-gray-600 glass hover:border-gray-500'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          multiple
          onChange={handleFileInput}
          className="hidden"
          id="file-input"
          accept=".pdf,.doc,.docx,.txt"
        />
        <label htmlFor="file-input" className="cursor-pointer">
          <div className="space-y-4">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-100 to-cyan-100 dark:from-blue-900/40 dark:to-cyan-900/40 mb-2">
              <svg className="w-10 h-10 text-blue-600 dark:text-blue-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <div>
              <p className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Drag files here</p>
                <p className="text-sm text-gray-300">or click to select files</p>
            </div>
            <div className="flex items-center justify-center space-x-2 text-xs text-gray-400 dark:text-gray-500">
              <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">PDF</span>
              <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">DOC</span>
              <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">DOCX</span>
              <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">TXT</span>
            </div>
          </div>
        </label>
      </div>

      {files.length > 0 && (
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-white">Selected Files</h2>
            <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full text-sm font-medium">
              {files.length} file(s)
            </span>
          </div>
          <div className="space-y-3">
            {files.map((file, index) => (
              <div key={index} className="group flex items-center justify-between p-4 glass hover:glass-dark rounded-xl hover:shadow-lg hover:scale-[1.02] transition-all duration-300">
                <div className="flex items-center space-x-4 flex-1 min-w-0">
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center flex-shrink-0">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-white truncate">{file.name}</p>
                    <p className="text-sm text-gray-400">{(file.size / 1024).toFixed(2)} KB</p>
                    {uploadProgress[file.name] !== undefined && (
                      <div className="mt-2">
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${uploadProgress[file.name]}%` }}
                          />
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{uploadProgress[file.name]}%</p>
                      </div>
                    )}
                  </div>
                </div>
                {!uploading && (
                  <button
                    onClick={() => removeFile(index)}
                    className="ml-4 p-2 rounded-lg text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors duration-200 flex-shrink-0"
                    title="Delete file"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                )}
              </div>
            ))}
          </div>
          
          <button
            onClick={uploadFiles}
            disabled={uploading || files.length === 0}
            className="w-full mt-6 px-6 py-4 glass-dark hover:bg-white/20 text-white font-semibold rounded-xl hover:shadow-xl hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none transition-all duration-300 flex items-center justify-center space-x-2"
          >
            {uploading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Uploading...</span>
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span>Upload {files.length} file(s)</span>
              </>
            )}
          </button>
        </div>
      )}

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {uploadedFiles.length > 0 && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-4 text-green-600">Successfully Uploaded</h2>
          <div className="space-y-2">
            {uploadedFiles.map((filename, index) => (
              <div key={index} className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-800">✓ {filename}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}