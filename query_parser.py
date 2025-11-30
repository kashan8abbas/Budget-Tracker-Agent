"""
Natural Language Query Parser using Google Gemini

This module extracts budget parameters from user's natural language queries
and converts them into the structured JSON format expected by the agent.
"""

import json
import os
from typing import Dict, Any, Optional
import google.generativeai as genai


class QueryParser:
    """
    Parses natural language queries and extracts budget parameters using Google Gemini.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the query parser with Google Gemini API key.
        
        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
        """
        # Get API key from parameter, environment variable, or .env file
        if api_key:
            self.api_key = api_key
        elif os.getenv("GEMINI_API_KEY"):
            self.api_key = os.getenv("GEMINI_API_KEY")
        else:
            raise ValueError(
                "Gemini API key not found. Please provide via:\n"
                "1. --api-key argument\n"
                "2. GEMINI_API_KEY environment variable\n"
                "3. .env file with GEMINI_API_KEY"
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        # Use gemini-2.5-flash (fast, latest, and supports generateContent)
        # Alternative options: 'models/gemini-2.0-flash', 'models/gemini-pro-latest'
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    def detect_intent_and_extract(self, user_query: str) -> Dict[str, Any]:
        """
        Detect user intent and extract parameters from natural language query.
        
        Returns:
            Dictionary with:
            - intent: "check", "update", "predict", "recommend", "analyze", "report"
            - parameters: Extracted budget parameters
            - update_type: "add", "replace", "set" (if intent is update)
            - update_field: "spent", "budget_limit", "history" (if intent is update)
        """
        system_prompt = """You are an intelligent assistant for a budget tracking system.
Analyze the user's query and determine:
1. Intent: What does the user want to do?
2. Parameters: What budget information is mentioned?
3. Updates: Is the user updating spending/budget?
4. Project Name: Extract project name if mentioned (CRITICAL - be accurate)

Return JSON in this exact format:
{
  "intent": "check" | "update" | "predict" | "recommend" | "analyze" | "report" | "question",
  "project_name": <string or null>,
  "parameters": {
    "budget_limit": <number or null>,
    "spent": <number or null>,
    "history": [<numbers>] or null
  },
  "update_type": "add" | "replace" | "set" | null,
  "update_field": "spent" | "budget_limit" | "history" | null,
  "update_value": <number or array or null>,
  "spending_description": <string or null>
}

Intent meanings (CRITICAL - Classify accurately):
- "check": User wants to check budget status, remaining amount, current spending, financial position
  Examples: "Check my budget status", "How much remaining?", "What's our financial position?", "Kitna paisa bacha hai?", "Budget check karo", "Give me a quick budget view", "Is the budget safe?"
  
- "update": User is updating spending/budget (e.g., "I spent 5000", "Add 3000 to expenses")
  
- "predict": User wants prediction, forecast, future spending estimate, overspending risk
  Examples: "Will we exceed budget?", "Predict if we'll overshoot", "What will expenses look like in 10 days?", "Are we spending too fast?", "Is there risk of overspending?", "If we keep spending like this, what will happen?", "Check risk level", "Are we in danger zone?"
  
- "recommend": User wants recommendations, suggestions, advice on budget management
  Examples: "Suggest ways to reduce spending", "Recommend how to stay within budget", "How can we prevent overspending?", "Give financial recommendations", "Do we need to cut down expenses?"
  
- "analyze": User wants analysis, trends, history, anomalies, patterns, comparisons
  Examples: "Analyze past month's spending", "Find anomalies in expenses", "Compare current spend with past trends", "Show weekly spending patterns", "Is there unusual spend?", "Track our project expenses", "Financial health check kar do", "Expenses ka forecast batao"
  
- "report": User wants a report, summary, financial summary, spending analysis, budget forecast
  Examples: "Generate a budget report", "Give me a financial summary", "Create a spending analysis", "Prepare a budget forecast", "Summarize spending", "Abhi tak kahan tak budget use hua?"
  
- "question": General question about budget, alerts, warnings, red flags
  Examples: "Alert me if overspending risk is high", "Check if there are red flags", "Overspent ho rahe hain kya?", "Kharchay normal hain ya zyada?"

Special handling:
- Team/Department queries: "How is marketing team's budget?" → Extract "marketing team" as project_name, intent: "check"
- Multilingual queries: Handle Urdu/Hindi mix (e.g., "Budget check karo", "Kitna paisa bacha hai?")
- Lazy/casual queries: Handle short, informal queries (e.g., "Budget check", "Status?")

Update detection (ONLY for NEW spending, not current state):
- If user says "I spent X today", "Add X", "Spent X just now" → update_type: "add", update_field: "spent"
- If user says "Spending is now X", "Set spent to X" → update_type: "replace", update_field: "spent"
- If user says "Budget is X", "Limit is X" → update_type: "replace", update_field: "budget_limit"

Spending Description Extraction (CRITICAL):
- Extract description/reason for spending if mentioned in the query
- Examples:
  * "spent 50 on buying services" → spending_description: "buying services"
  * "spent 5000 on software licenses for Mobile App" → spending_description: "software licenses"
  * "I spent 3000 today on marketing" → spending_description: "marketing"
  * "Add 2000 for office supplies" → spending_description: "office supplies"
  * "Spent 1000" → spending_description: null (no description mentioned)
- Patterns to look for:
  * "spent X on [description]"
  * "spent X for [description]"
  * "spent X on buying [description]"
  * "Add X for [description]"
  * "Spent X today on [description]"
- If no description is mentioned, set spending_description to null
- The description should be a short, clear string describing what the money was spent on

IMPORTANT: Distinguish between statements and updates:
- "My budget is 50000 and I've spent 42000" → intent: "check", parameters: {budget_limit: 50000, spent: 42000}, NO update
- "I've spent 42000 so far" → intent: "check", parameters: {spent: 42000}, NO update
- "I spent 5000 today" → intent: "update", update_type: "add", update_field: "spent", update_value: 5000
- "Budget is 50000, spent 42000" → intent: "check", parameters: {budget_limit: 50000, spent: 42000}, NO update

Project Detection (CRITICAL - Extract accurately):
- Extract project name if mentioned in ANY form: "for Website Redesign project", "in Marketing Campaign", "for Project ABC", "our project Mobile App", "Mobile App project", "the Mobile App", "Mobile App Development"
- Common patterns: 
  * "for [Project Name]" or "for our [Project Name]"
  * "in [Project Name]" or "in our [Project Name]"
  * "[Project Name] project" or "project [Project Name]"
  * "our project [Project Name]" or "our [Project Name]"
  * "the [Project Name]" or "[Project Name]"
- Examples:
  * "Is our budget overrunning for our project Mobile App?" → project_name: "Mobile App"
  * "Check budget for Website Redesign" → project_name: "Website Redesign"
  * "How is Mobile App Development doing?" → project_name: "Mobile App Development"
- IMPORTANT: Extract the EXACT project name as mentioned, even if partial (e.g., "Mobile App" is valid even if full name is "Mobile App Development")
- If project name is mentioned, extract it and set "project_name" field
- If no project mentioned, set "project_name" to null

Rules:
- Extract ALL numbers mentioned (even in words: "fifty thousand" → 50000, "50k" → 50000, "50,000" → 50000)
- Use null for missing parameters (don't use 0 unless explicitly mentioned)
- If user is STATING current values (budget is X, spent Y), use intent "check" with parameters, NOT "update"
- Only use "update" intent when user is ADDING NEW spending or CHANGING values
- If intent is "update", always set update_type, update_field, and update_value
- Handle multilingual queries (English, Urdu/Hindi mix) - extract intent and parameters regardless of language
- Always extract project_name if mentioned in the query (including team/department names like "marketing team", "IT department")
- For queries without explicit numbers, use null for parameters - the system will use existing project data
- Short/casual queries are valid: "Budget check", "Status?", "Kitna bacha?" → intent: "check", parameters: null
- Questions about future/risk → intent: "predict"
- Questions about past/trends → intent: "analyze"
- Questions asking for advice → intent: "recommend"
- Questions asking for summary/report → intent: "report"
"""

        try:
            # Combine system prompt and user query for Gemini
            full_prompt = f"{system_prompt}\n\nUser Query: {user_query}\n\nReturn ONLY valid JSON, no additional text:"
            
            # Generate response using Gemini
            # Note: response_mime_type may not be supported by all models
            try:
                # Try with JSON mode (if supported by the model)
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        response_mime_type="application/json"
                    )
                )
            except (AttributeError, TypeError, Exception):
                # Fallback if response_mime_type not supported
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1
                    )
                )
            
            content = response.text.strip()
            
            # Extract JSON from markdown if present
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                if end != -1:
                    content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                if end != -1:
                    content = content[start:end].strip()
            
            result = json.loads(content)
            
            # Normalize parameters
            params = result.get("parameters", {})
            if params.get("budget_limit") is not None:
                params["budget_limit"] = float(params["budget_limit"])
            if params.get("spent") is not None:
                params["spent"] = float(params["spent"])
            if params.get("history") is not None and isinstance(params["history"], list):
                params["history"] = [float(h) for h in params["history"] if isinstance(h, (int, float, str))]
            else:
                params["history"] = None
            
            result["parameters"] = params
            
            # Normalize project_name (strip whitespace, handle null)
            project_name = result.get("project_name")
            if project_name:
                project_name = str(project_name).strip()
                if not project_name or project_name.lower() in ["null", "none", ""]:
                    project_name = None
            result["project_name"] = project_name
            
            # Normalize update_value
            if result.get("update_value") is not None:
                if isinstance(result["update_value"], (int, float)):
                    result["update_value"] = float(result["update_value"])
                elif isinstance(result["update_value"], list):
                    result["update_value"] = [float(v) for v in result["update_value"]]
            
            # Extract spending_description
            spending_description = result.get("spending_description")
            if spending_description:
                spending_description = str(spending_description).strip()
                if not spending_description or spending_description.lower() in ["null", "none", ""]:
                    spending_description = None
            result["spending_description"] = spending_description
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"Error parsing Gemini response: {e}")
            print(f"Response: {content}")
            # Fallback: assume check intent
            return {
                "intent": "check",
                "project_name": None,
                "parameters": {"budget_limit": None, "spent": None, "history": None},
                "update_type": None,
                "update_field": None,
                "update_value": None
            }
        except Exception as e:
            print(f"Error in intent detection: {e}")
            raise

    def extract_parameters(self, user_query: str) -> Dict[str, Any]:
        """
        Extract budget parameters from natural language query using Google Gemini.
        
        Args:
            user_query: Natural language query from user
            
        Returns:
            Dictionary with extracted parameters in the format:
            {
                "budget_limit": <number>,
                "spent": <number>,
                "history": [<numbers>]  # Optional
            }
        """
        system_prompt = """You are a parameter extraction assistant for a budget tracking system.
Your task is to extract budget-related parameters from user queries and return them as JSON.

Extract the following parameters:
1. budget_limit: The total budget limit (required)
2. spent: The amount already spent (required)
3. history: An array of past spending amounts (optional)

Return ONLY valid JSON in this exact format:
{
  "budget_limit": <number>,
  "spent": <number>,
  "history": [<number>, <number>, ...]  // Optional, can be empty array or omitted
}

Rules:
- Extract numbers even if written in words (e.g., "fifty thousand" → 50000)
- Handle variations: "50k" → 50000, "50,000" → 50000
- If history is mentioned, extract all spending amounts mentioned
- If history is not mentioned, use empty array []
- Return ONLY the JSON object, no additional text or explanation
- If any required parameter is missing, use 0 as default but try to extract from context
"""

        try:
            # Combine system prompt and user query for Gemini
            full_prompt = f"{system_prompt}\n\nUser Query: {user_query}\n\nReturn ONLY valid JSON, no additional text:"
            
            # Generate response using Gemini with JSON format
            # Note: response_mime_type may not be supported by all models
            try:
                # Try with JSON mode (if supported by the model)
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        response_mime_type="application/json"
                    )
                )
            except (AttributeError, TypeError, Exception):
                # Fallback if response_mime_type not supported
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1
                    )
                )
            
            # Extract JSON from response
            content = response.text.strip()
            
            # Try to extract JSON if response contains markdown code blocks
            if "```json" in content:
                # Extract JSON from markdown code block
                start = content.find("```json") + 7
                end = content.find("```", start)
                if end != -1:
                    content = content[start:end].strip()
            elif "```" in content:
                # Extract from generic code block
                start = content.find("```") + 3
                end = content.find("```", start)
                if end != -1:
                    content = content[start:end].strip()
            
            # Parse JSON
            try:
                extracted = json.loads(content)
                
                # Validate and normalize
                budget_limit = float(extracted.get("budget_limit", 0))
                spent = float(extracted.get("spent", 0))
                history = extracted.get("history", [])
                
                # Ensure history is a list of numbers
                if isinstance(history, list):
                    history = [float(h) for h in history if isinstance(h, (int, float, str))]
                else:
                    history = []
                
                # Validate required parameters
                if budget_limit <= 0:
                    raise ValueError("budget_limit must be greater than 0")
                if spent < 0:
                    raise ValueError("spent cannot be negative")
                
                return {
                    "budget_limit": budget_limit,
                    "spent": spent,
                    "history": history
                }
                
            except json.JSONDecodeError as e:
                print(f"Error parsing Gemini response as JSON: {e}")
                print(f"Response content: {content}")
                raise ValueError(f"Failed to parse extracted parameters. Please try rephrasing your query.")
            except ValueError as e:
                raise ValueError(f"Invalid extracted parameters: {e}")
                
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            raise
    
    def create_task_assignment(self, user_query: str, message_id: str = "user-query-1") -> Dict[str, Any]:
        """
        Create a complete task_assignment message from user query with intent detection.
        
        Args:
            user_query: Natural language query from user
            message_id: Unique message ID
            
        Returns:
            Complete task_assignment JSON message with intent and update info
        """
        from datetime import datetime
        
        # Detect intent and extract parameters
        intent_data = self.detect_intent_and_extract(user_query)
        
        # Create task assignment message
        task_assignment = {
            "message_id": message_id,
            "sender": "SupervisorAgent",
            "recipient": "BudgetTrackerAgent",
            "type": "task_assignment",
            "user_query": user_query,  # Store original query for natural language response
            "task": {
                "name": "analyze_budget",
                "priority": 1,
                "intent": intent_data.get("intent", "check"),
                "project_name": intent_data.get("project_name"),  # Extracted project name
                "parameters": intent_data.get("parameters", {}),
                "update_info": {
                    "update_type": intent_data.get("update_type"),
                    "update_field": intent_data.get("update_field"),
                    "update_value": intent_data.get("update_value")
                } if intent_data.get("update_type") else None,
                "spending_description": intent_data.get("spending_description")  # Pass description
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return task_assignment

