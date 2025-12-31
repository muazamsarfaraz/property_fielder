#!/usr/bin/env python3
"""
Test script for Twilio SMS integration.
Sends a test SMS to verify credentials are working.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

def test_twilio_sms():
    """Send a test SMS via Twilio"""
    try:
        from twilio.rest import Client
    except ImportError:
        print("ERROR: Twilio library not installed. Run: pip install twilio")
        sys.exit(1)
    
    # Get credentials from environment
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_PHONE_NUMBER')
    
    if not all([account_sid, auth_token, from_number]):
        print("ERROR: Missing Twilio credentials in .env file")
        print(f"  TWILIO_ACCOUNT_SID: {'Set' if account_sid else 'Missing'}")
        print(f"  TWILIO_AUTH_TOKEN: {'Set' if auth_token else 'Missing'}")
        print(f"  TWILIO_PHONE_NUMBER: {'Set' if from_number else 'Missing'}")
        sys.exit(1)
    
    # Test phone number
    to_number = '+447507121721'
    
    print(f"Sending test SMS...")
    print(f"  From: {from_number}")
    print(f"  To: {to_number}")
    
    client = Client(account_sid, auth_token)
    
    try:
        message = client.messages.create(
            body="Test SMS from Property Fielder! Your Twilio integration is working correctly. 🎉",
            from_=from_number,
            to=to_number
        )
        
        print(f"\n✅ SUCCESS!")
        print(f"  Message SID: {message.sid}")
        print(f"  Status: {message.status}")
        print(f"\nCheck your phone for the test message.")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        sys.exit(1)


if __name__ == '__main__':
    test_twilio_sms()

