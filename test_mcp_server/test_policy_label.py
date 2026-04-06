#!/usr/bin/env python3
"""
Test script to create a case with policy number set to pyLabel
"""

import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.insert(0, 'app')

from app.pega_client import PegaCaseClient
from app.PegaSettings import PegaSettings
from app.Tokenhelper import PegaTokenHelper

async def test_policy_number():
    print('🔄 Testing policy number storage in pyLabel...')
    
    settings = PegaSettings.from_env()
    token_helper = PegaTokenHelper(settings)
    client = PegaCaseClient(settings, token_helper)
    
    # Test policy number
    policy_number = "POL-TEST-98765"
    
    # Create payload with policy number in pyLabel
    payload = {
        'caseTypeID': settings.allowed_case_type_id,
        'content': {
            'pyLabel': f'Policy: {policy_number}'
        }
    }
    
    print(f'📋 Creating case with policy number: {policy_number}')
    print(f'   Payload: {payload}')
    
    try:
        result = await client.create_case(payload, 'none', None, settings.default_origin_channel)
        print('✅ Case created successfully!')
        case_id = result.get('ID')
        print(f'   Case ID: {case_id}')
        print(f'   Policy Number: {policy_number}')
        print(f'   stored in: pyLabel')
        return case_id
    except Exception as e:
        print(f'❌ Error creating case: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    case_id = asyncio.run(test_policy_number())
    if case_id:
        print(f'\n🎉 Test completed! Case ID: {case_id}')
        print(f'Please check this case in Pega and verify pyLabel shows the policy number.')
    else:
        print('\n❌ Test failed')