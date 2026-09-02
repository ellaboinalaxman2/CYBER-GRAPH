# app/integrations/attack_engine_client.py
import httpx
from app.config.settings import settings
from typing import Optional, Dict, Any

class AttackEngineClient:
    @staticmethod
    async def get_attack_path(alert_id: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.ATTACK_ENGINE_URL}/api/attack-path/{alert_id}",
                    timeout=5.0
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
            except Exception:
                # Mock
                return {
                    "alert_id": alert_id,
                    "path": ["PC-01", "Server-01", "Server-02", "DB-01"],
                    "risk_score": 94.0,
                    "severity": "CRITICAL"
                }