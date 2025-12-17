import os
import requests
import logging
from typing import Optional, Dict, Any
from .schemas import Interaction

logger = logging.getLogger(__name__)

class Client:
    def __init__(self, api_key: Optional[str] = None, api_url: str = "https://api.gateagent.dev"):
        self.api_key = api_key or os.environ.get("GATEAGENT_API_KEY")
        self.api_url = api_url.rstrip("/")
        
        if not self.api_key:
            logger.warning("Gateagent API Key not found. Traces will not be sent.")

    def log_interaction(self, interaction: Interaction) -> bool:
        """
        Sends the interaction data to the Gateagent API.
        Returns True if successful, False otherwise.
        """
        if not self.api_key:
            return False

        try:
            payload = interaction.model_dump(mode='json')
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Gateagent-Version": "0.1.0"
            }
            
            response = requests.post(
                f"{self.api_url}/api/v1/traces",
                json=payload,
                headers=headers,
                timeout=5.0
            )
            
            if response.status_code >= 400:
                logger.error(f"Failed to send trace to Gateagent: {response.status_code} - {response.text}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error sending trace to Gateagent: {e}")
            return False
