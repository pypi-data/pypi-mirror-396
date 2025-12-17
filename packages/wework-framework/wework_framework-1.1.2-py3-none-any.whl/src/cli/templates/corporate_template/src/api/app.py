"""
{{PROJECT_NAME}} - Corporate Website API

FastAPI application for corporate website template.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title='{{PROJECT_NAME}} API',
    description='Corporate website API built with WeWork Framework',
    version='1.0.0'
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get('/')
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to {{PROJECT_NAME}} Corporate Website API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get('/health')
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get('/api/services')
async def get_services():
    """Get list of services"""
    return {
        "services": [
            {
                "id": 1,
                "title": "مشاوره تخصصی",
                "description": "ارائه مشاوره‌های تخصصی در زمینه کسب و کار",
                "icon": "💼"
            },
            {
                "id": 2,
                "title": "طراحی و توسعه",
                "description": "طراحی و توسعه نرم‌افزار و وب‌سایت",
                "icon": "🎨"
            },
            {
                "id": 3,
                "title": "پشتیبانی 24/7",
                "description": "پشتیبانی تمام وقت از خدمات ارائه شده",
                "icon": "🛟"
            }
        ]
    }


@app.post('/api/contact')
async def submit_contact(name: str, email: str, phone: str = None, subject: str = None, message: str = None):
    """Submit contact form"""
    # In a real application, save to database
    return {
        "success": True,
        "message": "پیام شما با موفقیت ارسال شد. در اسرع وقت با شما تماس خواهیم گرفت."
    }

