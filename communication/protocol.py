"""
Communication protocol utilities for message validation and handling.
"""

import json
from typing import Dict, Any, Optional
from .schemas import TaskAssignment, CompletionReport


def validate_task_assignment(message: Dict[str, Any]) -> bool:
    """
    Validates a task assignment message structure.
    
    Args:
        message: Dictionary containing the message data
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["message_id", "sender", "recipient", "type", "task"]
    
    if not all(field in message for field in required_fields):
        return False
    
    if message.get("type") != "task_assignment":
        return False
    
    task = message.get("task", {})
    if "name" not in task or "parameters" not in task:
        return False
    
    return True


def validate_completion_report(message: Dict[str, Any]) -> bool:
    """
    Validates a completion report message structure.
    
    Args:
        message: Dictionary containing the message data
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = [
        "message_id", "sender", "recipient", "type",
        "related_message_id", "status", "results"
    ]
    
    if not all(field in message for field in required_fields):
        return False
    
    if message.get("type") != "completion_report":
        return False
    
    if message.get("status") not in ["SUCCESS", "FAILURE"]:
        return False
    
    return True


def parse_message(json_string: str) -> Optional[Dict[str, Any]]:
    """
    Parses a JSON message string and validates its structure.
    
    Args:
        json_string: JSON string to parse
        
    Returns:
        Parsed message dictionary or None if invalid
    """
    try:
        message = json.loads(json_string)
        msg_type = message.get("type")
        
        if msg_type == "task_assignment":
            if validate_task_assignment(message):
                return message
        elif msg_type == "completion_report":
            if validate_completion_report(message):
                return message
        
        return None
    except json.JSONDecodeError:
        return None


def format_message(message_obj: Dict[str, Any], indent: int = 2) -> str:
    """
    Formats a message object as a pretty-printed JSON string.
    
    Args:
        message_obj: Message dictionary
        indent: JSON indentation level
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(message_obj, indent=indent)

