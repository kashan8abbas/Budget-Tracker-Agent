"""
API routes for Budget Tracker Agent
"""

import json
import uuid
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from datetime import datetime

from api.models import (
    AnalyzeRequest, UpdateRequest, QueryRequest,
    BudgetAnalysisResponse, CurrentBudgetResponse, UpdateResponse, HealthResponse,
    ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse, ProjectListResponse
)
from agents.workers.budget_tracker_agent import BudgetTrackerAgent
from query_parser import QueryParser

router = APIRouter(prefix="/api", tags=["budget"])


def create_agent() -> BudgetTrackerAgent:
    """Create and return a BudgetTrackerAgent instance"""
    return BudgetTrackerAgent()


def resolve_project_id(agent: BudgetTrackerAgent, project_id: str = None, project_name: str = None) -> str:
    """
    Resolve project_id from project_id or project_name.
    Implements Scenario 3: Natural Language Project Detection.
    
    Args:
        agent: BudgetTrackerAgent instance
        project_id: Direct project ID (if provided)
        project_name: Project name from natural language (if provided)
        
    Returns:
        Resolved project_id or None if cannot resolve
    """
    # If project_id provided directly, use it
    if project_id:
        # Verify it exists
        if agent.get_project(project_id):
            return project_id
        return None
    
    # If project_name provided, find by name
    if project_name:
        found_id = agent.find_project_by_name(project_name)
        if found_id:
            return found_id
        # Project not found - could create it here or return None
        # For now, return None (caller can decide to create)
        return None
    
    # No project specified - use current project
    current_id = agent.get_current_project_id()
    return current_id


@router.post("/query", response_model=BudgetAnalysisResponse)
async def process_natural_language_query(request: QueryRequest):
    """
    Process a natural language query about budget.
    
    Examples:
    - "Check my budget: 50000 limit, 42000 spent"
    - "I spent 5000 today"
    - "Will I exceed my budget?"
    - "Analyze my spending with history [5000, 6000, 7000]"
    """
    try:
        # Initialize query parser (will use GEMINI_API_KEY from env)
        try:
            parser = QueryParser()
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Gemini API key not configured. {str(e)}"
            )
        
        # Create task assignment from query
        task_assignment = parser.create_task_assignment(
            request.query,
            message_id=f"api-{uuid.uuid4().hex[:8]}"
        )
        
        # Check if intent is "list" - handle listing all projects
        intent = task_assignment["task"].get("intent", "check")
        if intent == "list":
            # Handle "list all projects" query
            agent = create_agent()
            projects = agent.list_projects()
            current_project_id = agent.get_current_project_id()
            agent.close()
            
            # Convert to ProjectResponse format
            from api.models import ProjectResponse, ProjectListResponse
            project_responses = []
            for proj in projects:
                # Normalize history if needed
                history = proj.get("history", [])
                if history and isinstance(history[0], dict):
                    # Extract amounts from history objects
                    history_amounts = [h.get("amount", h.get("value", 0)) for h in history if isinstance(h, dict)]
                else:
                    history_amounts = history if isinstance(history, list) else []
                
                project_responses.append(ProjectResponse(
                    success=True,
                    project_id=proj["project_id"],
                    project_name=proj["project_name"],
                    budget_limit=proj["budget_limit"],
                    spent=proj["spent"],
                    remaining=proj["remaining"],
                    history=history_amounts,
                    description=proj.get("description"),
                    status=proj.get("status", "active"),
                    created_at=proj.get("created_at"),
                    last_updated=proj.get("last_updated")
                ))
            
            # Generate natural language response for project list
            if project_responses:
                response_lines = [f"📋 **All Projects ({len(project_responses)}):**\n"]
                for proj in project_responses:
                    response_lines.append(
                        f"• **{proj.project_name}** (ID: {proj.project_id})\n"
                        f"  - Budget: ${proj.budget_limit:,.2f}\n"
                        f"  - Spent: ${proj.spent:,.2f}\n"
                        f"  - Remaining: ${proj.remaining:,.2f}\n"
                    )
                conversational_response = "\n".join(response_lines)
            else:
                conversational_response = "No projects found. Create a project by mentioning it in a query like 'Check budget for My Project'."
            
            # Return as BudgetAnalysisResponse with project list info in response field
            return BudgetAnalysisResponse(
                success=True,
                project_id=current_project_id,
                project_name=None,
                remaining=0,
                spending_rate=None,
                overshoot_risk=False,
                predicted_spending=0,
                anomalies=[],
                recommendations=[],
                response=conversational_response
            )
        
        # Initialize agent
        agent = create_agent()
        
        # SCENARIO 3: Resolve project from natural language or request
        project_name = task_assignment["task"].get("project_name")  # Extracted from query
        
        # Debug: Log extracted project name
        if project_name:
            print(f"[DEBUG] Extracted project_name from query: '{project_name}'")
        
        project_id = resolve_project_id(
            agent,
            project_id=request.project_id,  # From request body
            project_name=project_name  # From natural language
        )
        
        # If project not found but name was mentioned, try to find with flexible matching first
        if not project_id and project_name:
            # Try flexible matching one more time (in case QueryParser extracted with "Project" suffix)
            # This handles cases like "Website Redesign Project" vs "Website Redesign"
            project_id = agent.find_project_by_name(project_name)
            if project_id:
                print(f"[DEBUG] Found project by flexible matching: {project_id}")
            
            # If still not found, create it
            if not project_id:
                # Extract budget_limit from parameters if available
                params = task_assignment["task"].get("parameters", {})
                budget_limit = params.get("budget_limit", 0.0)
                project_id = agent.create_project(project_name, budget_limit)
                if project_id:
                    print(f"[DEBUG] Created new project: {project_id} ({project_name})")
                    agent.set_current_project(project_id)
        
        # If still no project, use current or create default
        # BUT: Only if no project name was mentioned in the query
        if not project_id:
            if project_name:
                # Project name was mentioned but not found - this is an error case
                # Don't fall back to current project, create the mentioned project instead
                params = task_assignment["task"].get("parameters", {})
                budget_limit = params.get("budget_limit", 0.0)
                project_id = agent.create_project(project_name, budget_limit)
                if project_id:
                    agent.set_current_project(project_id)
            else:
                # No project mentioned - use current or create default
                project_id = agent.get_current_project_id()
                if not project_id:
                    # Create a default project
                    project_id = agent.create_project("Default Project", 0.0)
                    if project_id:
                        agent.set_current_project(project_id)
        
        # Get project name for response
        project_info = agent.get_project(project_id) if project_id else None
        project_name_display = project_info.get("project_name") if project_info else None
        
        # Process the task
        # Extract spending description if available
        spending_description = task_assignment["task"].get("spending_description")
        
        task_data = {
            "project_id": project_id,
            "parameters": task_assignment["task"].get("parameters", {}),
            "intent": task_assignment["task"].get("intent", "check"),
            "update_info": task_assignment["task"].get("update_info"),
            "spending_description": spending_description,  # Pass description to agent
            "user_query": request.query
        }
        
        results = agent.process_task(task_data)
        
        # Generate natural language response
        intent = results.get("_intent", "check")
        user_query = results.get("_user_query", request.query)
        conversational_response = None
        
        try:
            conversational_response = agent.generate_natural_language_response(
                results, intent, user_query
            )
        except Exception:
            conversational_response = agent.format_conversational_response(results, intent)
        
        # Close agent connection
        agent.close()
        
        return BudgetAnalysisResponse(
            success=True,
            project_id=project_id,
            project_name=project_name_display,
            remaining=results.get("remaining", 0),
            spending_rate=results.get("spending_rate"),
            overshoot_risk=results.get("overshoot_risk", False),
            predicted_spending=results.get("predicted_spending", 0),
            anomalies=results.get("anomalies", []),
            recommendations=results.get("recommendations", []),
            response=conversational_response
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/analyze", response_model=BudgetAnalysisResponse)
async def analyze_budget(request: AnalyzeRequest):
    """
    Analyze budget with provided parameters.
    
    This endpoint performs budget analysis without natural language processing.
    """
    try:
        agent = create_agent()
        
        # Resolve project_id
        project_id = resolve_project_id(agent, project_id=request.project_id)
        if not project_id:
            project_id = agent.get_current_project_id()
            if not project_id:
                raise HTTPException(status_code=400, detail="No project specified and no current project set")
        
        project_info = agent.get_project(project_id)
        project_name = project_info.get("project_name") if project_info else None
        
        task_data = {
            "project_id": project_id,
            "parameters": request.parameters.dict(exclude_none=True),
            "intent": request.intent or "check",
            "user_query": ""
        }
        
        results = agent.process_task(task_data)
        
        # Generate natural language response
        intent = results.get("_intent", request.intent or "check")
        conversational_response = None
        
        try:
            conversational_response = agent.generate_natural_language_response(
                results, intent, ""
            )
        except Exception:
            conversational_response = agent.format_conversational_response(results, intent)
        
        agent.close()
        
        return BudgetAnalysisResponse(
            success=True,
            remaining=results.get("remaining", 0),
            spending_rate=results.get("spending_rate"),
            overshoot_risk=results.get("overshoot_risk", False),
            predicted_spending=results.get("predicted_spending", 0),
            anomalies=results.get("anomalies", []),
            recommendations=results.get("recommendations", []),
            response=conversational_response
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/update", response_model=UpdateResponse)
async def update_budget(request: UpdateRequest):
    """
    Update budget information.
    
    Update types:
    - "add": Add to existing value (for spent, adds to history too)
    - "replace": Replace existing value
    - "set": Set value (same as replace)
    
    Update fields:
    - "spent": Update spent amount
    - "budget_limit": Update budget limit
    - "history": Update spending history
    """
    try:
        agent = create_agent()
        
        # Resolve project_id
        project_id = resolve_project_id(agent, project_id=request.project_id)
        if not project_id:
            project_id = agent.get_current_project_id()
            if not project_id:
                agent.close()
                raise HTTPException(status_code=400, detail="No project specified and no current project set")
        
        project_info = agent.get_project(project_id)
        project_name = project_info.get("project_name") if project_info else None
        
        # Apply update
        success = agent.update_current_budget(
            update_type=request.update_type,
            update_field=request.update_field,
            update_value=request.update_value,
            project_id=project_id
        )
        
        if not success:
            agent.close()
            raise HTTPException(status_code=500, detail="Failed to update budget")
        
        # Get updated budget
        current = agent.get_current_budget(project_id=project_id)
        agent.close()
        
        if current:
            remaining = current.get("budget_limit", 0) - current.get("spent", 0)
            budget_response = CurrentBudgetResponse(
                success=True,
                project_id=project_id,
                project_name=project_name,
                budget_limit=current.get("budget_limit"),
                spent=current.get("spent"),
                remaining=remaining,
                history=current.get("history", []),
                last_updated=current.get("last_updated")
            )
        else:
            budget_response = None
        
        return UpdateResponse(
            success=True,
            message=f"Successfully updated {request.update_field}",
            budget=budget_response
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/budget", response_model=CurrentBudgetResponse)
async def get_current_budget():
    """
    Get the current budget state from LTM (uses current project).
    """
    try:
        agent = create_agent()
        project_id = agent.get_current_project_id()
        current = agent.get_current_budget(project_id=project_id) if project_id else None
        agent.close()
        
        project_info = agent.get_project(project_id) if project_id else None
        project_name = project_info.get("project_name") if project_info else None
        
        if current:
            remaining = current.get("budget_limit", 0) - current.get("spent", 0)
            return CurrentBudgetResponse(
                success=True,
                project_id=project_id,
                project_name=project_name,
                budget_limit=current.get("budget_limit"),
                spent=current.get("spent"),
                remaining=remaining,
                history=current.get("history", []),
                last_updated=current.get("last_updated")
            )
        else:
            return CurrentBudgetResponse(
                success=True,
                project_id=project_id,
                project_name=project_name,
                budget_limit=None,
                spent=None,
                remaining=None,
                history=[],
                last_updated=None
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify service and MongoDB connection.
    """
    try:
        agent = create_agent()
        mongodb_connected = agent.use_mongodb
        db_name = agent.mongo_db_name if mongodb_connected else None
        agent.close()
        
        return HealthResponse(
            status="healthy",
            mongodb_connected=mongodb_connected,
            database=db_name
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            mongodb_connected=False,
            database=None
        )


# ==================== PROJECT MANAGEMENT ENDPOINTS ====================

@router.post("/projects", response_model=ProjectResponse)
async def create_project(request: ProjectCreateRequest):
    """
    Create a new project with initial budget.
    """
    try:
        agent = create_agent()
        project_id = agent.create_project(
            project_name=request.project_name,
            budget_limit=request.budget_limit or 0.0,
            description=request.description
        )
        agent.close()
        
        if not project_id:
            raise HTTPException(status_code=400, detail="Project name already exists or invalid")
        
        # Get created project
        agent = create_agent()
        project = agent.get_project(project_id)
        agent.close()
        
        if not project:
            raise HTTPException(status_code=500, detail="Project created but could not be retrieved")
        
        return ProjectResponse(
            success=True,
            project_id=project["project_id"],
            project_name=project["project_name"],
            budget_limit=project["budget_limit"],
            spent=project["spent"],
            remaining=project["remaining"],
            history=project["history"],
            description=project.get("description"),
            status=project.get("status", "active"),
            created_at=project.get("created_at"),
            last_updated=project.get("last_updated")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects():
    """
    List all projects with their basic information.
    """
    try:
        agent = create_agent()
        projects = agent.list_projects()
        current_project_id = agent.get_current_project_id()
        agent.close()
        
        # Convert to ProjectResponse format
        project_responses = []
        for proj in projects:
            project_responses.append(ProjectResponse(
                success=True,
                project_id=proj["project_id"],
                project_name=proj["project_name"],
                budget_limit=proj["budget_limit"],
                spent=proj["spent"],
                remaining=proj["remaining"],
                history=proj.get("history", []),
                description=proj.get("description"),
                status=proj.get("status", "active"),
                created_at=proj.get("created_at"),
                last_updated=proj.get("last_updated")
            ))
        
        return ProjectListResponse(
            success=True,
            projects=project_responses,
            current_project_id=current_project_id,
            count=len(project_responses)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """
    Get project details by project_id.
    """
    try:
        agent = create_agent()
        project = agent.get_project(project_id)
        agent.close()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return ProjectResponse(
            success=True,
            project_id=project["project_id"],
            project_name=project["project_name"],
            budget_limit=project["budget_limit"],
            spent=project["spent"],
            remaining=project["remaining"],
            history=project["history"],
            description=project.get("description"),
            status=project.get("status", "active"),
            created_at=project.get("created_at"),
            last_updated=project.get("last_updated")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, request: ProjectUpdateRequest):
    """
    Update project information.
    """
    try:
        agent = create_agent()
        project = agent.get_project(project_id)
        
        if not project:
            agent.close()
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update fields if provided
        if request.project_name is not None:
            # Update project name (would need new method or direct DB update)
            pass  # TODO: Implement project name update
        
        if request.budget_limit is not None:
            agent.update_current_budget(
                budget_limit=request.budget_limit,
                project_id=project_id
            )
        
        if request.description is not None:
            # Update description (would need new method)
            pass  # TODO: Implement description update
        
        if request.status is not None:
            # Update status (would need new method)
            pass  # TODO: Implement status update
        
        # Get updated project
        updated_project = agent.get_project(project_id)
        agent.close()
        
        return ProjectResponse(
            success=True,
            project_id=updated_project["project_id"],
            project_name=updated_project["project_name"],
            budget_limit=updated_project["budget_limit"],
            spent=updated_project["spent"],
            remaining=updated_project["remaining"],
            history=updated_project["history"],
            description=updated_project.get("description"),
            status=updated_project.get("status", "active"),
            created_at=updated_project.get("created_at"),
            last_updated=updated_project.get("last_updated")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/projects/{project_id}", response_model=ProjectResponse)
async def delete_project(project_id: str):
    """
    Delete a project (cannot delete current project).
    """
    try:
        agent = create_agent()
        project = agent.get_project(project_id)
        
        if not project:
            agent.close()
            raise HTTPException(status_code=404, detail="Project not found")
        
        success = agent.delete_project(project_id)
        agent.close()
        
        if not success:
            raise HTTPException(status_code=400, detail="Cannot delete current project or project deletion failed")
        
        return ProjectResponse(
            success=True,
            project_id=project["project_id"],
            project_name=project["project_name"],
            budget_limit=project["budget_limit"],
            spent=project["spent"],
            remaining=project["remaining"],
            history=project["history"],
            description=project.get("description"),
            status="deleted",
            created_at=project.get("created_at"),
            last_updated=project.get("last_updated")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/projects/{project_id}/set-current", response_model=ProjectResponse)
async def set_current_project(project_id: str):
    """
    Set a project as the current active project.
    """
    try:
        agent = create_agent()
        success = agent.set_current_project(project_id)
        
        if not success:
            agent.close()
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = agent.get_project(project_id)
        agent.close()
        
        return ProjectResponse(
            success=True,
            project_id=project["project_id"],
            project_name=project["project_name"],
            budget_limit=project["budget_limit"],
            spent=project["spent"],
            remaining=project["remaining"],
            history=project["history"],
            description=project.get("description"),
            status=project.get("status", "active"),
            created_at=project.get("created_at"),
            last_updated=project.get("last_updated")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/projects/{project_id}/budget", response_model=CurrentBudgetResponse)
async def get_project_budget(project_id: str):
    """
    Get budget for a specific project.
    """
    try:
        agent = create_agent()
        project = agent.get_project(project_id)
        current = agent.get_current_budget(project_id=project_id)
        agent.close()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if current:
            remaining = current.get("budget_limit", 0) - current.get("spent", 0)
            return CurrentBudgetResponse(
                success=True,
                project_id=project_id,
                project_name=project["project_name"],
                budget_limit=current.get("budget_limit"),
                spent=current.get("spent"),
                remaining=remaining,
                history=current.get("history", []),
                last_updated=current.get("last_updated")
            )
        else:
            return CurrentBudgetResponse(
                success=True,
                project_id=project_id,
                project_name=project["project_name"],
                budget_limit=None,
                spent=None,
                remaining=None,
                history=[],
                last_updated=None
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

