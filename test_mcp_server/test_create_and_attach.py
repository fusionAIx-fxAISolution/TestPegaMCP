#!/usr/bin/env python3
"""
Pega Case Creation and Attachment Integration
"""

import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add app directory to path
sys.path.insert(0, 'app')

from app.pega_client import PegaCaseClient
from app.PegaSettings import PegaSettings
from app.Tokenhelper import PegaTokenHelper


if __name__ == "__main__":
    print("Integration code ready for Copilot testing")
