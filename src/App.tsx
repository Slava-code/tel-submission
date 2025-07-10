import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [preferences, setPreferences] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [saveMessage, setSaveMessage] = useState('')
  const [blockedCount, setBlockedCount] = useState(0)

  useEffect(() => {
    chrome.storage.local.get(['userPreferences', 'blockedVideosCount'], (result) => {
      if (result.userPreferences) {
        setPreferences(result.userPreferences)
      }
      setBlockedCount(result.blockedVideosCount || 0)
    })

    // Listen for storage changes to update counter in real-time
    const handleStorageChange = (changes: any) => {
      if (changes.blockedVideosCount) {
        setBlockedCount(changes.blockedVideosCount.newValue || 0)
      }
    }

    chrome.storage.onChanged.addListener(handleStorageChange)
    
    return () => {
      chrome.storage.onChanged.removeListener(handleStorageChange)
    }
  }, [])

  const handleSave = async () => {
    setIsLoading(true)
    setSaveMessage('')
    
    try {
      await chrome.storage.local.set({ userPreferences: preferences })
      setSaveMessage('Preferences saved successfully!')
      setTimeout(() => setSaveMessage(''), 3000)
    } catch (error) {
      setSaveMessage('Error saving preferences')
      setTimeout(() => setSaveMessage(''), 3000)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app-container">
      <h1>YouTube AI Productivity Extension</h1>
      <div className="stats-section">
        <div className="blocked-counter">
          <span className="counter-label">Videos Blocked:</span>
          <span className="counter-value">{blockedCount}</span>
        </div>
      </div>
      <div className="settings-section">
        <h2>Content Preferences</h2>
        <p>Describe what type of content you want to see on YouTube:</p>
        <textarea
          className="preferences-textarea"
          value={preferences}
          onChange={(e) => setPreferences(e.target.value)}
          placeholder="Example: I want to see videos about AI, startups, and technology. I want to avoid video games, celebrity gossip, and music videos."
          rows={6}
        />
        <button 
          className="save-button"
          onClick={handleSave}
          disabled={isLoading || !preferences.trim()}
        >
          {isLoading ? 'Saving...' : 'Save Preferences'}
        </button>
        {saveMessage && (
          <div className={`save-message ${saveMessage.includes('Error') ? 'error' : 'success'}`}>
            {saveMessage}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
