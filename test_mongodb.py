"""
Simple test script to verify MongoDB Atlas connection and LTM operations.
"""

import json
from agents.workers.budget_tracker_agent import BudgetTrackerAgent

def test_mongodb_connection():
    """Test MongoDB connection and basic LTM operations."""
    print("=" * 70)
    print("Testing MongoDB Atlas Integration")
    print("=" * 70)
    
    # Initialize agent (will connect to MongoDB if configured)
    print("\n1. Initializing Budget Tracker Agent...")
    agent = BudgetTrackerAgent()
    
    # Check if MongoDB is being used
    if agent.use_mongodb:
        print("✅ Connected to MongoDB Atlas!")
        print(f"   Database: {agent.mongo_db_name}")
        print(f"   Collections: tasks, current_budget")
    else:
        print("⚠️  MongoDB not connected - using file-based LTM")
        print(f"   LTM Path: {agent.ltm_path}")
        if not agent.mongo_uri:
            print("   Reason: No MongoDB URI configured")
        else:
            print("   Reason: Connection failed or pymongo not installed")
        return
    
    # Test 1: Write to LTM
    print("\n2. Testing write_to_ltm()...")
    test_key = "test_key_123"
    test_value = {"test": "data", "number": 42}
    success = agent.write_to_ltm(test_key, test_value)
    if success:
        print("✅ Successfully wrote to MongoDB")
    else:
        print("❌ Failed to write to MongoDB")
        return
    
    # Test 2: Read from LTM
    print("\n3. Testing read_from_ltm()...")
    retrieved = agent.read_from_ltm(test_key)
    if retrieved == test_value:
        print("✅ Successfully read from MongoDB")
        print(f"   Retrieved: {retrieved}")
    else:
        print("❌ Failed to read from MongoDB")
        print(f"   Expected: {test_value}")
        print(f"   Got: {retrieved}")
        return
    
    # Test 3: Update current budget
    print("\n4. Testing update_current_budget()...")
    try:
        success = agent.update_current_budget(
            budget_limit=10000.0,
            spent=500.0,
            history=[100, 200, 200]
        )
        if success:
            print("✅ Successfully updated current budget")
        else:
            print("❌ Failed to update current budget (returned False)")
            # Try to get more info
            import traceback
            traceback.print_exc()
            return
    except Exception as e:
        print(f"❌ Failed to update current budget: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 4: Get current budget
    print("\n5. Testing get_current_budget()...")
    current = agent.get_current_budget()
    if current:
        print("✅ Successfully retrieved current budget")
        print(f"   Budget Limit: ${current.get('budget_limit', 0):,.2f}")
        print(f"   Spent: ${current.get('spent', 0):,.2f}")
        print(f"   History: {current.get('history', [])}")
    else:
        print("❌ Failed to retrieve current budget")
        return
    
    # Test 5: Process a real task
    print("\n6. Testing full task processing...")
    task_data = {
        "parameters": {
            "budget_limit": 50000,
            "spent": 42000,
            "history": [5000, 7000, 8000, 6000]
        },
        "intent": "check",
        "user_query": "Check my budget"
    }
    
    try:
        results = agent.process_task(task_data)
        print("✅ Successfully processed task")
        print(f"   Remaining: ${results.get('remaining', 0):,.2f}")
        print(f"   Overshoot Risk: {results.get('overshoot_risk', False)}")
    except Exception as e:
        print(f"❌ Failed to process task: {e}")
        return
    
    # Cleanup
    print("\n7. Cleaning up test data...")
    try:
        if agent.use_mongodb:
            # Remove test key from MongoDB
            tasks_collection = agent.mongo_db["tasks"]
            tasks_collection.delete_one({"key": test_key, "agent_id": agent._id})
            print("✅ Cleaned up test data")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
    
    # Close connection
    agent.close()
    
    print("\n" + "=" * 70)
    print("✅ All tests passed! MongoDB integration is working correctly.")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_mongodb_connection()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

