#!/usr/bin/env python3
"""Test different content structures for Smart Claim case creation"""
import asyncio
import httpx
from dotenv import load_dotenv
from app.PegaSettings import PegaSettings
from app.Tokenhelper import PegaTokenHelper

load_dotenv()

async def test_content_structures():
    """Test different content structures"""
    print("=" * 80)
    print("TESTING DIFFERENT CONTENT STRUCTURES FOR SMART CLAIM")
    print("=" * 80)
    
    settings = PegaSettings.from_env()
    token_helper = PegaTokenHelper(settings)
    
    token = await token_helper.get_valid_token()
    
    # Test different content structures
    test_payloads = [
        {
            "name": "User provided template",
            "payload": {
                "caseTypeID": "FAI-SmartClaim-Work-SmartClaim",
                "content": {
                    "PolicyNumber": ""
                }
            }
        },
        {
            "name": "Empty content",
            "payload": {
                "caseTypeID": "FAI-SmartClaim-Work-SmartClaim",
                "content": {}
            }
        },
        {
            "name": "No content field",
            "payload": {
                "caseTypeID": "FAI-SmartClaim-Work-SmartClaim"
            }
        },
        {
            "name": "Minimal content with PolicyNumber",
            "payload": {
                "caseTypeID": "FAI-SmartClaim-Work-SmartClaim",
                "content": {
                    "PolicyNumber": "TEST123"
                }
            }
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for test in test_payloads:
            print(f"\n--- Testing: {test['name']} ---")
            print(f"Payload: {test['payload']}")
            
            try:
                response = await client.post(
                    f"{settings.pega_application_api_base}/cases",
                    json=test['payload'],
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },
                    timeout=30,
                    follow_redirects=False
                )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 303:
                    print("✓ Success! Case created.")
                    # Extract case ID from Location header
                    location = response.headers.get('location', '')
                    if 'pzPostData=' in location:
                        case_id = location.split('pzPostData=')[-1]
                        print(f"Case ID: {case_id}")
                    break
                elif response.status_code == 400:
                    print(f"✗ 400 Error: {response.text}")
                else:
                    print(f"Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_content_structures())
