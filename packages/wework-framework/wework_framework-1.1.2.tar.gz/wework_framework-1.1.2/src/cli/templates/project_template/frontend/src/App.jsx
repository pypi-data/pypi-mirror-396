import React from 'react'
import { API_BASE_URL } from './config'
import './App.css'

function App() {
  return (
    <div className="app">
      <header>
        <h1>{{PROJECT_NAME}}</h1>
        <p>Welcome to your new WeWork Framework project!</p>
      </header>
      <main>
        <div className="info">
          <h2>🚀 Getting Started</h2>
          <p>API Base URL: {API_BASE_URL}</p>
          <p>Backend API Docs: <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">http://localhost:8000/docs</a></p>
        </div>
        <div className="info">
          <h2>📚 CLI Commands</h2>
          <ul>
            <li><code>wework make:api &lt;name&gt;</code> - Generate a new API router</li>
            <li><code>wework make:model &lt;name&gt;</code> - Generate a new database model</li>
            <li><code>wework make:component &lt;name&gt;</code> - Generate a new React component</li>
            <li><code>wework make:hook &lt;name&gt;</code> - Generate a new React hook</li>
            <li><code>wework make:migration &lt;name&gt;</code> - Generate a new database migration</li>
          </ul>
        </div>
      </main>
    </div>
  )
}

export default App

