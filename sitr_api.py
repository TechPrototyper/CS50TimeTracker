#!/usr/bin/env python3
"""
SITR - Simple Time Tracker API

FastAPI server providing REST API for time tracking functionality.
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

from database_manager import DatabaseManager
from database_repositories import (
    UserRepository,
    ProjectRepository,
    TrackingRepository
)
from time_management_service import TimeManagementService
from sitr_models import User, Project, Tracking
from enums import ProjectState


# Pydantic Models for API
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    middle_initial: Optional[str] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    middle_initial: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    middle_initial: Optional[str] = None
    last_active: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    name: str
    user_id: int


class ProjectResponse(BaseModel):
    id: int
    name: str
    user_id: int
    state: str
    archive_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StartDayRequest(BaseModel):
    user_id: int


class EndDayRequest(BaseModel):
    user_id: int


class StartProjectRequest(BaseModel):
    user_id: int
    project_name: str
    no_confirm: bool = False


class EndProjectRequest(BaseModel):
    user_id: int
    project_name: str


class StartBreakRequest(BaseModel):
    user_id: int
    message: Optional[str] = None


class EndBreakRequest(BaseModel):
    user_id: int


class ContinueProjectRequest(BaseModel):
    user_id: int


class ArchiveProjectRequest(BaseModel):
    project_name: str
    user_id: int
    unarchive: bool = False


class OperationResponse(BaseModel):
    success: bool
    message: str
    timestamp: Optional[datetime] = None
    data: Optional[Dict[str, Any]] = None


# Initialize FastAPI app
app = FastAPI(
    title="SITR API",
    description="Simple Time Tracker REST API",
    version="1.0.0"
)

# Add CORS middleware for future web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get database manager
def get_db_manager() -> DatabaseManager:
    """Get database manager instance."""
    from pathlib import Path
    db_path = Path.home() / ".sitr" / "sitr.db"
    return DatabaseManager(f"sqlite:///{db_path}")


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Check if API is running."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "SITR API"
    }


# User Management Endpoints
@app.post("/api/users", response_model=UserResponse, tags=["Users"])
async def create_user(user_data: UserCreate):
    """Create a new user."""
    db_manager = get_db_manager()
    user_repo = UserRepository(db_manager, User)

    try:
        user = user_repo.add({
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "email": user_data.email,
            "middle_initial": user_data.middle_initial
        })
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/api/users", response_model=List[UserResponse], tags=["Users"])
async def list_users():
    """Get all users."""
    db_manager = get_db_manager()
    user_repo = UserRepository(db_manager, User)

    try:
        users = user_repo.get_all()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/users/email/{email}",
         response_model=UserResponse,
         tags=["Users"])
async def get_user_by_email(email: str):
    """Get user by email address."""
    db_manager = get_db_manager()
    user_repo = UserRepository(db_manager, User)

    try:
        user = user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{email}' not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.put("/api/users/{email}", response_model=UserResponse, tags=["Users"])
async def update_user(email: str, user_data: UserUpdate):
    """Update user information."""
    db_manager = get_db_manager()
    user_repo = UserRepository(db_manager, User)

    try:
        user = user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{email}' not found"
            )

        update_data = {}
        if user_data.first_name is not None:
            update_data["first_name"] = user_data.first_name
        if user_data.last_name is not None:
            update_data["last_name"] = user_data.last_name
        if user_data.middle_initial is not None:
            update_data["middle_initial"] = user_data.middle_initial

        if update_data:
            user_repo.update(user.id, update_data)
            user = user_repo.get(user.id)

        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/api/users/{email}", tags=["Users"])
async def delete_user(email: str):
    """Delete a user."""
    db_manager = get_db_manager()
    user_repo = UserRepository(db_manager, User)

    try:
        user = user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{email}' not found"
            )

        user_repo.delete(user.id)
        return {"success": True, "message": f"User '{email}' deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/users/select/{email}", tags=["Users"])
async def select_user(email: str):
    """Mark user as last selected (for client-side tracking)."""
    db_manager = get_db_manager()
    user_repo = UserRepository(db_manager, User)

    try:
        user = user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{email}' not found"
            )

        user_repo.update(user.id, {"last_active": datetime.utcnow()})
        return {
            "success": True,
            "message": f"User '{email}' selected",
            "user_id": user.id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Workday Endpoints
@app.post("/api/workday/start",
          response_model=OperationResponse,
          tags=["Workday"])
async def start_day(request: StartDayRequest):
    """Start a new work day."""
    db_manager = get_db_manager()
    service = TimeManagementService(db_manager)

    try:
        result = service.start_day(request.user_id)
        return OperationResponse(
            success=True,
            message=result["message"],
            timestamp=result["timestamp"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/workday/end",
          response_model=OperationResponse,
          tags=["Workday"])
async def end_day(request: EndDayRequest):
    """End the current work day."""
    db_manager = get_db_manager()
    service = TimeManagementService(db_manager)

    try:
        result = service.end_day(request.user_id)
        return OperationResponse(
            success=True,
            message=result["message"],
            timestamp=result["timestamp"],
            data={
                "closed_project": result.get("closed_project"),
                "closed_break": result.get("closed_break")
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Project Tracking Endpoints
@app.post("/api/projects/start",
          response_model=OperationResponse,
          tags=["Projects"])
async def start_project(request: StartProjectRequest):
    """Start working on a project."""
    db_manager = get_db_manager()
    service = TimeManagementService(db_manager)

    try:
        result = service.start_project(
            request.user_id,
            request.project_name,
            request.no_confirm
        )
        return OperationResponse(
            success=True,
            message=result["message"],
            timestamp=result["timestamp"],
            data={
                "previous_project": result.get("previous_project"),
                "closed_break": result.get("closed_break")
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/projects/end",
          response_model=OperationResponse,
          tags=["Projects"])
async def end_project(request: EndProjectRequest):
    """End working on a project."""
    db_manager = get_db_manager()
    service = TimeManagementService(db_manager)

    try:
        result = service.end_project(
            request.user_id,
            request.project_name
        )
        return OperationResponse(
            success=True,
            message=result["message"],
            timestamp=result["timestamp"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Break Endpoints
@app.post("/api/breaks/start",
          response_model=OperationResponse,
          tags=["Breaks"])
async def start_break(request: StartBreakRequest):
    """Start a break."""
    db_manager = get_db_manager()
    service = TimeManagementService(db_manager)

    try:
        result = service.start_break(request.user_id, request.message)
        return OperationResponse(
            success=True,
            message=result["message"],
            timestamp=result["timestamp"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/breaks/end",
          response_model=OperationResponse,
          tags=["Breaks"])
async def end_break(request: EndBreakRequest):
    """End a break."""
    db_manager = get_db_manager()
    service = TimeManagementService(db_manager)

    try:
        result = service.end_break(request.user_id)
        return OperationResponse(
            success=True,
            message=result["message"],
            timestamp=result["timestamp"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/projects/continue",
          response_model=OperationResponse,
          tags=["Projects"])
async def continue_project(request: ContinueProjectRequest):
    """End break and resume previous project."""
    db_manager = get_db_manager()
    service = TimeManagementService(db_manager)

    try:
        result = service.continue_project(request.user_id)
        return OperationResponse(
            success=True,
            message=result["message"],
            timestamp=result["timestamp"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Project Management Endpoints
@app.post("/api/projects",
          response_model=ProjectResponse,
          tags=["Project Management"])
async def create_project(project_data: ProjectCreate):
    """Create a new project."""
    db_manager = get_db_manager()
    project_repo = ProjectRepository(db_manager, Project)

    try:
        project = project_repo.add({
            "name": project_data.name,
            "user_id": project_data.user_id,
            "state": ProjectState.ACTIVE.value
        })
        return project
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/api/projects",
         response_model=List[ProjectResponse],
         tags=["Project Management"])
async def list_projects(
    user_id: int,
    include_archived: bool = False,
    sort_alphabetically: bool = False
):
    """List projects for a user."""
    db_manager = get_db_manager()
    project_repo = ProjectRepository(db_manager, Project)

    try:
        if include_archived:
            projects = project_repo.get_all()
            projects = [p for p in projects if p.user_id == user_id]
        else:
            projects = project_repo.get_active_projects(user_id)

        if sort_alphabetically:
            projects = sorted(projects, key=lambda p: p.name.lower())
        else:
            projects = sorted(projects, key=lambda p: p.created_at)

        return projects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/projects/archive", tags=["Project Management"])
async def archive_project(request: ArchiveProjectRequest):
    """Archive or unarchive a project."""
    db_manager = get_db_manager()
    project_repo = ProjectRepository(db_manager, Project)

    try:
        project = project_repo.get_by_name(
            request.project_name,
            request.user_id
        )
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{request.project_name}' not found"
            )

        if request.unarchive:
            project_repo.update(project.id, {
                "state": ProjectState.ACTIVE.value,
                "archive_date": None
            })
            message = f"Project '{request.project_name}' unarchived"
        else:
            project_repo.update(project.id, {
                "state": ProjectState.ARCHIVED.value,
                "archive_date": datetime.utcnow()
            })
            message = f"Project '{request.project_name}' archived"

        return {"success": True, "message": message}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Main entry point for running with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
