"""
{{PROJECT_NAME}} - Admin Panel API

FastAPI application for admin panel template.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title='{{PROJECT_NAME}} Admin API',
    description='Admin panel API built with WeWork Framework',
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
        "message": "Welcome to {{PROJECT_NAME}} Admin Panel API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get('/health')
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get('/api/dashboard/stats')
async def get_dashboard_stats():
    """Get dashboard statistics"""
    return {
        "totalUsers": 1250,
        "totalOrders": 3420,
        "totalRevenue": 125000000,
        "growthRate": 12.5
    }


@app.get('/api/users')
async def get_users(page: int = 1, limit: int = 10, search: str = None):
    """Get list of users"""
    users = [
        {"id": i, "name": f"کاربر {i}", "email": f"user{i}@example.com", "role": "user", "status": "active"}
        for i in range(1, 51)
    ]
    
    if search:
        users = [u for u in users if search.lower() in u["name"].lower() or search.lower() in u["email"].lower()]
    
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "users": users[start:end],
        "total": len(users),
        "page": page,
        "limit": limit
    }

