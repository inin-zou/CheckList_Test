'use client'

import { useState, useEffect } from 'react'

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    anthropicApiKey: '',
    anthropicModel: 'claude-sonnet-4-5-20250929',
    openaiApiKey: '',
    weaviateUrl: 'http://localhost:8080',
  })
  const [saved, setSaved] = useState(false)
  const [showApiKey, setShowApiKey] = useState(false)

  useEffect(() => {
    // Load settings from localStorage on mount
    const savedSettings = localStorage.getItem('appSettings')
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings))
    }
  }, [])

  const handleSave = () => {
    localStorage.setItem('appSettings', JSON.stringify(settings))
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const handleReset = () => {
    const defaultSettings = {
      anthropicApiKey: '',
      anthropicModel: 'claude-sonnet-4-5-20250929',
      openaiApiKey: '',
      weaviateUrl: 'http://localhost:8080',
    }
    setSettings(defaultSettings)
    localStorage.setItem('appSettings', JSON.stringify(defaultSettings))
  }

  return (
    <div className="container mx-auto p-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">Settings</h1>
      
      <div className="space-y-6">
        {/* Anthropic Configuration */}
        <div className="border rounded-lg p-6 bg-white shadow-sm">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <span className="text-2xl mr-2">🤖</span>
            Anthropic Claude Configuration
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                API Key
                <span className="text-red-500 ml-1">*</span>
              </label>
              <div className="flex gap-2">
                <input
                  type={showApiKey ? 'text' : 'password'}
                  value={settings.anthropicApiKey}
                  onChange={(e) => setSettings({ ...settings, anthropicApiKey: e.target.value })}
                  className="flex-1 border rounded-lg p-2 font-mono text-sm"
                  placeholder="sk-ant-..."
                />
                <button
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  {showApiKey ? '🙈' : '👁️'}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Get your API key from{' '}
                <a
                  href="https://console.anthropic.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  console.anthropic.com
                </a>
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Model
                <span className="text-red-500 ml-1">*</span>
              </label>
              <select
                value={settings.anthropicModel}
                onChange={(e) => setSettings({ ...settings, anthropicModel: e.target.value })}
                className="w-full border rounded-lg p-2"
              >
                <option value="claude-sonnet-4-5-20250929">Claude Sonnet 4.5 (Latest)</option>
                <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet (Deprecated)</option>
                <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">
                Recommended: Claude Sonnet 4.5 for best performance
              </p>
            </div>
          </div>
        </div>

        {/* OpenAI Configuration */}
        <div className="border rounded-lg p-6 bg-white shadow-sm">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <span className="text-2xl mr-2">🔷</span>
            OpenAI Configuration (Optional)
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                API Key
              </label>
              <input
                type={showApiKey ? 'text' : 'password'}
                value={settings.openaiApiKey}
                onChange={(e) => setSettings({ ...settings, openaiApiKey: e.target.value })}
                className="w-full border rounded-lg p-2 font-mono text-sm"
                placeholder="sk-..."
              />
              <p className="text-xs text-gray-500 mt-1">
                Only required if using OpenAI embeddings
              </p>
            </div>
          </div>
        </div>

        {/* Weaviate Configuration */}
        <div className="border rounded-lg p-6 bg-white shadow-sm">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <span className="text-2xl mr-2">🗄️</span>
            Weaviate Vector Database
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Database URL
                <span className="text-red-500 ml-1">*</span>
              </label>
              <input
                type="text"
                value={settings.weaviateUrl}
                onChange={(e) => setSettings({ ...settings, weaviateUrl: e.target.value })}
                className="w-full border rounded-lg p-2"
                placeholder="http://localhost:8080"
              />
              <p className="text-xs text-gray-500 mt-1">
                Local development: http://localhost:8080
              </p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            onClick={handleSave}
            className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            {saved ? '✓ Saved Successfully!' : 'Save Settings'}
          </button>
          <button
            onClick={handleReset}
            className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Reset to Default
          </button>
        </div>

        {/* Information Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">ℹ️ Important Notes</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Settings are saved locally in your browser</li>
            <li>• Backend configuration in <code className="bg-blue-100 px-1 rounded">backend/.env</code> takes precedence</li>
            <li>• Never share your API keys publicly</li>
            <li>• Use Claude Sonnet 4.5 for best results with German language support</li>
          </ul>
        </div>
      </div>
    </div>
  )
}