# app/integrations/ai_client.py
import httpx
from app.config.settings import settings
from typing import Optional, Dict, Any

class AIClient:
    @staticmethod
    async def predict_anomaly(event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.AI_ENGINE_URL}/api/predict",
                    json=event_data,
                    timeout=5.0
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
            except Exception:
                # Mock response for development
                return {"anomaly_score": 0.87, "prediction": "ATTACK"}