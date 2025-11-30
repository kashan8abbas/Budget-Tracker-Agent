"""
Simple test script for Budget Tracker Agent API

Run this after starting the API server to test all endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("=" * 70)
    print("Testing Health Check")
    print("=" * 70)
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ Health check passed\n")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}\n")
        return False

def test_query():
    """Test natural language query endpoint"""
    print("=" * 70)
    print("Testing Natural Language Query")
    print("=" * 70)
    try:
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": "Check my budget: 50000 limit, 42000 spent"}
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Remaining: ${data.get('remaining', 0):,.2f}")
        print(f"Overshoot Risk: {data.get('overshoot_risk', False)}")
        print(f"Response: {data.get('response', 'N/A')[:100]}...")
        print("✅ Query test passed\n")
        return True
    except Exception as e:
        print(f"❌ Query test failed: {e}\n")
        return False

def test_analyze():
    """Test analyze endpoint"""
    print("=" * 70)
    print("Testing Budget Analysis")
    print("=" * 70)
    try:
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json={
                "parameters": {
                    "budget_limit": 50000,
                    "spent": 42000,
                    "history": [5000, 7000, 8000, 6000]
                },
                "intent": "check"
            }
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Remaining: ${data.get('remaining', 0):,.2f}")
        print(f"Spending Rate: ${data.get('spending_rate', 0) or 0:,.2f}")
        print(f"Overshoot Risk: {data.get('overshoot_risk', False)}")
        print("✅ Analysis test passed\n")
        return True
    except Exception as e:
        print(f"❌ Analysis test failed: {e}\n")
        return False

def test_update():
    """Test update endpoint"""
    print("=" * 70)
    print("Testing Budget Update")
    print("=" * 70)
    try:
        response = requests.post(
            f"{BASE_URL}/api/update",
            json={
                "update_type": "add",
                "update_field": "spent",
                "update_value": 1000
            }
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        if data.get('budget'):
            budget = data['budget']
            print(f"Updated Budget - Remaining: ${budget.get('remaining', 0):,.2f}")
        print("✅ Update test passed\n")
        return True
    except Exception as e:
        print(f"❌ Update test failed: {e}\n")
        return False

def test_get_budget():
    """Test get current budget endpoint"""
    print("=" * 70)
    print("Testing Get Current Budget")
    print("=" * 70)
    try:
        response = requests.get(f"{BASE_URL}/api/budget")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        if data.get('budget_limit'):
            print(f"Budget Limit: ${data.get('budget_limit', 0):,.2f}")
            print(f"Spent: ${data.get('spent', 0):,.2f}")
            print(f"Remaining: ${data.get('remaining', 0):,.2f}")
        else:
            print("No budget data found (this is OK if no budget has been set)")
        print("✅ Get budget test passed\n")
        return True
    except Exception as e:
        print(f"❌ Get budget test failed: {e}\n")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Budget Tracker Agent API Test Suite")
    print("=" * 70)
    print(f"Testing API at: {BASE_URL}")
    print("Make sure the API server is running!\n")
    
    results = []
    
    # Run all tests
    results.append(("Health Check", test_health()))
    results.append(("Natural Language Query", test_query()))
    results.append(("Budget Analysis", test_analyze()))
    results.append(("Budget Update", test_update()))
    results.append(("Get Current Budget", test_get_budget()))
    
    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 70)

