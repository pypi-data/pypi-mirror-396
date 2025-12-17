"""
WeWork Framework - Main FastAPI Application

This is a generic framework application. Use CLI commands to generate
your own APIs, models, and components.

CLI Commands:
  wework make:api <name>      - Generate a new API router
  wework make:model <name>    - Generate a new database model
  wework make:component <name> - Generate a new React component
  wework make:hook <name>      - Generate a new React hook
  wework make:migration <name> - Generate a new database migration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.config.loader import ConfigLoader
from src.api.auth_api import router as auth_router
from src.api.billing_api import router as billing_router
from src.api.admin_api import router as admin_router
from src.api.notifications_api import router as notifications_router
from src.config.settings import settings
import logging
import asyncio

# Configure uvicorn logging
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)

app = FastAPI(
    title='WeWork Framework API',
    description='A modular full-stack framework for building modern web applications',
    version='1.1.0'
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

# Config loader
cfg = ConfigLoader()

# Include core routers (you can add your own using: wework make:api <name>)
app.include_router(auth_router)
app.include_router(billing_router)
app.include_router(admin_router)
app.include_router(notifications_router)

# Example: To add your own API router:
# from src.api.your_api import router as your_router
# app.include_router(your_router)


@app.on_event('startup')
async def startup():
    """Application startup event"""
    await cfg.load()
    asyncio.create_task(cfg.start_listener())
    # Add your startup tasks here
    logging.info("WeWork Framework started successfully")


@app.on_event('shutdown')
async def shutdown():
    """Application shutdown event"""
    # Add your cleanup tasks here
    logging.info("WeWork Framework shutting down")


@app.get('/')
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to WeWork Framework",
        "version": "1.1.0",
        "docs": "/docs",
        "cli_help": "Run 'wework --help' to see available commands"
    }


@app.get('/config')
async def get_config():
    """Get application configuration"""
    return cfg._cfg


@app.post('/config')
async def set_config(payload: dict):
    """Update application configuration"""
    for k, v in payload.items():
        cfg.set(k, v)
    return {'status': 'ok'}
