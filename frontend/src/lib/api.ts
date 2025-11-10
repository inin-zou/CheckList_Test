import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// File upload with progress
export const uploadFile = async (file: File, onProgress?: (progress: number) => void) => {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient.post('/api/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(progress)
      }
    },
  })
}

// List uploaded files
export const listFiles = () => apiClient.get('/api/files')

// Delete file
export const deleteFile = (filename: string) => apiClient.delete(`/api/files/${filename}`)

// Checklist operations
export const getChecklists = () => apiClient.get('/api/checklist')
export const getChecklist = (id: string) => apiClient.get(`/api/checklist/${id}`)
export const createChecklist = (data: any) => apiClient.post('/api/checklist', data)
export const updateChecklist = (id: string, data: any) => apiClient.put(`/api/checklist/${id}`, data)
export const deleteChecklist = (id: string) => apiClient.delete(`/api/checklist/${id}`)
export const runChecklist = (id: string, documentPath?: string) => 
  apiClient.post(`/api/checklist/${id}/run`, documentPath ? { document_path: documentPath } : {})
export const getChecklistResults = () => apiClient.get('/api/checklist/results')

// RAG operations
export const askRAG = (question: string) => apiClient.post('/api/rag/ask', { question })

export const api = {
  uploadFile,
  listFiles,
  deleteFile,
  getChecklists,
  getChecklist,
  createChecklist,
  updateChecklist,
  deleteChecklist,
  runChecklist,
  getChecklistResults,
  askRAG,
}