export interface FileInfo {
  id: string
  name: string
  size: number
  uploadedAt: string
}

export interface Checklist {
  id: string
  name: string
  items: ChecklistItem[]
  createdAt: string
  updatedAt: string
}

export type ChecklistItem = QuestionItem | ConditionItem

export interface QuestionItem {
  type: 'question'
  content: string
}

export interface ConditionItem {
  type: 'condition'
  content: string
  expected_value: string
}

export interface RAGResponse {
  answer: string
  sources: string[]
}