from __future__ import annotations

import logging
from typing import Optional

import httpx

from src.config.settings import settings

logger = logging.getLogger(__name__)


class WecanSMSClient:
    """Simple REST client for WECAN SMS provider."""

    def __init__(self):
        self.rest_url = settings.wecan_rest_url
        self.token = settings.wecan_token
        self.from_number = settings.wecan_from_number

    @property
    def is_configured(self) -> bool:
        return all([self.rest_url, self.token, self.from_number])

    async def send_sms(self, phone_number: str, message: str | dict, template_id: Optional[int] = None) -> bool:
        if not self.is_configured:
            logger.warning("WECAN SMS not configured; skipping SMS send.")
            return False
        
        url = self.rest_url+"/sms/send"

        request_data = {
                "from": self.from_number,
                "recipients": [phone_number],
                "message": message,
                "type": 1,
            }

        if template_id:
            url = self.rest_url+"/sms/pattern-send"
            request_data["patternId"] = template_id

        headers = {
            "Content-Type": "application/json",
            "token": self.token or "",
        }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(url, json=request_data, headers=headers)
            logger.info("WECAN SMS response code: %s", response.status_code)
            if response.is_success:
                data = response.json()
                status = (
                    data.get("result", {}).get("status")
                    if isinstance(data, dict)
                    else None
                )
                if status == 0:
                    logger.info("WECAN SMS sent successfully.")
                    return True
                logger.error("WECAN SMS provider error: %s", data)
            else:
                logger.error("WECAN SMS HTTP error: %s - %s", response.status_code, response.text)
        except Exception as exc:
            logger.exception("WECAN SMS exception: %s", exc)
        return False


wecan_sms_client = WecanSMSClient()

