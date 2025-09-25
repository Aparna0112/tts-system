import asyncio
import httpx
import logging
from datetime import datetime
from typing import Dict, List
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSMonitor:
    def __init__(self, endpoints: Dict[str, str]):
        self.endpoints = endpoints
        self.client = httpx.AsyncClient(timeout=10.0)
        self.metrics = {}
    
    async def check_health(self, name: str, url: str) -> Dict:
        try:
            response = await self.client.get(f"{url}/health")
            return {
                "name": name,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "name": name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_engine_status(self, name: str, url: str) -> Dict:
        try:
            response = await self.client.get(f"{url}/status")
            if response.status_code == 200:
                return {"name": name, **response.json()}
            return {"name": name, "error": "status_unavailable"}
        except Exception as e:
            return {"name": name, "error": str(e)}
    
    async def monitor_all(self) -> Dict:
        health_tasks = [
            self.check_health(name, url) 
            for name, url in self.endpoints.items()
        ]
        status_tasks = [
            self.get_engine_status(name, url) 
            for name, url in self.endpoints.items()
        ]
        
        health_results = await asyncio.gather(*health_tasks, return_exceptions=True)
        status_results = await asyncio.gather(*status_tasks, return_exceptions=True)
        
        return {
            "health": health_results,
            "status": status_results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def continuous_monitoring(self, interval: int = 30):
        while True:
            try:
                results = await self.monitor_all()
                logger.info(f"Monitoring results: {json.dumps(results, indent=2)}")
                
                # Check for unhealthy services
                for health in results["health"]:
                    if isinstance(health, dict) and health.get("status") != "healthy":
                        logger.warning(f"Service {health['name']} is unhealthy: {health}")
                
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(interval)

async def main():
    endpoints = {
        "gateway": "https://gateway-endpoint.runpod.io",
        "kokkoro": "https://kokkoro-endpoint.runpod.io",
        "chatterbox": "https://chatterbox-endpoint.runpod.io",
        "coqui": "https://coqui-endpoint.runpod.io"
    }
    
    monitor = TTSMonitor(endpoints)
    await monitor.continuous_monitoring()

if __name__ == "__main__":
    asyncio.run(main())