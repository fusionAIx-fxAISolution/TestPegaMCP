#!/usr/bin/env python3
import asyncio
import httpx
import json

async def call_pega_create_case(policy_number: str):
    """Call the pega_create_case tool via MCP"""
    url = "http://localhost:8001/mcp"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "pega_create_case",
            "arguments": {
                "PolicyNumber": policy_number
            }
        }
    }
    
    async with httpx.AsyncClient() as client:
        headers = {"Accept": "application/json, text/event-stream"}
        response = await client.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                print("Case created successfully!")
                print(f"Result: {result['result']}")
            else:
                print("Error in response:", result)
        else:
            print("Request failed")

if __name__ == "__main__":
    policy_number = "POL123456710"
    asyncio.run(call_pega_create_case(policy_number))