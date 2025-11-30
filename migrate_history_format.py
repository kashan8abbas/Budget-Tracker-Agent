"""
Migration script to convert old history format (array of numbers) to new format (array of objects).

This script will:
1. Read all projects from MongoDB
2. Convert history from [50, 500] to [{amount: 50, description: null, date: ..., category: null}, ...]
3. Save back to MongoDB

Run this once to migrate existing data.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

# Get MongoDB connection from env or config file
mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
mongo_db_name = os.getenv("MONGO_DB_NAME", "budget_tracker")

# Try to read from config file if not in env
if not mongo_uri:
    try:
        import json
        with open("config/agent_config.json", "r") as f:
            config = json.load(f)
            mongo_uri = config.get("mongo_uri")
            mongo_db_name = config.get("mongo_db_name", mongo_db_name)
    except:
        pass

if not mongo_uri:
    print("Error: MONGO_URI not found in environment variables or config file")
    print("Please set MONGO_URI in .env file or config/agent_config.json")
    exit(1)

def normalize_history(history):
    """Convert old format to new format"""
    if not history:
        return []
    
    normalized = []
    now = datetime.utcnow()
    
    for item in history:
        if isinstance(item, dict):
            # Already in new format, ensure required fields
            normalized.append({
                "amount": float(item.get("amount", item.get("value", 0))),
                "description": item.get("description"),
                "date": item.get("date", now.isoformat() + "Z"),
                "category": item.get("category")
            })
        elif isinstance(item, (int, float)):
            # Old format (just a number), convert to new format
            normalized.append({
                "amount": float(item),
                "description": None,
                "date": now.isoformat() + "Z",
                "category": None
            })
    
    return normalized

def migrate_projects():
    """Migrate all projects to new history format"""
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client[mongo_db_name]
        projects_collection = db["projects"]
        
        # Get all projects
        projects = list(projects_collection.find({}))
        
        print(f"Found {len(projects)} projects to migrate...")
        
        migrated_count = 0
        for proj in projects:
            project_id = proj.get("project_id")
            history = proj.get("history", [])
            
            # Check if migration needed
            needs_migration = False
            if history:
                # Check if any item is not a dict (old format)
                for item in history:
                    if not isinstance(item, dict):
                        needs_migration = True
                        break
            
            if needs_migration:
                # Normalize history
                normalized_history = normalize_history(history)
                
                # Update in MongoDB
                projects_collection.update_one(
                    {"project_id": project_id},
                    {
                        "$set": {
                            "history": normalized_history,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                print(f"✅ Migrated project: {proj.get('project_name', project_id)}")
                print(f"   History: {history} → {len(normalized_history)} entries")
                migrated_count += 1
            else:
                print(f"⏭️  Skipped project: {proj.get('project_name', project_id)} (already in new format)")
        
        print(f"\n✅ Migration complete! Migrated {migrated_count} projects.")
        client.close()
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔄 Starting history format migration...")
    print(f"MongoDB URI: {mongo_uri}")
    print(f"Database: {mongo_db_name}")
    print()
    
    migrate_projects()

