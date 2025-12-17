"""
{{PROJECT_NAME}} - Main FastAPI Application

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
from src.config.settings import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title='{{PROJECT_NAME}} API',
    description='A modular full-stack application built with WeWork Framework',
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
        "message": "Welcome to {{PROJECT_NAME}}",
        "version": "1.0.0",
        "docs": "/docs",
        "cli_help": "Run 'wework --help' to see available commands"
    }


@app.get('/health')
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

