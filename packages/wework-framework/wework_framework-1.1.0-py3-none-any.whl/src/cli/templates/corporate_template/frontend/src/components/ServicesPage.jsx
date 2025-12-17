import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE_URL } from '../config'
import '../App.css'

function ServicesPage() {
  const [services, setServices] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/services`)
        setServices(response.data.services || [])
      } catch (error) {
        console.error('Error fetching services:', error)
        // Fallback data
        setServices([
          {
            id: 1,
            title: 'مشاوره تخصصی',
            description: 'ارائه مشاوره‌های تخصصی در زمینه کسب و کار',
            icon: '💼'
          },
          {
            id: 2,
            title: 'طراحی و توسعه',
            description: 'طراحی و توسعه نرم‌افزار و وب‌سایت',
            icon: '🎨'
          },
          {
            id: 3,
            title: 'پشتیبانی 24/7',
            description: 'پشتیبانی تمام وقت از خدمات ارائه شده',
            icon: '🛟'
          }
        ])
      } finally {
        setLoading(false)
      }
    }

    fetchServices()
  }, [])

  return (
    <div style={{ paddingTop: '80px' }}>
      <section className="section" style={{ background: 'white', minHeight: '100vh' }}>
        <h2 className="section-title">خدمات ما</h2>
        <p className="section-subtitle">
          مجموعه‌ای کامل از خدمات حرفه‌ای برای رفع نیازهای شما
        </p>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <p>در حال بارگذاری...</p>
          </div>
        ) : (
          <div className="services-grid">
            {services.map((service) => (
              <div key={service.id} className="service-card">
                <div className="service-icon">{service.icon || '📦'}</div>
                <h3>{service.title}</h3>
                <p>{service.description}</p>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

export default ServicesPage

