import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navigation from './components/Navigation'
import HomePage from './components/HomePage'
import ServicesPage from './components/ServicesPage'
import AboutPage from './components/AboutPage'
import ContactPage from './components/ContactPage'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Navigation />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/contact" element={<ContactPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App

