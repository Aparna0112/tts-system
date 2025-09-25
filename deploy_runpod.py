import runpod
import os

# Set your RunPod API key
runpod.api_key = "YOUR_RUNPOD_API_KEY_HERE"

def deploy_engine(name, dockerfile_path):
    """Deploy a single TTS engine to RunPod"""
    
    # Create serverless endpoint
    endpoint = runpod.create_endpoint(
        name=name,
        image_name=f"tts-{name}:latest",
        gpu_ids="NVIDIA GeForce RTX 4090",
        container_disk_in_gb=20,
        env={
            "CUDA_VISIBLE_DEVICES": "0"
        }
    )
    
    print(f"Deployed {name}: {endpoint['id']}")
    return endpoint

def main():
    print("Deploying TTS System to RunPod...")
    
    # Deploy engines
    engines = ["kokkoro", "chatterbox", "coqui"]
    endpoints = {}
    
    for engine in engines:
        print(f"Deploying {engine}...")
        endpoint = deploy_engine(engine, f"engines/{engine}")
        endpoints[engine] = endpoint
    
    # Deploy gateway
    print("Deploying gateway...")
    gateway = deploy_engine("gateway", "gateway")
    endpoints["gateway"] = gateway
    
    print("\nDeployment complete!")
    print("Endpoints:")
    for name, endpoint in endpoints.items():
        print(f"{name}: https://{endpoint['id']}-runpod.io")

if __name__ == "__main__":
    main()