"""
{{PROJECT_NAME}} - Messaging System API

FastAPI application for messaging system template.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from src.config.settings import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title='{{PROJECT_NAME}} Messaging API',
    description='Messaging system API for Iranian messengers built with WeWork Framework',
    version='1.0.0'
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)


# Pydantic models
class SubscriptionPlanResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    duration_days: int
    max_accounts: int
    max_messages_per_day: int
    features: Optional[dict]


class MessengerAccountCreate(BaseModel):
    messenger_type: str
    account_name: str
    account_phone: Optional[str]
    credentials: Optional[dict]


class MessageCampaignCreate(BaseModel):
    name: str
    message_text: str
    recipients: List[str]
    account_ids: List[int]


@app.get('/')
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to {{PROJECT_NAME}} Messaging System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get('/health')
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get('/api/plans')
async def get_subscription_plans():
    """Get available subscription plans"""
    return {
        "plans": [
            {
                "id": 1,
                "name": "پلن پایه",
                "description": "مناسب برای استفاده شخصی",
                "price": 50000,
                "duration_days": 30,
                "max_accounts": 2,
                "max_messages_per_day": 500,
                "features": {
                    "support": "پشتیبانی ایمیل",
                    "api_access": False
                }
            },
            {
                "id": 2,
                "name": "پلن حرفه‌ای",
                "description": "مناسب برای کسب و کارهای کوچک",
                "price": 150000,
                "duration_days": 30,
                "max_accounts": 5,
                "max_messages_per_day": 2000,
                "features": {
                    "support": "پشتیبانی تلفنی",
                    "api_access": True
                }
            },
            {
                "id": 3,
                "name": "پلن سازمانی",
                "description": "مناسب برای سازمان‌های بزرگ",
                "price": 500000,
                "duration_days": 30,
                "max_accounts": 20,
                "max_messages_per_day": 10000,
                "features": {
                    "support": "پشتیبانی اختصاصی",
                    "api_access": True,
                    "custom_integration": True
                }
            }
        ]
    }


@app.post('/api/subscriptions')
async def create_subscription(plan_id: int, user_id: int = 1):
    """Create a new subscription"""
    # In real implementation, verify payment and create subscription
    return {
        "success": True,
        "subscription_id": 1,
        "message": "اشتراک با موفقیت فعال شد"
    }


@app.get('/api/users/{user_id}/accounts')
async def get_user_accounts(user_id: int):
    """Get user's messenger accounts"""
    return {
        "accounts": [
            {
                "id": 1,
                "messenger_type": "bale",
                "account_name": "اکانت بله",
                "account_phone": "09123456789",
                "is_active": True,
                "is_verified": True
            },
            {
                "id": 2,
                "messenger_type": "eita",
                "account_name": "اکانت ایتا",
                "account_phone": "09123456790",
                "is_active": True,
                "is_verified": True
            }
        ]
    }


@app.post('/api/users/{user_id}/accounts')
async def create_messenger_account(user_id: int, account: MessengerAccountCreate):
    """Create a new messenger account"""
    return {
        "success": True,
        "account_id": 1,
        "message": "اکانت با موفقیت اضافه شد"
    }


@app.delete('/api/accounts/{account_id}')
async def delete_account(account_id: int):
    """Delete a messenger account"""
    return {"success": True, "message": "اکانت با موفقیت حذف شد"}


@app.post('/api/campaigns')
async def create_campaign(campaign: MessageCampaignCreate, user_id: int = 1):
    """Create a new message campaign"""
    # Distribute recipients across accounts
    account_count = len(campaign.account_ids)
    recipients_per_account = len(campaign.recipients) // account_count if account_count > 0 else 0
    
    return {
        "success": True,
        "campaign_id": 1,
        "message": "کمپین با موفقیت ایجاد شد",
        "distribution": {
            "total_recipients": len(campaign.recipients),
            "accounts_used": account_count,
            "recipients_per_account": recipients_per_account
        }
    }


@app.get('/api/campaigns')
async def get_campaigns(user_id: int = 1):
    """Get user's campaigns"""
    return {
        "campaigns": [
            {
                "id": 1,
                "name": "کمپین تست",
                "status": "completed",
                "total_recipients": 100,
                "sent_count": 98,
                "failed_count": 2,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }


@app.get('/api/campaigns/{campaign_id}')
async def get_campaign(campaign_id: int):
    """Get campaign details"""
    return {
        "id": campaign_id,
        "name": "کمپین تست",
        "message_text": "سلام، این یک پیام تست است",
        "status": "completed",
        "total_recipients": 100,
        "sent_count": 98,
        "failed_count": 2,
        "accounts_used": ["بله", "ایتا"],
        "created_at": "2024-01-01T00:00:00Z"
    }


@app.get('/api/stats')
async def get_stats(user_id: int = 1):
    """Get user statistics"""
    return {
        "total_accounts": 2,
        "total_campaigns": 5,
        "total_messages_sent": 1250,
        "success_rate": 98.5,
        "active_subscription": True
    }

