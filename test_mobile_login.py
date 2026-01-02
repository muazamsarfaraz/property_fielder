#!/usr/bin/env python3
"""
Test script to verify mobile API login endpoint
"""

import requests
import json

# Configuration
ODOO_URL = "http://localhost:8069"
DB_NAME = "property_fielder"

def test_login(username, password):
    """Test the mobile login endpoint"""
    url = f"{ODOO_URL}/mobile/api/auth/login"
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "username": username,
            "password": password
        },
        "id": 1
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"\n🔐 Testing login for user: {username}")
    print(f"📡 URL: {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📄 Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            result = response.json().get('result', {})
            if result.get('success'):
                print("\n✅ Login successful!")
                print(f"   User ID: {result.get('user_id')}")
                print(f"   Inspector ID: {result.get('inspector_id')}")
                print(f"   Inspector Name: {result.get('inspector_name')}")
                print(f"   Session ID: {result.get('session_id')}")
                return True
            else:
                print(f"\n❌ Login failed: {result.get('error')}")
                return False
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out - backend might not be running")
        return False
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection error - backend not accessible")
        print("   Make sure Odoo is running: docker-compose up -d")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

def check_backend_health():
    """Check if backend is accessible"""
    url = f"{ODOO_URL}/web/health"
    print(f"\n🏥 Checking backend health...")
    print(f"📡 URL: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy!")
            return True
        else:
            print(f"⚠️ Backend returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Property Fielder Mobile API Login Test")
    print("=" * 60)
    
    # Check backend health first
    if not check_backend_health():
        print("\n⚠️ Backend is not accessible. Please start it with:")
        print("   cd property_fielder")
        print("   docker-compose up -d")
        exit(1)
    
    # Test login with admin credentials
    print("\n" + "=" * 60)
    print("Test 1: Admin Login")
    print("=" * 60)
    test_login("admin", "admin")
    
    # Test login with inspector credentials
    print("\n" + "=" * 60)
    print("Test 2: Inspector Login")
    print("=" * 60)
    test_login("inspector", "inspector123")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\n📝 Next Steps:")
    print("   1. If login failed, create an inspector user in Odoo")
    print("   2. Access Odoo: http://localhost:8069")
    print("   3. Login as admin/admin")
    print("   4. Create inspector user and link to inspector profile")
    print("   5. Try logging in to the mobile app!")

