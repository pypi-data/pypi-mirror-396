"""
{{PROJECT_NAME}} - E-commerce API

FastAPI application for e-commerce template.
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
    description='E-commerce API built with WeWork Framework',
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
        "message": "Welcome to {{PROJECT_NAME}} E-commerce API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get('/health')
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get('/api/products')
async def get_products(category: str = None, search: str = None):
    """Get list of products"""
    products = [
        {
            "id": 1,
            "name": "محصول نمونه 1",
            "description": "توضیحات محصول نمونه",
            "price": 150000,
            "image_url": "https://via.placeholder.com/300",
            "category": "الکترونیک",
            "stock": 10
        },
        {
            "id": 2,
            "name": "محصول نمونه 2",
            "description": "توضیحات محصول نمونه",
            "price": 250000,
            "image_url": "https://via.placeholder.com/300",
            "category": "پوشاک",
            "stock": 5
        },
        {
            "id": 3,
            "name": "محصول نمونه 3",
            "description": "توضیحات محصول نمونه",
            "price": 350000,
            "image_url": "https://via.placeholder.com/300",
            "category": "الکترونیک",
            "stock": 8
        }
    ]
    
    if category:
        products = [p for p in products if p["category"] == category]
    if search:
        products = [p for p in products if search.lower() in p["name"].lower()]
    
    return {"products": products}


@app.get('/api/products/{product_id}')
async def get_product(product_id: int):
    """Get product by ID"""
    return {
        "id": product_id,
        "name": "محصول نمونه",
        "description": "توضیحات کامل محصول",
        "price": 150000,
        "image_url": "https://via.placeholder.com/600",
        "category": "الکترونیک",
        "stock": 10
    }

