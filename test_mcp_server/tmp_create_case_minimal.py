#!/usr/bin/env python3
import asyncio
import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, 'app')
from app.PegaSettings import PegaSettings
from app.Tokenhelper import PegaTokenHelper
import httpx

async def main():
    settings = PegaSettings.from_env()
    token_helper = PegaTokenHelper(settings)
    token = await token_helper.get_valid_token()
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
    payload = {
        'caseTypeID': settings.allowed_case_type_id,
        'processID': settings.allowed_create_process_id,
    }
    print('payload=', payload)
    async with httpx.AsyncClient(follow_redirects=False) as client:
        response = await client.post(
            f'{settings.pega_application_api_base}/cases',
            json=payload,
            headers=headers,
            timeout=30,
        )
        print('status', response.status_code)
        print('location', response.headers.get('location'))
        print('body', response.text[:1200])

if __name__ == '__main__':
    asyncio.run(main())
