'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import type { Checklist, ChecklistItem } from '@/types'

export default function ChecklistPage() {
  const [checklists, setChecklists] = useState<Checklist[]>([])
  const [selectedChecklist, setSelectedChecklist] = useState<Checklist | null>(null)
  const [results, setResults] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newChecklist, setNewChecklist] = useState({
    name: '',
    items: [] as ChecklistItem[],
  })

  useEffect(() => {
    loadChecklists()
  }, [])

  const loadChecklists = async () => {
    try {
      const response = await api.getChecklists()
      setChecklists(response.data)
    } catch (error) {
      console.error('Failed to load checklists:', error)
    }
  }

  const handleCreateChecklist = async () => {
    try {
      setLoading(true)
      await api.createChecklist({
        name: newChecklist.name,
        items: newChecklist.items,
      })

      setShowCreateForm(false)
      setNewChecklist({
        name: '',
        items: [] as ChecklistItem[],
      })
      await loadChecklists()
    } catch (error) {
      console.error('Failed to create checklist:', error)
      alert('Failed to create checklist')
    } finally {
      setLoading(false)
    }
  }

  const handleRunChecklist = async (checklistId: string) => {
    try {
      setLoading(true)
      setResults(null)
      const response = await api.runChecklist(checklistId)
      setResults(response.data)
    } catch (error) {
      console.error('Failed to run checklist:', error)
      alert('Failed to run checklist')
    } finally {
      setLoading(false)
    }
  }

  const addQuestion = () => {
    setNewChecklist({
      ...newChecklist,
      items: [...newChecklist.items, { type: 'question' as const, content: '' }],
    })
  }

  const addCondition = () => {
    setNewChecklist({
      ...newChecklist,
      items: [
        ...newChecklist.items,
        { type: 'condition' as const, content: '', expected_value: '' },
      ],
    })
  }

  const removeItem = (index: number) => {
    setNewChecklist({
      ...newChecklist,
      items: newChecklist.items.filter((_, i) => i !== index),
    })
  }

  return (
    <div className="container mx-auto p-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-xl glass-dark flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">Checklist Management</h1>
              <p className="text-gray-300">Create and manage your intelligent checklists</p>
            </div>
          </div>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            {showCreateForm ? 'Cancel' : 'Create New Checklist'}
          </button>
        </div>
      </div>

      {showCreateForm && (
        <div className="mb-8 p-6 glass rounded-2xl shadow-xl">
          <h2 className="text-2xl font-bold text-white mb-6">Create New Checklist</h2>
          
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-200 mb-2">Checklist Name</label>
            <input
              type="text"
              value={newChecklist.name}
              onChange={(e) => setNewChecklist(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-4 py-3 border-2 border-gray-600 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-800 glass-dark text-white transition-all duration-200"
              placeholder="Enter checklist name"
            />
          </div>

          <div className="mb-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Questions & Conditions</span>
              </h3>
              <div className="flex gap-2">
                <button
                  onClick={addQuestion}
                  className="px-4 py-2 glass-dark text-white text-sm font-semibold rounded-lg hover:shadow-lg hover:scale-105 transition-all duration-200 flex items-center space-x-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  <span>Add Question</span>
                </button>
                <button
                  onClick={addCondition}
                  className="px-4 py-2 glass-dark text-white text-sm font-semibold rounded-lg hover:shadow-lg hover:scale-105 transition-all duration-200 flex items-center space-x-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  <span>Add Condition</span>
                </button>
              </div>
            </div>
            {newChecklist.items.map((item, index) => (
              <div key={index} className="flex gap-3 items-start p-4 border-2 border-gray-700 rounded-xl glass-dark hover:shadow-md transition-all duration-200 mb-3">
                <div className="flex-1">
                  <input
                    type="text"
                    value={item.content}
                    onChange={(e) => {
                      const newItems = [...newChecklist.items]
                      if (item.type === 'question') {
                        newItems[index] = {
                          type: 'question' as const,
                          content: e.target.value,
                        }
                      } else {
                        newItems[index] = {
                          type: 'condition' as const,
                          content: e.target.value,
                          expected_value: item.expected_value,
                        }
                      }
                      setNewChecklist({ ...newChecklist, items: newItems })
                    }}
                    className="w-full border rounded-lg p-2"
                    placeholder={item.type === 'question' ? 'Enter a question' : 'Enter a condition'}
                  />
                  {item.type === 'condition' && (
                    <input
                      type="text"
                      value={item.expected_value}
                      onChange={(e) => {
                        const newItems = [...newChecklist.items]
                        newItems[index] = {
                          type: 'condition' as const,
                          content: item.content,
                          expected_value: e.target.value,
                        }
                        setNewChecklist({ ...newChecklist, items: newItems })
                      }}
                      className="w-full border rounded-lg p-2 mt-2"
                      placeholder="Expected value"
                    />
                  )}
                </div>
                <button
                  onClick={() => removeItem(index)}
                  className="p-2 rounded-lg text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors duration-200"
                  title="Delete"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>

          <button
            onClick={handleCreateChecklist}
            disabled={loading || !newChecklist.name.trim()}
            className="w-full glass-dark text-white py-3 rounded-lg hover:shadow-xl hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none transition-all duration-300"
          >
            {loading ? 'Creating...' : 'Create Checklist'}
          </button>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-2xl font-semibold mb-4">Your Checklists</h2>
          <div className="space-y-4">
            {checklists.length === 0 ? (
              <div className="border rounded-lg p-6 text-center text-gray-500">
                No checklists yet. Create one to get started!
              </div>
            ) : (
              checklists.map((checklist) => (
                <div
                  key={checklist.id}
                  className={`glass rounded-xl p-6 cursor-pointer transition-all duration-300 hover:shadow-2xl hover:scale-105 ${
                    selectedChecklist?.id === checklist.id
                      ? 'border-2 border-purple-500 shadow-xl'
                      : ''
                  }`}
                  onClick={() => setSelectedChecklist(checklist)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-xl font-bold text-white">{checklist.name}</h3>
                    <span className="text-xs text-gray-500">
                      {checklist.items.length} items
                    </span>
                  </div>
                  <div className="text-sm text-gray-300">
                    <p>
                      Questions: {checklist.items.filter(i => i.type === 'question').length}
                    </p>
                    <p>
                      Conditions: {checklist.items.filter(i => i.type === 'condition').length}
                    </p>
                  </div>
                  {selectedChecklist?.id === checklist.id && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleRunChecklist(checklist.id)
                      }}
                      disabled={loading}
                      className="mt-3 w-full glass-dark text-white py-2 rounded-lg hover:shadow-lg hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:hover:scale-100"
                    >
                      {loading ? 'Running...' : 'Run Checklist'}
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-semibold mb-4">Checklist Details & Results</h2>
          {selectedChecklist ? (
            <div className="border rounded-lg p-4">
              <h3 className="text-xl font-semibold mb-4">{selectedChecklist.name}</h3>
              
              <div className="mb-4">
                <h4 className="font-semibold mb-2">Items:</h4>
                <ul className="space-y-2">
                  {selectedChecklist.items.map((item, index) => (
                    <li key={index} className="text-sm">
                      <span className="font-medium">
                        {item.type === 'question' ? '❓' : '✓'}
                      </span>{' '}
                      {item.content}
                      {item.type === 'condition' && item.expected_value && (
                        <span className="text-gray-500 ml-2">
                          (Expected: {item.expected_value})
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>

              {results && (
                <div className="mt-6 pt-6 border-t">
                  <h4 className="font-semibold mb-3 text-green-600">Results:</h4>
                  
                  {results.answers && results.answers.length > 0 && (
                    <div className="mb-4">
                      <h5 className="font-medium mb-2">Answers:</h5>
                      <ul className="space-y-2">
                        {results.answers.map((answer: any, index: number) => (
                          <li key={index} className="bg-gray-50 p-3 rounded text-sm">
                            <p className="font-medium text-gray-700 mb-1">
                              Q: {answer.question}
                            </p>
                            <p className="text-gray-900">
                              A: {answer.answer}
                            </p>
                            {answer.explanation && (
                              <p className="text-xs text-gray-500 mt-1">
                                {answer.explanation}
                              </p>
                            )}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {results.evaluations && results.evaluations.length > 0 && (
                    <div>
                      <h5 className="font-medium mb-2">Evaluations:</h5>
                      <ul className="space-y-2">
                        {results.evaluations.map((evaluation: any, index: number) => (
                          <li key={index} className="bg-gray-50 p-3 rounded text-sm">
                            <p className="font-medium text-gray-700 mb-1">
                              {evaluation.condition}
                            </p>
                            <p className="text-gray-900">
                              Result: {evaluation.result ? '✓ Pass' : '✗ Fail'}
                            </p>
                            {evaluation.explanation && (
                              <p className="text-xs text-gray-500 mt-1">
                                {evaluation.explanation}
                              </p>
                            )}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="border rounded-lg p-6 text-center text-gray-500">
              Select a checklist to view details
            </div>
          )}
        </div>
      </div>
    </div>
  )
}