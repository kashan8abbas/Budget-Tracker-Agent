"""
Message schemas for Supervisor-Worker communication protocol.
Defines the structure of task assignments and completion reports.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TaskAssignment:
    """Schema for task assignment messages from Supervisor to Worker."""
    message_id: str
    sender: str
    recipient: str
    type: str = "task_assignment"
    task: Dict[str, Any] = None
    timestamp: str = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "type": self.type,
            "task": self.task,
            "timestamp": self.timestamp or datetime.utcnow().isoformat() + "Z"
        }


@dataclass
class CompletionReport:
    """Schema for completion report messages from Worker to Supervisor."""
    message_id: str
    sender: str
    recipient: str
    type: str = "completion_report"
    related_message_id: str = None
    status: str = None  # "SUCCESS" or "FAILURE"
    results: Dict[str, Any] = None
    timestamp: str = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "type": self.type,
            "related_message_id": self.related_message_id,
            "status": self.status,
            "results": self.results,
            "timestamp": self.timestamp or datetime.utcnow().isoformat() + "Z"
        }


@dataclass
class BudgetTaskParameters:
    """Schema for budget analysis task parameters."""
    budget_limit: float
    spent: float
    history: Optional[List[float]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BudgetTaskParameters':
        """Create from dictionary."""
        return cls(
            budget_limit=data.get("budget_limit", 0.0),
            spent=data.get("spent", 0.0),
            history=data.get("history", [])
        )


@dataclass
class BudgetAnalysisResults:
    """Schema for budget analysis results."""
    remaining: float
    spending_rate: Optional[float] = None
    overshoot_risk: bool = False
    predicted_spending: float = 0.0
    anomalies: List[Dict[str, Any]] = None
    recommendations: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "remaining": self.remaining,
            "spending_rate": self.spending_rate,
            "overshoot_risk": self.overshoot_risk,
            "predicted_spending": self.predicted_spending,
            "anomalies": self.anomalies or [],
            "recommendations": self.recommendations or []
        }

