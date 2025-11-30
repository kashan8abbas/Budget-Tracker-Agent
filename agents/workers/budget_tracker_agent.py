"""
Budget Tracker Agent - Worker Agent for Budget Analysis and Monitoring

This agent:
- Monitors budgets and detects overspending
- Performs simple predictions based on spending history
- Provides recommendations for budget management
- Stores past results in Long-Term Memory (LTM)
"""

import json
import os
import statistics
from typing import Any, Optional, Dict, List
from datetime import datetime

from .worker_base import AbstractWorkerAgent
from communication.schemas import BudgetTaskParameters, BudgetAnalysisResults

# MongoDB support (optional)
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, OperationFailure
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    MongoClient = None


class BudgetTrackerAgent(AbstractWorkerAgent):
    """
    Worker Agent specialized in budget tracking and analysis.
    
    Implements rule-based logic for:
    - Budget remaining calculation
    - Spending rate analysis
    - Overspend risk prediction
    - Anomaly detection
    - Budget recommendations
    """

    def __init__(self, agent_id: str = "BudgetTrackerAgent", 
                 supervisor_id: str = "SupervisorAgent",
                 config_path: str = "config/agent_config.json"):
        """
        Initialize the Budget Tracker Agent.
        
        Args:
            agent_id: Unique identifier for this agent
            supervisor_id: Identifier of the supervisor agent
            config_path: Path to agent configuration file
        """
        super().__init__(agent_id, supervisor_id)
        
        # Load configuration
        self.config = self._load_config(config_path)
        self.ltm_path = self.config.get("ltm_path", "LTM/BudgetTrackerAgent/memory.json")
        self.enable_ltm_cache = self.config.get("enable_ltm_cache", True)
        self.anomaly_threshold = self.config.get("anomaly_threshold_multiplier", 2.0)
        
        # MongoDB configuration
        self.mongo_uri = self.config.get("mongo_uri") or os.getenv("MONGODB_URI")
        self.mongo_db_name = self.config.get("mongo_db_name", "budget_tracker")
        self.mongo_client = None
        self.mongo_db = None
        self.use_mongodb = False
        
        # Initialize MongoDB connection if URI is provided
        if self.mongo_uri and MONGO_AVAILABLE:
            try:
                self.mongo_client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
                # Test connection
                self.mongo_client.admin.command('ping')
                self.mongo_db = self.mongo_client[self.mongo_db_name]
                self.use_mongodb = True
                # print(f"[{self._id}] Connected to MongoDB Atlas")
            except (ConnectionFailure, Exception) as e:
                # print(f"[{self._id}] MongoDB connection failed, falling back to file-based LTM: {e}")
                self.use_mongodb = False
                self.mongo_client = None
                self.mongo_db = None
        
        # Initialize LTM (file-based if MongoDB not available)
        self._initialize_ltm()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load agent configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # print(f"[{self._id}] Warning: Config file not found, using defaults")
            return {}
        except json.JSONDecodeError as e:
            # print(f"[{self._id}] Error loading config: {e}")
            return {}

    def _initialize_ltm(self):
        """Initialize LTM (MongoDB or file-based) with empty structure if it doesn't exist."""
        if self.use_mongodb:
            # MongoDB initialization - collections are created automatically on first insert
            # Just ensure indexes exist
            try:
                tasks_collection = self.mongo_db["tasks"]
                current_budget_collection = self.mongo_db["current_budget"]
                # Create indexes for better performance
                tasks_collection.create_index("key", unique=True)
                current_budget_collection.create_index("agent_id", unique=True)
                # Ensure current_budget document exists
                if current_budget_collection.count_documents({"agent_id": self._id}) == 0:
                    current_budget_collection.insert_one({
                        "agent_id": self._id,
                        "current_budget": None
                    })
            except Exception as e:
                # print(f"[{self._id}] Error initializing MongoDB LTM: {e}")
                pass
        else:
            # File-based initialization
            ltm_dir = os.path.dirname(self.ltm_path)
            if ltm_dir and not os.path.exists(ltm_dir):
                os.makedirs(ltm_dir, exist_ok=True)
            
            if not os.path.exists(self.ltm_path):
                initial_data = {
                    "current_budget": None,  # Stores current budget context
                    "tasks": {}
                }
                with open(self.ltm_path, 'w') as f:
                    json.dump(initial_data, f, indent=2)
                # print(f"[{self._id}] Initialized LTM at {self.ltm_path}")
            else:
                # Ensure current_budget exists in existing LTM
                try:
                    with open(self.ltm_path, 'r') as f:
                        ltm_data = json.load(f)
                    if "current_budget" not in ltm_data:
                        ltm_data["current_budget"] = None
                        with open(self.ltm_path, 'w') as f:
                            json.dump(ltm_data, f, indent=2)
                except:
                    pass  # If file is corrupted, will be fixed on next write

    def _generate_ltm_key(self, task_data: Dict[str, Any], project_id: str = None) -> str:
        """
        Generate a unique key for LTM storage based on task parameters and project.
        
        Format: "{project_id}:analyze_budget:{budget_limit}:{spent}:{history_hash}"
        """
        project_id = project_id or self.get_current_project_id() or "default"
        budget_limit = task_data.get("budget_limit", 0)
        spent = task_data.get("spent", 0)
        history = task_data.get("history", [])
        
        # Create a simple hash from history (sum of first 5 values or all if less)
        if history:
            history_str = ",".join(map(str, history[:5]))
        else:
            history_str = "no_history"
        
        return f"{project_id}:analyze_budget:{budget_limit}:{spent}:{history_str}"

    def read_from_ltm(self, key: str, project_id: str = None) -> Optional[Any]:
        """
        Reads a value from the agent's LTM based on the key.
        
        Args:
            key: The LTM key to look up
            
        Returns:
            The stored value or None if the key is not found
        """
        if self.use_mongodb:
            try:
                tasks_collection = self.mongo_db["tasks"]
                query = {"key": key, "agent_id": self._id}
                if project_id:
                    query["project_id"] = project_id
                result = tasks_collection.find_one(query)
                if result:
                    return result.get("value")
                return None
            except Exception as e:
                # print(f"[{self._id}] Error reading from MongoDB LTM: {e}")
                return None
        else:
            # File-based read
            try:
                if not os.path.exists(self.ltm_path):
                    return None
                
                with open(self.ltm_path, 'r') as f:
                    ltm_data = json.load(f)
                
                tasks = ltm_data.get("tasks", {})
                return tasks.get(key)
            except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
                # print(f"[{self._id}] Error reading from LTM: {e}")
                return None

    def write_to_ltm(self, key: str, value: Any, project_id: str = None) -> bool:
        """
        Writes a key-value pair to the agent's Long-Term Memory (LTM).
        
        Args:
            key: The LTM key to store
            value: The value to store
            
        Returns:
            True on success, False otherwise
        """
        if self.use_mongodb:
            try:
                tasks_collection = self.mongo_db["tasks"]
                project_id = project_id or self.get_current_project_id() or "default"
                # Upsert: update if exists, insert if not
                tasks_collection.update_one(
                    {"key": key, "agent_id": self._id, "project_id": project_id},
                    {
                        "$set": {
                            "key": key,
                            "agent_id": self._id,
                            "project_id": project_id,
                            "value": value,
                            "updated_at": datetime.utcnow()
                        }
                    },
                    upsert=True
                )
                # print(f"[{self._id}] Stored result in MongoDB LTM with key: {key}")
                return True
            except Exception as e:
                # print(f"[{self._id}] Error writing to MongoDB LTM: {e}")
                return False
        else:
            # File-based write
            try:
                # Load existing LTM data
                if os.path.exists(self.ltm_path):
                    with open(self.ltm_path, 'r') as f:
                        ltm_data = json.load(f)
                else:
                    ltm_data = {"current_budget": None, "tasks": {}}
                
                # Update with new entry
                if "tasks" not in ltm_data:
                    ltm_data["tasks"] = {}
                
                ltm_data["tasks"][key] = value
                
                # Write back to file
                with open(self.ltm_path, 'w') as f:
                    json.dump(ltm_data, f, indent=2)
                
                # print(f"[{self._id}] Stored result in LTM with key: {key}")
                return True
            except Exception as e:
                # print(f"[{self._id}] Error writing to LTM: {e}")
                return False
    
    def _normalize_history(self, history: Any) -> List[Dict[str, Any]]:
        """
        Normalize history to new format (array of objects).
        Handles backward compatibility with old format (array of numbers).
        
        Args:
            history: History in any format (array of numbers, array of objects, or None)
            
        Returns:
            List of history objects with structure:
            {
                "amount": float,
                "description": str or None,
                "date": str (ISO format),
                "category": str or None
            }
        """
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
            else:
                # Skip invalid entries
                continue
        
        return normalized
    
    def _extract_amounts_from_history(self, history: List[Dict[str, Any]]) -> List[float]:
        """
        Extract amounts from history objects for calculations.
        
        Args:
            history: List of history objects
            
        Returns:
            List of amounts (floats)
        """
        if not history:
            return []
        
        amounts = []
        for item in history:
            if isinstance(item, dict):
                amounts.append(float(item.get("amount", item.get("value", 0))))
            elif isinstance(item, (int, float)):
                amounts.append(float(item))
        
        return amounts
    
    def get_current_budget(self, project_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve the current budget context from LTM.
        
        Returns:
            Dictionary with current budget state or None if not set
        """
        if self.use_mongodb:
            try:
                projects_collection = self.mongo_db["projects"]
                project_id = project_id or self.get_current_project_id()
                if not project_id:
                    return None
                result = projects_collection.find_one({"project_id": project_id, "agent_id": self._id})
                if result:
                    history = result.get("history", [])
                    # Normalize history to new format
                    history = self._normalize_history(history)
                    return {
                        "budget_limit": result.get("budget_limit", 0.0),
                        "spent": result.get("spent", 0.0),
                        "history": history,
                        "last_updated": result.get("updated_at", result.get("created_at"))
                    }
                return None
            except Exception as e:
                # print(f"[{self._id}] Error reading current budget from MongoDB: {e}")
                return None
        else:
            # File-based read
            try:
                if not os.path.exists(self.ltm_path):
                    return None
                
                with open(self.ltm_path, 'r') as f:
                    ltm_data = json.load(f)
                
                # For file-based, check if projects structure exists
                projects = ltm_data.get("projects", {})
                current_project_id = ltm_data.get("current_project")
                if current_project_id and current_project_id in projects:
                    proj_data = projects[current_project_id]
                    if isinstance(proj_data, dict):
                        # Normalize history
                        if "history" in proj_data:
                            proj_data["history"] = self._normalize_history(proj_data["history"])
                    return proj_data
                # Fallback to old structure
                current = ltm_data.get("current_budget")
                if current and isinstance(current, dict) and "history" in current:
                    current["history"] = self._normalize_history(current["history"])
                return current
            except Exception as e:
                # print(f"[{self._id}] Error reading current budget: {e}")
                return None
    
    def update_current_budget(self, budget_limit: float = None, spent: float = None, 
                              history: List[float] = None, update_type: str = None,
                              update_field: str = None, update_value: Any = None,
                              project_id: str = None) -> bool:
        """
        Update the current budget context in LTM.
        
        Args:
            budget_limit: New budget limit (if updating)
            spent: New spent amount (if updating)
            history: New history array (if updating)
            update_type: "add", "replace", or "set"
            update_field: "spent", "budget_limit", or "history"
            update_value: Value to add/replace
            
        Returns:
            True on success, False otherwise
        """
        if self.use_mongodb:
            try:
                projects_collection = self.mongo_db["projects"]
                project_id = project_id or self.get_current_project_id()
                
                if not project_id:
                    # No project set, cannot update
                    return False
                
                # Get current project budget or create new
                result = projects_collection.find_one({"project_id": project_id, "agent_id": self._id})
                if result:
                    # Normalize history to new format
                    history = result.get("history", [])
                    history = self._normalize_history(history)
                    
                    current = {
                        "budget_limit": result.get("budget_limit", 0.0),
                        "spent": result.get("spent", 0.0),
                        "history": history
                    }
                else:
                    # Project doesn't exist, cannot update
                    return False
                
                # Ensure current is a dict with required fields
                if not isinstance(current, dict):
                    current = {}
                if "budget_limit" not in current:
                    current["budget_limit"] = 0.0
                if "spent" not in current:
                    current["spent"] = 0.0
                if "history" not in current:
                    current["history"] = []
                
                # ALWAYS normalize history (convert old format to new format)
                current["history"] = self._normalize_history(current["history"])
                
                # Handle updates
                if update_type and update_field and update_value is not None:
                    if update_field == "spent":
                        if update_type == "add":
                            amount = float(update_value)
                            current["spent"] = current.get("spent", 0.0) + amount
                            # Get description if available
                            description = None
                            if hasattr(self, '_current_spending_description'):
                                description = getattr(self, '_current_spending_description', None)
                            
                            # Add to history with description
                            current["history"].append({
                                "amount": amount,
                                "description": description,
                                "date": datetime.utcnow().isoformat() + "Z",
                                "category": None
                            })
                        elif update_type == "replace" or update_type == "set":
                            current["spent"] = float(update_value)
                    
                    elif update_field == "budget_limit":
                        current["budget_limit"] = float(update_value)
                    
                    elif update_field == "history":
                        if update_type == "add":
                            # Normalize and add
                            if isinstance(update_value, list):
                                normalized = self._normalize_history(update_value)
                                current["history"].extend(normalized)
                            else:
                                normalized = self._normalize_history([update_value])
                                current["history"].extend(normalized)
                        elif update_type == "replace" or update_type == "set":
                            # Normalize and replace
                            if isinstance(update_value, list):
                                current["history"] = self._normalize_history(update_value)
                            else:
                                current["history"] = self._normalize_history([update_value])
                
                # Apply direct updates (if provided)
                if budget_limit is not None:
                    current["budget_limit"] = float(budget_limit)
                
                # Track if spent was updated to preserve auto-calculated history
                spent_was_updated = False
                if spent is not None:
                    spent_value = float(spent)
                    # If setting spent directly and it's different from current, add difference to history
                    current_spent = current.get("spent", 0.0)
                    if spent_value != current_spent:
                        spent_was_updated = True
                        # Calculate difference
                        difference = spent_value - current_spent
                        if difference > 0:
                            # Get description if available
                            description = None
                            if hasattr(self, '_current_spending_description'):
                                description = getattr(self, '_current_spending_description', None)
                            
                            # Add the difference to history (new spending) with description
                            current["history"].append({
                                "amount": difference,
                                "description": description,
                                "date": datetime.utcnow().isoformat() + "Z",
                                "category": None
                            })
                        # Update spent
                        current["spent"] = spent_value
                    else:
                        # Same value, just set it
                        current["spent"] = spent_value
                
                # Only overwrite history if spent was NOT updated (to preserve auto-calculated history)
                # OR if history is explicitly provided and spent is not being updated
                if history is not None and not spent_was_updated:
                    # Normalize history to new format
                    current["history"] = self._normalize_history(history)
                
                # Ensure history is always normalized before saving
                current["history"] = self._normalize_history(current["history"])
                
                # Update timestamp
                now = datetime.utcnow()
                
                # Save to MongoDB projects collection
                projects_collection.update_one(
                    {"project_id": project_id, "agent_id": self._id},
                    {
                        "$set": {
                            "budget_limit": current["budget_limit"],
                            "spent": current["spent"],
                            "history": current["history"],
                            "updated_at": now
                        }
                    }
                )
                
                # print(f"[{self._id}] Updated current budget in MongoDB LTM")
                return True
            except Exception as e:
                print(f"[{self._id}] Error updating current budget in MongoDB: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            # File-based update
            try:
                # Load existing LTM data
                if os.path.exists(self.ltm_path):
                    with open(self.ltm_path, 'r') as f:
                        ltm_data = json.load(f)
                else:
                    ltm_data = {"current_budget": None, "tasks": {}}
                
                # Get current budget or create new
                current = ltm_data.get("current_budget")
                if current is None:
                    current = {
                        "budget_limit": 0.0,
                        "spent": 0.0,
                        "history": []
                    }
                
                # Normalize existing history first
                if "history" in current:
                    current["history"] = self._normalize_history(current["history"])
                else:
                    current["history"] = []
                
                # Handle updates
                if update_type and update_field and update_value is not None:
                    if update_field == "spent":
                        if update_type == "add":
                            amount = float(update_value)
                            current["spent"] = current.get("spent", 0.0) + amount
                            # Get description if available
                            description = None
                            if hasattr(self, '_current_spending_description'):
                                description = getattr(self, '_current_spending_description', None)
                            
                            # Add to history with description
                            current["history"].append({
                                "amount": amount,
                                "description": description,
                                "date": datetime.utcnow().isoformat() + "Z",
                                "category": None
                            })
                        elif update_type == "replace" or update_type == "set":
                            current["spent"] = float(update_value)
                    
                    elif update_field == "budget_limit":
                        current["budget_limit"] = float(update_value)
                    
                    elif update_field == "history":
                        if update_type == "add":
                            # Normalize and add
                            if isinstance(update_value, list):
                                normalized = self._normalize_history(update_value)
                                current["history"].extend(normalized)
                            else:
                                normalized = self._normalize_history([update_value])
                                current["history"].extend(normalized)
                        elif update_type == "replace" or update_type == "set":
                            # Normalize and replace
                            if isinstance(update_value, list):
                                current["history"] = self._normalize_history(update_value)
                            else:
                                current["history"] = self._normalize_history([update_value])
                
                # Apply direct updates (if provided)
                if budget_limit is not None:
                    current["budget_limit"] = float(budget_limit)
                
                # Track if spent was updated to preserve auto-calculated history
                spent_was_updated = False
                if spent is not None:
                    spent_value = float(spent)
                    # If setting spent directly and it's different from current, add difference to history
                    current_spent = current.get("spent", 0.0)
                    if spent_value != current_spent:
                        spent_was_updated = True
                        # Calculate difference
                        difference = spent_value - current_spent
                        if difference > 0:
                            # Get description if available
                            description = None
                            if hasattr(self, '_current_spending_description'):
                                description = getattr(self, '_current_spending_description', None)
                            
                            # Add the difference to history (new spending) with description
                            current["history"].append({
                                "amount": difference,
                                "description": description,
                                "date": datetime.utcnow().isoformat() + "Z",
                                "category": None
                            })
                        # Update spent
                        current["spent"] = spent_value
                    else:
                        # Same value, just set it
                        current["spent"] = spent_value
                
                # Only overwrite history if spent was NOT updated (to preserve auto-calculated history)
                # OR if history is explicitly provided and spent is not being updated
                if history is not None and not spent_was_updated:
                    # Normalize history to new format
                    current["history"] = self._normalize_history(history)
                
                # Ensure history is always normalized before saving
                current["history"] = self._normalize_history(current["history"])
                
                # Update timestamp
                now = datetime.utcnow()
                current["last_updated"] = now.isoformat() + "Z"
                
                # Save back - use projects structure if available
                if "projects" not in ltm_data:
                    ltm_data["projects"] = {}
                
                project_id = project_id or ltm_data.get("current_project") or "default"
                ltm_data["projects"][project_id] = current
                ltm_data["current_project"] = project_id
                
                # Also keep old structure for backward compatibility
                if project_id == "default" or not ltm_data.get("current_project"):
                    ltm_data["current_budget"] = current
                
                with open(self.ltm_path, 'w') as f:
                    json.dump(ltm_data, f, indent=2)
                
                # print(f"[{self._id}] Updated current budget in LTM")
                return True
            except Exception as e:
                # print(f"[{self._id}] Error updating current budget: {e}")
                return False
    
    # ==================== PROJECT MANAGEMENT METHODS ====================
    
    def create_project(self, project_name: str, budget_limit: float = 0.0, description: str = None) -> Optional[str]:
        """
        Create a new project with initial budget.
        
        Args:
            project_name: Name of the project
            budget_limit: Initial budget limit (optional)
            description: Project description (optional)
            
        Returns:
            Project ID on success, None on failure
        """
        import uuid
        try:
            # Generate project ID
            project_id = f"project_{uuid.uuid4().hex[:12]}"
            
            # Normalize project name
            project_name = project_name.strip()
            if not project_name:
                return None
            
            now = datetime.utcnow()
            
            if self.use_mongodb:
                try:
                    projects_collection = self.mongo_db["projects"]
                    
                    # Check if project name already exists (flexible matching)
                    # Normalize search name
                    normalized_search = project_name.lower().strip()
                    for suffix in [" project", "project", " proj", "proj"]:
                        if normalized_search.endswith(suffix):
                            normalized_search = normalized_search[:-len(suffix)].strip()
                    
                    # First try exact match
                    existing = projects_collection.find_one({
                        "project_name": project_name,
                        "agent_id": self._id
                    })
                    if existing:
                        return None  # Project name already exists
                    
                    # Try flexible matching
                    all_projects = projects_collection.find({"agent_id": self._id})
                    for proj in all_projects:
                        db_name = proj.get("project_name", "").lower().strip()
                        for suffix in [" project", "project", " proj", "proj"]:
                            if db_name.endswith(suffix):
                                db_name = db_name[:-len(suffix)].strip()
                        if db_name == normalized_search:
                            return None  # Similar project name already exists
                    
                    # Create new project
                    project_doc = {
                        "project_id": project_id,
                        "project_name": project_name,
                        "agent_id": self._id,
                        "budget_limit": float(budget_limit),
                        "spent": 0.0,
                        "history": [],
                        "description": description,
                        "status": "active",
                        "created_at": now,
                        "updated_at": now
                    }
                    
                    projects_collection.insert_one(project_doc)
                    
                    # Set as current project if no current project
                    current_project_collection = self.mongo_db["current_project"]
                    if current_project_collection.count_documents({"agent_id": self._id}) == 0:
                        current_project_collection.insert_one({
                            "agent_id": self._id,
                            "current_project_id": project_id,
                            "updated_at": now
                        })
                    
                    return project_id
                except Exception as e:
                    # print(f"[{self._id}] Error creating project in MongoDB: {e}")
                    return None
            else:
                # File-based
                if not os.path.exists(self.ltm_path):
                    self._initialize_ltm()
                
                with open(self.ltm_path, 'r') as f:
                    ltm_data = json.load(f)
                
                if "projects" not in ltm_data:
                    ltm_data["projects"] = {}
                
                # Check if project name already exists (flexible matching)
                normalized_search = project_name.lower().strip()
                for suffix in [" project", "project", " proj", "proj"]:
                    if normalized_search.endswith(suffix):
                        normalized_search = normalized_search[:-len(suffix)].strip()
                
                # First try exact match
                for pid, pdata in ltm_data["projects"].items():
                    if isinstance(pdata, dict) and pdata.get("project_name") == project_name:
                        return None  # Project name already exists
                
                # Try flexible matching
                for pid, pdata in ltm_data["projects"].items():
                    if isinstance(pdata, dict):
                        db_name = pdata.get("project_name", "").lower().strip()
                        for suffix in [" project", "project", " proj", "proj"]:
                            if db_name.endswith(suffix):
                                db_name = db_name[:-len(suffix)].strip()
                        if db_name == normalized_search:
                            return None  # Similar project name already exists
                
                # Create new project
                ltm_data["projects"][project_id] = {
                    "project_name": project_name,
                    "budget_limit": float(budget_limit),
                    "spent": 0.0,
                    "history": [],
                    "description": description,
                    "status": "active",
                    "created_at": now.isoformat() + "Z",
                    "last_updated": now.isoformat() + "Z"
                }
                
                # Set as current if no current project
                if not ltm_data.get("current_project"):
                    ltm_data["current_project"] = project_id
                
                with open(self.ltm_path, 'w') as f:
                    json.dump(ltm_data, f, indent=2)
                
                return project_id
        except Exception as e:
            # print(f"[{self._id}] Error creating project: {e}")
            return None
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects with their basic information.
        
        Returns:
            List of project dictionaries
        """
        try:
            if self.use_mongodb:
                projects_collection = self.mongo_db["projects"]
                current_project_collection = self.mongo_db["current_project"]
                
                # Get current project
                current_result = current_project_collection.find_one({"agent_id": self._id})
                current_project_id = current_result.get("current_project_id") if current_result else None
                
                # Get all projects
                projects = list(projects_collection.find({"agent_id": self._id}).sort("created_at", -1))
                
                result = []
                for proj in projects:
                    budget_limit = proj.get("budget_limit", 0.0)
                    spent = proj.get("spent", 0.0)
                    remaining = budget_limit - spent
                    # Normalize history to new format
                    history = proj.get("history", [])
                    history = self._normalize_history(history)
                    
                    result.append({
                        "project_id": proj.get("project_id"),
                        "project_name": proj.get("project_name"),
                        "budget_limit": budget_limit,
                        "spent": spent,
                        "remaining": remaining,
                        "history": history,
                        "description": proj.get("description"),
                        "status": proj.get("status", "active"),
                        "is_current": (proj.get("project_id") == current_project_id),
                        "created_at": proj.get("created_at").isoformat() if proj.get("created_at") else None,
                        "last_updated": proj.get("updated_at").isoformat() if proj.get("updated_at") else None
                    })
                
                return result
            else:
                # File-based
                if not os.path.exists(self.ltm_path):
                    return []
                
                with open(self.ltm_path, 'r') as f:
                    ltm_data = json.load(f)
                
                projects = ltm_data.get("projects", {})
                current_project_id = ltm_data.get("current_project")
                
                result = []
                for project_id, proj_data in projects.items():
                    if not isinstance(proj_data, dict):
                        continue
                    
                    budget_limit = proj_data.get("budget_limit", 0.0)
                    spent = proj_data.get("spent", 0.0)
                    remaining = budget_limit - spent
                    
                    result.append({
                        "project_id": project_id,
                        "project_name": proj_data.get("project_name", project_id),
                        "budget_limit": budget_limit,
                        "spent": spent,
                        "remaining": remaining,
                        "description": proj_data.get("description"),
                        "status": proj_data.get("status", "active"),
                        "is_current": (project_id == current_project_id),
                        "created_at": proj_data.get("created_at"),
                        "last_updated": proj_data.get("last_updated")
                    })
                
                return result
        except Exception as e:
            # print(f"[{self._id}] Error listing projects: {e}")
            return []
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project details by project_id.
        
        Args:
            project_id: Project ID to retrieve
            
        Returns:
            Project dictionary or None if not found
        """
        try:
            if self.use_mongodb:
                projects_collection = self.mongo_db["projects"]
                result = projects_collection.find_one({"project_id": project_id, "agent_id": self._id})
                if result:
                    budget_limit = result.get("budget_limit", 0.0)
                    spent = result.get("spent", 0.0)
                    # Normalize history to new format
                    history = result.get("history", [])
                    history = self._normalize_history(history)
                    
                    return {
                        "project_id": result.get("project_id"),
                        "project_name": result.get("project_name"),
                        "budget_limit": budget_limit,
                        "spent": spent,
                        "remaining": budget_limit - spent,
                        "history": history,
                        "description": result.get("description"),
                        "status": result.get("status", "active"),
                        "created_at": result.get("created_at").isoformat() if result.get("created_at") else None,
                        "last_updated": result.get("updated_at").isoformat() if result.get("updated_at") else None
                    }
                return None
            else:
                # File-based
                if not os.path.exists(self.ltm_path):
                    return None
                
                with open(self.ltm_path, 'r') as f:
                    ltm_data = json.load(f)
                
                projects = ltm_data.get("projects", {})
                if project_id in projects:
                    proj_data = projects[project_id]
                    if not isinstance(proj_data, dict):
                        return None
                    
                    budget_limit = proj_data.get("budget_limit", 0.0)
                    spent = proj_data.get("spent", 0.0)
                    return {
                        "project_id": project_id,
                        "project_name": proj_data.get("project_name", project_id),
                        "budget_limit": budget_limit,
                        "spent": spent,
                        "remaining": budget_limit - spent,
                        "history": proj_data.get("history", []),
                        "description": proj_data.get("description"),
                        "status": proj_data.get("status", "active"),
                        "created_at": proj_data.get("created_at"),
                        "last_updated": proj_data.get("last_updated")
                    }
                return None
        except Exception as e:
            # print(f"[{self._id}] Error getting project: {e}")
            return None
    
    def find_project_by_name(self, project_name: str) -> Optional[str]:
        """
        Find project ID by project name (flexible matching).
        
        Args:
            project_name: Name of the project to find (can include "Project" suffix)
            
        Returns:
            Project ID if found, None otherwise
        """
        try:
            project_name = project_name.strip()
            if not project_name:
                return None
            
            # Normalize the search name: remove "Project" suffix, case-insensitive
            normalized_search = project_name.lower().strip()
            # Remove common suffixes
            for suffix in [" project", "project", " proj", "proj", " development", "development"]:
                if normalized_search.endswith(suffix):
                    normalized_search = normalized_search[:-len(suffix)].strip()
            
            if self.use_mongodb:
                projects_collection = self.mongo_db["projects"]
                # First try exact match (case-insensitive)
                result = projects_collection.find_one({
                    "project_name": {"$regex": f"^{project_name}$", "$options": "i"},
                    "agent_id": self._id
                })
                if result:
                    return result.get("project_id")
                
                # Try partial match - search name contained in DB name or vice versa
                all_projects = projects_collection.find({"agent_id": self._id})
                best_match = None
                best_score = 0
                
                for proj in all_projects:
                    db_name = proj.get("project_name", "").lower().strip()
                    db_name_normalized = db_name
                    # Remove "Project" suffix from DB name too
                    for suffix in [" project", "project", " proj", "proj", " development", "development"]:
                        if db_name_normalized.endswith(suffix):
                            db_name_normalized = db_name_normalized[:-len(suffix)].strip()
                    
                    # Exact normalized match (highest priority)
                    if db_name_normalized == normalized_search:
                        return proj.get("project_id")
                    
                    # Partial match: search name is contained in DB name or vice versa
                    if normalized_search in db_name_normalized or db_name_normalized in normalized_search:
                        # Score: longer match is better
                        match_length = min(len(normalized_search), len(db_name_normalized))
                        if match_length > best_score:
                            best_score = match_length
                            best_match = proj.get("project_id")
                
                if best_match:
                    return best_match
                
                return None
            else:
                # File-based
                if not os.path.exists(self.ltm_path):
                    return None
                
                with open(self.ltm_path, 'r') as f:
                    ltm_data = json.load(f)
                
                projects = ltm_data.get("projects", {})
                # First try exact match (case-insensitive)
                for project_id, proj_data in projects.items():
                    if isinstance(proj_data, dict):
                        db_name = proj_data.get("project_name", "")
                        if db_name.lower() == project_name.lower():
                            return project_id
                
                # Try partial match - search name contained in DB name or vice versa
                best_match = None
                best_score = 0
                
                for project_id, proj_data in projects.items():
                    if isinstance(proj_data, dict):
                        db_name = proj_data.get("project_name", "").lower().strip()
                        db_name_normalized = db_name
                        # Remove "Project" suffix from DB name
                        for suffix in [" project", "project", " proj", "proj", " development", "development"]:
                            if db_name_normalized.endswith(suffix):
                                db_name_normalized = db_name_normalized[:-len(suffix)].strip()
                        
                        # Exact normalized match (highest priority)
                        if db_name_normalized == normalized_search:
                            return project_id
                        
                        # Partial match: search name is contained in DB name or vice versa
                        if normalized_search in db_name_normalized or db_name_normalized in normalized_search:
                            # Score: longer match is better
                            match_length = min(len(normalized_search), len(db_name_normalized))
                            if match_length > best_score:
                                best_score = match_length
                                best_match = project_id
                
                if best_match:
                    return best_match
                
                return None
        except Exception as e:
            # print(f"[{self._id}] Error finding project by name: {e}")
            return None
    
    def set_current_project(self, project_id: str) -> bool:
        """
        Set the current active project.
        
        Args:
            project_id: Project ID to set as current
            
        Returns:
            True on success, False otherwise
        """
        try:
            # Verify project exists
            if not self.get_project(project_id):
                return False
            
            if self.use_mongodb:
                current_project_collection = self.mongo_db["current_project"]
                current_project_collection.update_one(
                    {"agent_id": self._id},
                    {
                        "$set": {
                            "agent_id": self._id,
                            "current_project_id": project_id,
                            "updated_at": datetime.utcnow()
                        }
                    },
                    upsert=True
                )
                return True
            else:
                # File-based
                if not os.path.exists(self.ltm_path):
                    self._initialize_ltm()
                
                with open(self.ltm_path, 'r') as f:
                    ltm_data = json.load(f)
                
                ltm_data["current_project"] = project_id
                
                with open(self.ltm_path, 'w') as f:
                    json.dump(ltm_data, f, indent=2)
                
                return True
        except Exception as e:
            # print(f"[{self._id}] Error setting current project: {e}")
            return False
    
    def get_current_project_id(self) -> Optional[str]:
        """
        Get the current active project ID.
        
        Returns:
            Project ID or None if no project is set
        """
        try:
            if self.use_mongodb:
                current_project_collection = self.mongo_db["current_project"]
                result = current_project_collection.find_one({"agent_id": self._id})
                if result:
                    return result.get("current_project_id")
                return None
            else:
                # File-based
                if not os.path.exists(self.ltm_path):
                    return None
                
                with open(self.ltm_path, 'r') as f:
                    ltm_data = json.load(f)
                
                return ltm_data.get("current_project")
        except Exception as e:
            # print(f"[{self._id}] Error getting current project ID: {e}")
            return None
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project (cannot delete current project).
        
        Args:
            project_id: Project ID to delete
            
        Returns:
            True on success, False otherwise
        """
        try:
            current_project_id = self.get_current_project_id()
            if project_id == current_project_id:
                return False  # Cannot delete current project
            
            if self.use_mongodb:
                projects_collection = self.mongo_db["projects"]
                tasks_collection = self.mongo_db["tasks"]
                
                # Delete project
                result = projects_collection.delete_one({"project_id": project_id, "agent_id": self._id})
                if result.deleted_count > 0:
                    # Also delete related task cache entries
                    tasks_collection.delete_many({"project_id": project_id, "agent_id": self._id})
                    return True
                return False
            else:
                # File-based
                if not os.path.exists(self.ltm_path):
                    return False
                
                with open(self.ltm_path, 'r') as f:
                    ltm_data = json.load(f)
                
                projects = ltm_data.get("projects", {})
                if project_id in projects:
                    del projects[project_id]
                    ltm_data["projects"] = projects
                    
                    # Also clean up related task cache entries
                    tasks = ltm_data.get("tasks", {})
                    keys_to_remove = [k for k in tasks.keys() if k.startswith(f"{project_id}:")]
                    for key in keys_to_remove:
                        del tasks[key]
                    ltm_data["tasks"] = tasks
                    
                    with open(self.ltm_path, 'w') as f:
                        json.dump(ltm_data, f, indent=2)
                    
                    return True
                return False
        except Exception as e:
            # print(f"[{self._id}] Error deleting project: {e}")
            return False
    
    def merge_with_context(self, extracted_params: Dict[str, Any], project_id: str = None) -> Dict[str, Any]:
        """
        Merge extracted parameters with current budget context from LTM.
        
        Args:
            extracted_params: Parameters extracted from query
            
        Returns:
            Merged parameters with context filled in
        """
        current = self.get_current_budget(project_id=project_id)
        
        # Start with extracted params
        merged = {
            "budget_limit": extracted_params.get("budget_limit"),
            "spent": extracted_params.get("spent"),
            "history": extracted_params.get("history")
        }
        
        # Fill in missing values from context
        if current:
            if merged["budget_limit"] is None:
                merged["budget_limit"] = current.get("budget_limit")
            if merged["spent"] is None:
                merged["spent"] = current.get("spent")
            if merged["history"] is None:
                merged["history"] = current.get("history", [])
        
        # Ensure we have valid numbers (default to 0 if still None)
        merged["budget_limit"] = merged["budget_limit"] if merged["budget_limit"] is not None else 0.0
        merged["spent"] = merged["spent"] if merged["spent"] is not None else 0.0
        merged["history"] = merged["history"] if merged["history"] is not None else []
        
        return merged

    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a budget analysis task using rule-based logic.
        
        Business Logic:
        1. Handle updates if present
        2. Merge with context from LTM
        3. Calculate remaining budget
        4. Calculate spending rate from history
        5. Predict overspend risk
        6. Detect anomalies in spending history
        7. Generate recommendations
        8. Update current budget in LTM
        
        Args:
            task_data: Dictionary containing task parameters and optional update_info:
                - budget_limit: Total budget limit
                - spent: Amount already spent
                - history: Optional list of past spending amounts
                - update_info: Optional update information
                
        Returns:
            Dictionary containing analysis results
        """
        # Get project_id from task_data
        project_id = task_data.get("project_id")
        
        # Handle updates first
        update_info = task_data.get("update_info")
        if update_info and update_info.get("update_type"):
            # Apply update to current budget
            self.update_current_budget(
                update_type=update_info.get("update_type"),
                update_field=update_info.get("update_field"),
                update_value=update_info.get("update_value"),
                project_id=project_id
            )
        
        # Merge extracted parameters with context
        # IMPORTANT: If an update was applied, we need to get the UPDATED context
        # and ignore extracted values for the updated field
        # Parameters are nested in task_data["parameters"]
        params = task_data.get("parameters", {})
        extracted = {
            "budget_limit": params.get("budget_limit"),
            "spent": params.get("spent"),
            "history": params.get("history")
        }
        
        # If an update was applied, clear the extracted value for that field
        # so merge_with_context will use the updated context value instead
        if update_info and update_info.get("update_type"):
            update_field = update_info.get("update_field")
            if update_field == "spent":
                # Don't use extracted spent if it was part of an update
                # The updated context has the correct value
                extracted["spent"] = None
            elif update_field == "budget_limit":
                extracted["budget_limit"] = None
            elif update_field == "history":
                extracted["history"] = None
        
        merged_params = self.merge_with_context(extracted, project_id=project_id)
        
        # CRITICAL FIX: After update, get the ACTUAL updated state from the project
        # This ensures we use the cumulative spent and full history, not stale merged values
        if update_info and update_info.get("update_type"):
            # Get the fresh state from the project (after update was applied)
            current_state = self.get_current_budget(project_id=project_id)
            if current_state:
                # Override merged_params with actual updated values from project
                # This ensures cumulative spent and complete history are used
                merged_params["spent"] = current_state.get("spent", merged_params["spent"])
                merged_params["history"] = current_state.get("history", merged_params["history"])
                # Preserve budget_limit from merged if it was provided, otherwise use current
                if merged_params.get("budget_limit") is None:
                    merged_params["budget_limit"] = current_state.get("budget_limit", merged_params.get("budget_limit", 0.0))
        
        # Check LTM cache first (using merged params)
        if self.enable_ltm_cache:
            ltm_key = self._generate_ltm_key(merged_params, project_id=project_id)
            cached_result = self.read_from_ltm(ltm_key, project_id=project_id)
            if cached_result:
                # print(f"[{self._id}] Using cached result from LTM")
                # If update was applied, don't overwrite it - get the actual updated state
                if update_info and update_info.get("update_type"):
                    # Update was already applied, get current state for accurate results
                    current_state = self.get_current_budget(project_id=project_id)
                    if current_state:
                        # Update cached result with actual current values
                        cached_result["remaining"] = current_state.get("budget_limit", 0) - current_state.get("spent", 0)
                        # Recalculate spending rate from actual history
                        actual_history = current_state.get("history", [])
                        if actual_history and len(actual_history) > 0:
                            try:
                                # Normalize and extract amounts
                                normalized_history = self._normalize_history(actual_history)
                                history_amounts = self._extract_amounts_from_history(normalized_history)
                                if history_amounts:
                                    cached_result["spending_rate"] = round(statistics.mean(history_amounts), 2)
                            except:
                                pass
                else:
                    # No update, safe to update with merged params
                    self.update_current_budget(
                        budget_limit=merged_params["budget_limit"],
                        spent=merged_params["spent"],
                        history=merged_params["history"],
                        project_id=project_id
                    )
                # Add query-specific fields to cached result
                cached_result["_intent"] = task_data.get("intent", "check")
                cached_result["_user_query"] = task_data.get("user_query", "")
                return cached_result
        
        # Extract parameters (now using merged values)
        budget_limit = float(merged_params.get("budget_limit", 0))
        spent = float(merged_params.get("spent", 0))
        history = merged_params.get("history", [])
        
        if budget_limit < 0 or spent < 0:
            raise ValueError("Budget limit and spent amount must be non-negative")
        
        # 1. Calculate remaining budget
        remaining = budget_limit - spent
        
        # 2. Calculate spending rate (if history provided)
        spending_rate = None
        if history and len(history) > 0:
            try:
                # Normalize history and extract amounts
                normalized_history = self._normalize_history(history)
                history_amounts = self._extract_amounts_from_history(normalized_history)
                if history_amounts:
                    spending_rate = statistics.mean(history_amounts)
            except (ValueError, TypeError):
                spending_rate = None
        
        # 3. Predict overspend risk
        predicted_spending = spent
        overshoot_risk = False
        
        if spending_rate is not None and spending_rate > 0:
            # Simple prediction: assume current spending rate continues
            # Estimate remaining days/periods based on history length
            normalized_history = self._normalize_history(history)
            periods_remaining = max(1, len(normalized_history))  # Rough estimate
            predicted_spending = spent + (spending_rate * periods_remaining)
            
            if predicted_spending > budget_limit:
                overshoot_risk = True
        
        # 4. Anomaly detection
        anomalies = []
        if history and len(history) > 2:
            try:
                history_floats = [float(h) for h in history]
                mean = statistics.mean(history_floats)
                if len(history_floats) > 1:
                    std = statistics.stdev(history_floats)
                    threshold = mean + (self.anomaly_threshold * std)
                    
                    for idx, value in enumerate(history_floats):
                        if value > threshold:
                            anomalies.append({
                                "index": idx,
                                "value": value,
                                "threshold": threshold,
                                "deviation": value - mean
                            })
            except (ValueError, TypeError, statistics.StatisticsError):
                pass
        
        # 5. Generate recommendations
        recommendations = self._generate_recommendations(
            remaining, overshoot_risk, predicted_spending, budget_limit, spending_rate
        )
        
        # Build results dictionary
        intent = task_data.get("intent", "check")
        user_query = task_data.get("user_query", "")
        results = {
            "remaining": round(remaining, 2),
            "spending_rate": round(spending_rate, 2) if spending_rate is not None else None,
            "overshoot_risk": overshoot_risk,
            "predicted_spending": round(predicted_spending, 2),
            "anomalies": anomalies,
            "recommendations": recommendations,
            "_intent": intent,  # Store intent for response formatting
            "_user_query": user_query  # Store original query for natural language generation
        }
        
        # Don't store _user_query in LTM (it's query-specific)
        ltm_results = {k: v for k, v in results.items() if not k.startswith("_")}
        
        # Store in LTM for future use (without query-specific fields)
        if self.enable_ltm_cache:
            ltm_key = self._generate_ltm_key(merged_params, project_id=project_id)
            self.write_to_ltm(ltm_key, ltm_results, project_id=project_id)
            
            # Update current budget context
            # IMPORTANT: If an update was applied, don't overwrite it
            # Get the current state which has the update already applied
            if update_info and update_info.get("update_type"):
                # Update was already applied above, don't overwrite
                # The project state is already correct with cumulative spent and history
                pass
            else:
                # No update was applied, safe to update with calculated values
                # But get current state first to preserve existing history
                current_state = self.get_current_budget(project_id=project_id)
                if current_state:
                    # Preserve existing history, only update if we have new values
                    final_history = history if history else current_state.get("history", [])
                    final_spent = spent if spent != current_state.get("spent", 0) else current_state.get("spent", 0)
                    final_budget_limit = budget_limit if budget_limit != current_state.get("budget_limit", 0) else current_state.get("budget_limit", 0)
                else:
                    final_history = history
                    final_spent = spent
                    final_budget_limit = budget_limit
                
                # Only update if we have values to update
                self.update_current_budget(
                    budget_limit=final_budget_limit,
                    spent=final_spent,
                    history=final_history,
                    project_id=project_id
                )
        
        return results

    def _generate_recommendations(self, remaining: float, overshoot_risk: bool,
                                 predicted_spending: float, budget_limit: float,
                                 spending_rate: Optional[float]) -> List[str]:
        """
        Generate budget management recommendations based on analysis.
        
        Args:
            remaining: Remaining budget
            overshoot_risk: Whether overspend risk is detected
            predicted_spending: Predicted total spending
            budget_limit: Total budget limit
            spending_rate: Average spending rate
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Calculate remaining percentage
        remaining_percentage = (remaining / budget_limit * 100) if budget_limit > 0 else 0
        
        if overshoot_risk:
            recommendations.append(
                f"⚠️ HIGH RISK: Predicted spending ({predicted_spending:.2f}) exceeds budget limit ({budget_limit:.2f})"
            )
            
            if spending_rate:
                reduction_needed = (predicted_spending - budget_limit) / spending_rate
                recommendations.append(
                    f"Reduce upcoming spending by {self.config.get('recommendation_reduction_percentage_min', 10)}-{self.config.get('recommendation_reduction_percentage_max', 20)}%"
                )
                recommendations.append(
                    f"Consider pausing low-priority expenses for approximately {int(reduction_needed)} periods"
                )
            
            recommendations.append("Reallocate budget from non-essential categories")
            recommendations.append("Review and prioritize critical expenses only")
        
        elif remaining_percentage < 20:
            recommendations.append(
                f"⚠️ WARNING: Only {remaining_percentage:.1f}% of budget remaining"
            )
            recommendations.append("Monitor spending closely and avoid unnecessary expenses")
            recommendations.append("Consider reallocating budget from completed or low-priority items")
        
        elif remaining_percentage < 50:
            recommendations.append(
                f"Moderate budget remaining ({remaining_percentage:.1f}%)"
            )
            recommendations.append("Continue monitoring spending patterns")
            recommendations.append("Plan upcoming expenses to stay within budget")
        
        else:
            recommendations.append(
                f"✅ Good budget health: {remaining_percentage:.1f}% remaining"
            )
            recommendations.append("Continue current spending patterns")
        
        if not recommendations:
            recommendations.append("No specific recommendations at this time")
        
        return recommendations

    def handle_incoming_message(self, json_message: str):
        """Override to handle full task object with intent and update_info."""
        try:
            message = json.loads(json_message)
            msg_type = message.get("type")
            
            if msg_type == "task_assignment":
                task = message.get("task", {})
                task_data = {
                    "parameters": task.get("parameters", {}),
                    "intent": task.get("intent", "check"),
                    "update_info": task.get("update_info"),
                    "user_query": message.get("user_query", "")  # Store original query
                }
                self._current_task_id = message.get("message_id")
                # print(f"[{self._id}] received task: {task.get('name', 'analyze_budget')} (intent: {task_data.get('intent')})")
                self._execute_task(task_data, self._current_task_id)
            
        except json.JSONDecodeError as e:
            # print(f"[{self._id}] ERROR decoding message: {e}")
            pass
    
    def generate_natural_language_response(self, results: Dict[str, Any], intent: str, user_query: str = "") -> str:
        """
        Generate a natural, paragraph-style conversational response using Google Gemini.
        
        Args:
            results: Analysis results dictionary
            intent: User intent (check, predict, recommend, etc.)
            user_query: Original user query for context
            
        Returns:
            Natural language paragraph response
        """
        # Prepare context for Gemini
        remaining = results.get("remaining", 0)
        spending_rate = results.get("spending_rate")
        overshoot_risk = results.get("overshoot_risk", False)
        predicted_spending = results.get("predicted_spending", 0)
        anomalies = results.get("anomalies", [])
        recommendations = results.get("recommendations", [])
        
        # Build context string for Gemini
        context = f"""Budget Analysis Results:
- Remaining budget: ${remaining:,.2f}
- Spending rate: ${spending_rate:,.2f} per period (if available)
- Overshoot risk: {overshoot_risk}
- Predicted total spending: ${predicted_spending:,.2f}
- Anomalies detected: {len(anomalies)}
- Recommendations: {', '.join(recommendations[:3]) if recommendations else 'None'}
"""
        
        system_prompt = """You are a helpful budget advisor assistant. Your role is to provide natural, conversational responses about budget status in a friendly, human-like manner.

Guidelines:
- Write in paragraph form, like a real person talking (not bullet points or lists)
- Be conversational and friendly, like ChatGPT
- Answer the user's question directly and naturally
- Use the analysis results to provide accurate information
- If there are warnings or risks, explain them clearly but helpfully
- Make it feel like a real conversation, not a system report
- Keep responses concise but informative (2-4 sentences typically)
- Use natural transitions and flow

Examples:
- For "How much remaining?": "You currently have $8,000 remaining from your $50,000 budget. That's about 16% left, so you're doing well but should keep an eye on spending."
- For "Will we exceed budget?": "Based on your current spending patterns, you're predicted to spend $68,000 total, which would exceed your $50,000 budget. I'd recommend reducing upcoming expenses by about 10-20% to stay on track."
- For updates: "Got it! I've updated your spending. You now have $7,500 remaining from your budget. Your average spending is $500 per period, which looks manageable."

Write ONLY the response paragraph, nothing else."""

        user_prompt = f"""User asked: "{user_query}"
Intent: {intent}

{context}

Provide a natural, conversational response to the user's question:"""

        try:
            # Try to use Gemini to generate natural response
            try:
                import google.generativeai as genai
                api_key = os.getenv("GEMINI_API_KEY")
                if api_key:
                    genai.configure(api_key=api_key)
                    # Use gemini-2.5-flash (fast, latest, and supports generateContent)
                    model = genai.GenerativeModel('models/gemini-2.5-flash')
                    
                    # Combine system prompt and user prompt
                    full_prompt = f"{system_prompt}\n\n{user_prompt}"
                    
                    response = model.generate_content(
                        full_prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.7,  # Slightly higher for more natural responses
                            max_output_tokens=200
                        )
                    )
                    return response.text.strip()
            except Exception:
                pass  # Fallback to template-based response
        except:
            pass
        
        # Fallback to template-based response if Gemini fails
        return self.format_conversational_response(results, intent)
    
    def format_conversational_response(self, results: Dict[str, Any], intent: str = "check") -> str:
        """
        Format analysis results as a natural language conversational response.
        
        Args:
            results: Analysis results dictionary
            intent: User intent (check, predict, recommend, etc.)
            
        Returns:
            Natural language response string
        """
        remaining = results.get("remaining", 0)
        spending_rate = results.get("spending_rate")
        overshoot_risk = results.get("overshoot_risk", False)
        predicted_spending = results.get("predicted_spending", 0)
        anomalies = results.get("anomalies", [])
        recommendations = results.get("recommendations", [])
        
        response_parts = []
        
        if intent == "check" or intent == "question":
            # Natural language check response
            response_parts.append(f"📊 **Your Budget Status:**\n")
            
            if remaining > 0:
                remaining_pct = (remaining / (remaining + results.get("spent", 0)) * 100) if (remaining + results.get("spent", 0)) > 0 else 0
                response_parts.append(f"You have **${remaining:,.2f}** remaining from your budget ({remaining_pct:.1f}% left).")
            else:
                response_parts.append(f"You have **no budget remaining**. You've used your entire budget.")
            
            if spending_rate:
                response_parts.append(f"\nYour average spending rate is **${spending_rate:,.2f}** per period.")
            
            if overshoot_risk:
                response_parts.append(f"\n⚠️ **Warning:** Based on current spending patterns, you're predicted to spend **${predicted_spending:,.2f}** total, which exceeds your budget limit!")
            else:
                if remaining > 0:
                    response_parts.append(f"\n✅ Your budget is on track and you're staying within limits.")
        
        elif intent == "predict":
            # Natural language prediction response
            if overshoot_risk:
                response_parts.append(f"⚠️ **Overspending Risk Detected!**\n")
                response_parts.append(f"Based on your current spending patterns, you're predicted to spend **${predicted_spending:,.2f}** total.")
                response_parts.append(f"This **exceeds your budget limit**, so you're at risk of overspending.")
            else:
                response_parts.append(f"✅ **No Overspending Risk**\n")
                response_parts.append(f"Based on your current spending patterns, you're predicted to spend **${predicted_spending:,.2f}** total.")
                response_parts.append(f"You're **within your budget limits** and on track.")
        
        elif intent == "analyze":
            # Natural language analysis response
            response_parts.append(f"📈 **Spending Analysis:**\n")
            response_parts.append(f"You have **${remaining:,.2f}** remaining in your budget.")
            
            if spending_rate:
                response_parts.append(f"Your average spending is **${spending_rate:,.2f}** per period.")
            
            if anomalies:
                response_parts.append(f"\n🔍 **Anomalies Detected:**")
                response_parts.append(f"I found {len(anomalies)} unusual spending period(s):")
                for anomaly in anomalies:
                    response_parts.append(f"   • Period {anomaly['index']+1}: You spent **${anomaly['value']:,.2f}**, which is **${anomaly['deviation']:,.2f}** above your average.")
            else:
                response_parts.append(f"\n✅ No unusual spending patterns detected. Your expenses are consistent.")
        
        elif intent == "recommend":
            # Natural language recommendations
            response_parts.append(f"💡 **Recommendations:**\n")
            for i, rec in enumerate(recommendations, 1):
                # Remove emoji from recommendation if present for cleaner output
                clean_rec = rec.replace("⚠️", "").replace("✅", "").strip()
                response_parts.append(f"{i}. {clean_rec}")
        
        elif intent == "report":
            # Natural language report
            response_parts.append(f"📋 **Budget Report:**\n")
            response_parts.append(f"**Remaining Budget:** ${remaining:,.2f}")
            if spending_rate:
                response_parts.append(f"**Average Spending Rate:** ${spending_rate:,.2f} per period")
            risk_status = "Yes - You may exceed your budget" if overshoot_risk else "No - You're on track"
            response_parts.append(f"**Overshoot Risk:** {risk_status}")
            response_parts.append(f"**Predicted Total Spending:** ${predicted_spending:,.2f}")
            if anomalies:
                response_parts.append(f"**Anomalies:** {len(anomalies)} unusual spending period(s) detected")
        
        elif intent == "update":
            # Natural language update confirmation
            response_parts.append(f"✅ **Budget Updated Successfully!**\n")
            response_parts.append(f"Your current budget status:")
            response_parts.append(f"   • Remaining: **${remaining:,.2f}**")
            if spending_rate:
                response_parts.append(f"   • Average spending: **${spending_rate:,.2f}** per period")
        
        # Always add recommendations if available and not already shown
        if recommendations and intent not in ["recommend", "update"]:
            response_parts.append(f"\n💡 **Suggestions:**")
            for rec in recommendations[:3]:  # Show top 3
                clean_rec = rec.replace("⚠️", "").replace("✅", "").strip()
                response_parts.append(f"   • {clean_rec}")
        
        return "\n".join(response_parts)
    
    def send_message(self, recipient: str, message_obj: Dict[str, Any], show_json: bool = False):
        """
        Sends the final JSON message object through the communication layer.
        
        For standalone execution, this prints natural language response to console.
        Can be easily replaced with HTTP POST or other communication methods.
        
        Args:
            recipient: Recipient agent ID
            message_obj: Message dictionary to send
            show_json: If True, also displays JSON (default: False for cleaner output)
        """
        from communication.protocol import format_message
        
        # Format conversational response if results are present
        results = message_obj.get("results", {})
        if results and "error" not in results:
            # Try to get intent and user query from results
            intent = results.get("_intent", "check")
            user_query = results.get("_user_query", "")
            
            # Generate natural language paragraph response using Gemini
            try:
                conversational = self.generate_natural_language_response(results, intent, user_query)
            except Exception as e:
                # Fallback to template-based response
                conversational = self.format_conversational_response(results, intent)
            
            # print(f"\n{'='*70}")
            print(conversational)
            # print(f"{'='*70}\n")
            
            # Only show JSON if explicitly requested (for debugging)
            if show_json:
                print(f"📄 **Technical Details (JSON):**")
                print(f"{'='*70}")
                formatted_message = format_message(message_obj)
                print(formatted_message)
                print(f"{'='*70}\n")
        else:
            # Error case - show both
            print(f"\n{'='*70}")
            print(f"❌ **Error Response:**")
            print(f"{'='*70}")
            if "error" in results:
                print(f"Error: {results.get('error', 'Unknown error')}")
            formatted_message = format_message(message_obj)
            print(formatted_message)
            print(f"{'='*70}\n")
        
        # Return the message object for programmatic use
        return message_obj
    
    def close(self):
        """Close MongoDB connection if it exists."""
        if self.mongo_client:
            try:
                self.mongo_client.close()
                # print(f"[{self._id}] Closed MongoDB connection")
            except Exception:
                pass

