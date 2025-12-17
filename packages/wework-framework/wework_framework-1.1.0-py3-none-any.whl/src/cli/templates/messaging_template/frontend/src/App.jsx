import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './components/LandingPage'
import Dashboard from './components/Dashboard'
import AdminPanel from './components/AdminPanel'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard/*" element={<Dashboard />} />
        <Route path="/admin/*" element={<AdminPanel />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App

