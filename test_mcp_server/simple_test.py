#!/usr/bin/env python3
"""
Simple test script to check case creation
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

async def test_case_creation():
    print('🔄 Loading Pega settings...')
    try:
        settings = PegaSettings.from_env()
        print(f'✅ Case Type ID: {settings.allowed_case_type_id}')
    except Exception as e:
        print(f'❌ Failed to load settings: {e}')
        return

    print('🔄 Initializing token helper...')
    try:
        token_helper = PegaTokenHelper(settings)
        print('✅ Token helper initialized')
    except Exception as e:
        print(f'❌ Failed to initialize token helper: {e}')
        return

    print('🔄 Getting access token...')
    try:
        token = await token_helper.get_valid_token()
        print(f'✅ Token obtained: {token[:20]}...')
    except Exception as e:
        print(f'❌ Failed to get token: {e}')
        return

    print('🔄 Initializing Pega client...')
    try:
        client = PegaCaseClient(settings, token_helper)
        print('✅ Pega client initialized')
    except Exception as e:
        print(f'❌ Failed to initialize client: {e}')
        return

    # Test basic case creation with processID (no content to avoid validation errors)
    payload = {
        'caseTypeID': settings.allowed_case_type_id,
        'processID': settings.allowed_create_process_id,
    }
    print(f'🔄 Creating case with payload: {payload}')

    try:
        result = await client.create_case(payload, 'none', None, settings.default_origin_channel)
        print('✅ Case created successfully!')
        print(f'   Case ID: {result.get("ID")}')
        print(f'   Full response: {result}')
        case_id_1 = result.get('ID')
    except Exception as e:
        print(f'❌ Error creating case: {e}')
        import traceback
        traceback.print_exc()
        case_id_1 = None

    # Now test with PolicyNumber
    print('\n🔄 Testing with PolicyNumber...')
    payload_with_policy = {
        'caseTypeID': settings.allowed_case_type_id,
        'processID': settings.allowed_create_process_id,
        'pyLabel': 'Policy: POL123456710',
        'content': {
            'PolicyNumber': 'POL123456710'
        }
    }
    print(f'🔄 Creating case with PolicyNumber payload: {payload_with_policy}')

    try:
        result = await client.create_case(payload_with_policy, 'none', None, settings.default_origin_channel)
        print('✅ Case with PolicyNumber created successfully!')
        print(f'   Case ID: {result.get("ID")}')
        print(f'   Full response: {result}')
        case_id_2 = result.get('ID')
    except Exception as e:
        print(f'❌ Error creating case with PolicyNumber: {e}')
        import traceback
        traceback.print_exc()
        case_id_2 = None

    return case_id_1 or case_id_2

if __name__ == "__main__":
    case_id = asyncio.run(test_case_creation())
    if case_id:
        print(f'\n🎉 Test completed! Case ID: {case_id}')
        print('Please check this case in your Pega environment.')
    else:
        print('\n❌ Test failed - no case created')