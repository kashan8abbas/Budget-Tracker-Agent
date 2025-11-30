"""
Pydantic models for API request/response validation
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class BudgetParameters(BaseModel):
    """Budget parameters for analysis"""
    budget_limit: Optional[float] = Field(None, description="Total budget limit")
    spent: Optional[float] = Field(None, description="Amount already spent")
    history: Optional[List[float]] = Field(None, description="List of past spending amounts")


class AnalyzeRequest(BaseModel):
    """Request model for budget analysis"""
    project_id: Optional[str] = Field(None, description="Project ID (optional, uses current project if not provided)")
    parameters: BudgetParameters = Field(..., description="Budget parameters")
    intent: Optional[str] = Field("check", description="User intent: check, predict, analyze, recommend, report")


class UpdateRequest(BaseModel):
    """Request model for budget update"""
    project_id: Optional[str] = Field(None, description="Project ID (optional, uses current project if not provided)")
    update_type: str = Field(..., description="Type of update: add, replace, set")
    update_field: str = Field(..., description="Field to update: spent, budget_limit, history")
    update_value: float | List[float] = Field(..., description="Value to update with")


class QueryRequest(BaseModel):
    """Request model for natural language query"""
    query: str = Field(..., description="Natural language query about budget")
    project_id: Optional[str] = Field(None, description="Project ID (optional, will be extracted from query or use current project)")


class BudgetAnalysisResponse(BaseModel):
    """Response model for budget analysis"""
    success: bool = Field(..., description="Whether the operation was successful")
    project_id: Optional[str] = Field(None, description="Project ID used for this analysis")
    project_name: Optional[str] = Field(None, description="Project name")
    remaining: float = Field(..., description="Remaining budget")
    spending_rate: Optional[float] = Field(None, description="Average spending rate per period")
    overshoot_risk: bool = Field(..., description="Whether there's a risk of exceeding budget")
    predicted_spending: float = Field(..., description="Predicted total spending")
    anomalies: List[dict] = Field(default_factory=list, description="Detected spending anomalies")
    recommendations: List[str] = Field(default_factory=list, description="Budget management recommendations")
    response: Optional[str] = Field(None, description="Natural language response")
    error: Optional[str] = Field(None, description="Error message if operation failed")


class CurrentBudgetResponse(BaseModel):
    """Response model for current budget"""
    success: bool = Field(..., description="Whether the operation was successful")
    project_id: Optional[str] = Field(None, description="Project ID")
    project_name: Optional[str] = Field(None, description="Project name")
    budget_limit: Optional[float] = Field(None, description="Current budget limit")
    spent: Optional[float] = Field(None, description="Current spent amount")
    remaining: Optional[float] = Field(None, description="Remaining budget")
    history: List[float] = Field(default_factory=list, description="Spending history")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    error: Optional[str] = Field(None, description="Error message if operation failed")


class UpdateResponse(BaseModel):
    """Response model for budget update"""
    success: bool = Field(..., description="Whether the update was successful")
    message: str = Field(..., description="Status message")
    budget: Optional[CurrentBudgetResponse] = Field(None, description="Updated budget state")
    error: Optional[str] = Field(None, description="Error message if operation failed")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    mongodb_connected: bool = Field(..., description="Whether MongoDB is connected")
    database: Optional[str] = Field(None, description="Database name")


# Project Management Models
class ProjectCreateRequest(BaseModel):
    """Request model for creating a project"""
    project_name: str = Field(..., description="Name of the project")
    budget_limit: Optional[float] = Field(0.0, description="Initial budget limit")
    description: Optional[str] = Field(None, description="Project description")


class ProjectUpdateRequest(BaseModel):
    """Request model for updating a project"""
    project_name: Optional[str] = Field(None, description="New project name")
    budget_limit: Optional[float] = Field(None, description="New budget limit")
    description: Optional[str] = Field(None, description="New description")
    status: Optional[str] = Field(None, description="Project status: active, completed, archived")


class ProjectResponse(BaseModel):
    """Response model for project"""
    success: bool = Field(..., description="Whether the operation was successful")
    project_id: str = Field(..., description="Project ID")
    project_name: str = Field(..., description="Project name")
    budget_limit: float = Field(..., description="Budget limit")
    spent: float = Field(..., description="Amount spent")
    remaining: float = Field(..., description="Remaining budget")
    history: List[float] = Field(default_factory=list, description="Spending history")
    description: Optional[str] = Field(None, description="Project description")
    status: str = Field("active", description="Project status")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    error: Optional[str] = Field(None, description="Error message if operation failed")


class ProjectListResponse(BaseModel):
    """Response model for listing projects"""
    success: bool = Field(..., description="Whether the operation was successful")
    projects: List[ProjectResponse] = Field(default_factory=list, description="List of projects")
    current_project_id: Optional[str] = Field(None, description="Current active project ID")
    count: int = Field(0, description="Total number of projects")

