import asyncio
import httpx
import time
from typing import Optional

class TTSClient:
    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate_tts(self, text: str, engine: str = "kokkoro", voice: str = "default", speed: float = 1.0) -> Optional[bytes]:
        try:
            start_time = time.time()
            
            async with self.client.stream(
                "POST",
                f"{self.gateway_url}/tts",
                json={
                    "text": text,
                    "engine": engine,
                    "voice": voice,
                    "speed": speed
                }
            ) as response:
                if response.status_code != 200:
                    print(f"Error: {response.status_code} - {response.text}")
                    return None
                
                audio_data = b""
                async for chunk in response.aiter_bytes():
                    audio_data += chunk
                
                end_time = time.time()
                print(f"Generated {len(audio_data)} bytes in {end_time - start_time:.2f}s using {engine}")
                return audio_data
        
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    async def health_check(self) -> dict:
        try:
            response = await self.client.get(f"{self.gateway_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def engine_status(self) -> dict:
        try:
            response = await self.client.get(f"{self.gateway_url}/engines/status")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

async def test_all_engines():
    client = TTSClient("http://localhost:8000")  # Change to your gateway URL
    
    # Health check
    print("=== Health Check ===")
    health = await client.health_check()
    print(health)
    
    # Engine status
    print("\n=== Engine Status ===")
    status = await client.engine_status()
    print(status)
    
    # Test each engine
    test_text = "Hello, this is a test of the text-to-speech system."
    engines = ["kokkoro", "chatterbox", "coqui"]
    
    for engine in engines:
        print(f"\n=== Testing {engine.upper()} ===")
        audio_data = await client.generate_tts(test_text, engine=engine)
        
        if audio_data:
            # Save to file for testing
            filename = f"test_{engine}.mp3"
            with open(filename, "wb") as f:
                f.write(audio_data)
            print(f"Audio saved to {filename}")

async def load_test():
    client = TTSClient("http://localhost:8000")
    
    print("=== Load Test ===")
    tasks = []
    for i in range(10):
        task = client.generate_tts(
            f"This is load test message number {i+1}",
            engine="kokkoro"
        )
        tasks.append(task)
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    successful = sum(1 for r in results if r is not None)
    print(f"Completed {successful}/10 requests in {end_time - start_time:.2f}s")

if __name__ == "__main__":
    print("TTS System Test Client")
    print("1. Testing all engines...")
    asyncio.run(test_all_engines())
    
    print("\n2. Running load test...")
    asyncio.run(load_test())