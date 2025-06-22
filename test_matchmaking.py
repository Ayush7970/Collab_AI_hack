#!/usr/bin/env python3
"""
Test script for the new AI-powered matchmaking functionality
"""

import requests
import json
import os

# Configuration
AGENT_URL = "http://127.0.0.1:8003"
FRONTEND_URL = "http://127.0.0.1:5000"

def test_health():
    """Test agent health"""
    print("🔍 Testing agent health...")
    try:
        response = requests.get(f"{AGENT_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent is healthy: {data['status']}")
            print(f"   Total users: {data['total_users']}")
            return True
        else:
            print(f"❌ Agent health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Agent health check error: {e}")
        return False

def test_create_profile():
    """Test profile creation"""
    print("\n🔍 Testing profile creation...")
    
    profile_data = {
        "user_id": "test_user",
        "name": "Test User",
        "bio": "A test user for matchmaking verification",
        "interests": ["testing", "development", "AI"],
        "skills": ["Python", "Testing", "Debugging"],
        "location": "Test City, TC",
        "profession": "Test Engineer"
    }
    
    try:
        response = requests.post(f"{AGENT_URL}/create_profile", json=profile_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Profile created successfully: {result['user_id']}")
                return True
            else:
                print(f"❌ Profile creation failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Profile creation request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Profile creation error: {e}")
        return False

def test_matchmaking():
    """Test AI matchmaking"""
    print("\n🔍 Testing AI matchmaking...")
    
    match_data = {
        "query": "Python developer for testing and debugging",
        "limit": 3
    }
    
    try:
        response = requests.post(f"{AGENT_URL}/match_users", json=match_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ AI matchmaking successful!")
                print(f"   Found {result['count']} matches")
                for i, match in enumerate(result['matches']):
                    print(f"   {i+1}. {match['name']} ({match['user_id']})")
                return True
            else:
                print(f"❌ AI matchmaking failed: {result.get('message')}")
                return False
        else:
            print(f"❌ AI matchmaking request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI matchmaking error: {e}")
        return False

def test_frontend_health():
    """Test frontend health"""
    print("\n🔍 Testing frontend health...")
    try:
        response = requests.get(f"{FRONTEND_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Frontend is healthy: {data['frontend']}")
            if data.get('agent'):
                print(f"   Agent status: {data['agent'].get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Frontend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend health check error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting AI Matchmaking System Tests")
    print("=" * 50)
    
    # Check if ANTHROPIC_API_KEY is set
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️  Warning: ANTHROPIC_API_KEY not set. Claude matchmaking may fail.")
        print("   Set it with: export ANTHROPIC_API_KEY='your_key_here'")
    
    tests = [
        ("Agent Health", test_health),
        ("Profile Creation", test_create_profile),
        ("AI Matchmaking", test_matchmaking),
        ("Frontend Health", test_frontend_health)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The AI matchmaking system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main() 