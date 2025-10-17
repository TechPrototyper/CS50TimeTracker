#!/usr/bin/env python3
"""
SITR - Simple Time Tracker API

FastAPI server providing REST API for time tracking functionality.
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

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


# Database initialization is handled by `sitr init-db` command
# No automatic initialization on module load to avoid performance overhead


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


@app.get("/api/users", tags=["Users"])
async def list_users(include_archived: bool = False):
    """
    Get all users.
    
    Args:
        include_archived: If True, include archived users
    """
    db_manager = get_db_manager()
    user_repo = UserRepository(db_manager, User)

    try:
        if include_archived:
            users = user_repo.get_all()
        else:
            users = user_repo.get_active_users()
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


@app.post("/api/users/{email}/archive", tags=["Users"])
async def archive_user(email: str):
    """Archive a user (soft delete)."""
    db_manager = get_db_manager()
    user_repo = UserRepository(db_manager, User)

    try:
        user = user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{email}' not found"
            )
        
        if not user.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{email}' is already archived"
            )

        user_repo.archive_user(user.id)
        return {
            "success": True,
            "message": f"User '{email}' archived"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/users/{email}/restore", tags=["Users"])
async def restore_user(email: str):
    """Restore an archived user."""
    db_manager = get_db_manager()
    user_repo = UserRepository(db_manager, User)

    try:
        user = user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{email}' not found"
            )
        
        if user.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{email}' is not archived"
            )

        user_repo.restore_user(user.id)
        return {
            "success": True,
            "message": f"User '{email}' restored"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/users/{email}/deletion-impact", tags=["Users"])
async def get_user_deletion_impact(email: str):
    """Get information about what would be deleted if user is deleted."""
    db_manager = get_db_manager()
    user_repo = UserRepository(db_manager, User)

    try:
        user = user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{email}' not found"
            )

        # Count tracking entries
        from sqlmodel import Session, select
        with Session(db_manager.engine) as session:
            tracking_count = len(
                session.exec(
                    select(Tracking).where(Tracking.user_id == user.id)
                ).all()
            )
            
            # Get projects owned by this user
            projects_owned = session.exec(
                select(Project).where(Project.user_id == user.id)
            ).all()
            
            projects_count = len(projects_owned)
            
            # Check if any projects have tracking from other users
            projects_with_shared_tracking = 0
            for project in projects_owned:
                other_users_tracking = session.exec(
                    select(Tracking).where(
                        Tracking.project_id == project.id,
                        Tracking.user_id != user.id
                    )
                ).first()
                if other_users_tracking:
                    projects_with_shared_tracking += 1

        return {
            "tracking_entries": tracking_count,
            "projects_owned": projects_count,
            "projects_with_shared_tracking": projects_with_shared_tracking
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/api/users/{email}", tags=["Users"])
async def delete_user(email: str, cascade: bool = False):
    """
    Delete a user.
    
    Args:
        email: User email
        cascade: If True, also delete all related data
    """
    db_manager = get_db_manager()
    user_repo = UserRepository(db_manager, User)

    try:
        user = user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{email}' not found"
            )

        if cascade:
            # Delete with CASCADE - remove all related data
            from sqlmodel import Session, select, delete as sql_delete
            
            deleted_counts = {
                "trackings": 0,
                "projects": 0
            }
            
            with Session(db_manager.engine) as session:
                # Delete all tracking entries for this user
                tracking_result = session.exec(
                    sql_delete(Tracking).where(Tracking.user_id == user.id)
                )
                deleted_counts["trackings"] = tracking_result.rowcount
                
                # Get projects owned by this user
                projects = session.exec(
                    select(Project).where(Project.user_id == user.id)
                ).all()
                
                # Delete projects (and their tracking via cascade)
                for project in projects:
                    # Delete tracking for this project from all users
                    session.exec(
                        sql_delete(Tracking).where(
                            Tracking.project_id == project.id
                        )
                    )
                    session.delete(project)
                    deleted_counts["projects"] += 1
                
                # Now delete the user
                session.delete(user)
                session.commit()
            
            return {
                "success": True,
                "message": f"User '{email}' and all related data deleted",
                "deleted": deleted_counts
            }
        else:
            # Try to delete without cascade - will fail if data exists
            try:
                user_repo.delete(user.id)
                return {
                    "success": True,
                    "message": f"User '{email}' deleted"
                }
            except Exception as e:
                if "FOREIGN KEY" in str(e) or "IntegrityError" in str(e):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            f"Cannot delete user '{email}' because they have "
                            "related data (tracking entries or projects). "
                            "Use cascade=true to delete all related data, "
                            "or use /archive endpoint to archive the user."
                        )
                    )
                raise
                
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
            auto_create=True  # Auto-create project if not found
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


@app.get("/api/tracking/latest", tags=["Time Tracking"])
async def get_latest_tracking(user_id: int):
    """Get the latest tracking entry for a user.
    
    This is useful for determining what the user is currently working on.
    """
    db_manager = get_db_manager()
    tracking_repo = TrackingRepository(db_manager, Tracking)
    project_repo = ProjectRepository(db_manager, Project)

    try:
        # Get all tracking entries for user, sorted by date_time desc
        all_entries = tracking_repo.get_all()
        user_entries = [
            e for e in all_entries if e.user_id == user_id
        ]
        
        if not user_entries:
            return None
        
        # Sort by date_time descending and get the latest
        user_entries.sort(key=lambda e: e.date_time, reverse=True)
        latest = user_entries[0]
        
        # Get project name if project_id exists
        project_name = None
        if latest.project_id:
            project = project_repo.get(latest.project_id)
            if project:
                project_name = project.name
        
        # Ensure timestamp has UTC timezone info
        timestamp = latest.date_time
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        
        return {
            "id": latest.id,
            "user_id": latest.user_id,
            "action": latest.action,
            "project_name": project_name,
            "timestamp": timestamp.isoformat(),
            "message": latest.message
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/tracking/today", tags=["Time Tracking"])
async def get_today_tracking(user_id: int):
    """Get all tracking entries for today for a user.
    
    Returns entries from today's workday in chronological order.
    """
    db_manager = get_db_manager()
    tracking_repo = TrackingRepository(db_manager, Tracking)
    project_repo = ProjectRepository(db_manager, Project)

    try:
        # Get all tracking entries for user
        all_entries = tracking_repo.get_all()
        user_entries = [
            e for e in all_entries if e.user_id == user_id
        ]
        
        if not user_entries:
            return []
        
        # Sort by date_time descending
        user_entries.sort(key=lambda e: e.date_time, reverse=True)
        
        # Find today's entries (from last Workday Start to now or Workday End)
        today_entries = []
        found_workday_start = False
        
        for entry in user_entries:
            if entry.action == "Workday End":
                # If we find a Workday End before finding a Workday Start,
                # it means the workday has already ended - no active workday
                if not found_workday_start:
                    return []
                # If we already found the start, stop here (end of workday)
                break
            
            if entry.action == "Workday Start":
                found_workday_start = True
                # Add this entry
                project_name = None
                if entry.project_id:
                    project = project_repo.get(entry.project_id)
                    if project:
                        project_name = project.name
                
                # Ensure timestamp has UTC timezone info
                timestamp = entry.date_time
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                
                today_entries.append({
                    "id": entry.id,
                    "user_id": entry.user_id,
                    "action": entry.action,
                    "project_name": project_name,
                    "timestamp": timestamp.isoformat(),
                    "message": entry.message
                })
                break  # Found workday start, stop searching
            
            if found_workday_start or entry.action in [
                "Project Start", "Project End", "Project Resume",
                "Break Start", "Break End"
            ]:
                # Add this entry
                project_name = None
                if entry.project_id:
                    project = project_repo.get(entry.project_id)
                    if project:
                        project_name = project.name
                
                # Ensure timestamp has UTC timezone info
                timestamp = entry.date_time
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                
                today_entries.append({
                    "id": entry.id,
                    "user_id": entry.user_id,
                    "action": entry.action,
                    "project_name": project_name,
                    "timestamp": timestamp.isoformat(),
                    "message": entry.message
                })
        
        # Reverse to get chronological order (oldest first)
        today_entries.reverse()
        
        return today_entries
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Reports API
@app.get("/api/reports/daily", tags=["Reports"])
async def get_daily_report(user_id: int, date: Optional[str] = None):
    """Get daily report for a user.
    
    Returns all tracking entries for a specific day with calculated durations.
    If no date is provided, returns today's report.
    
    Args:
        user_id: The user ID
        date: Optional date in YYYY-MM-DD format (defaults to today)
    """
    db_manager = get_db_manager()
    tracking_repo = TrackingRepository(db_manager, Tracking)
    project_repo = ProjectRepository(db_manager, Project)
    
    try:
        from datetime import date as date_type, timedelta
        
        # Parse target date
        if date:
            target_date = datetime.fromisoformat(date).date()
        else:
            target_date = datetime.now().date()
        
        # Get all entries for user
        all_entries = tracking_repo.get_all()
        user_entries = [e for e in all_entries if e.user_id == user_id]
        user_entries.sort(key=lambda e: e.date_time)
        
        # Filter for target date
        day_entries = []
        for entry in user_entries:
            entry_date = entry.date_time.date()
            if entry_date == target_date:
                # Get project name if exists
                project_name = None
                if entry.project_id:
                    project = project_repo.get(entry.project_id)
                    if project:
                        project_name = project.name
                
                # Ensure timestamp has UTC timezone info
                timestamp = entry.date_time
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                
                day_entries.append({
                    "id": entry.id,
                    "timestamp": timestamp.isoformat(),
                    "action": entry.action,
                    "project_name": project_name,
                    "message": entry.message
                })
        
        return {
            "date": target_date.isoformat(),
            "user_id": user_id,
            "entries": day_entries
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/reports/weekly", tags=["Reports"])
async def get_weekly_report(
    user_id: int,
    week_start: Optional[str] = None
):
    """Get weekly report for a user.
    
    Returns all tracking entries for a week with calculated durations per day.
    If no week_start is provided, returns current week.
    
    Args:
        user_id: The user ID
        week_start: Optional start date in YYYY-MM-DD format (Monday)
    """
    db_manager = get_db_manager()
    tracking_repo = TrackingRepository(db_manager, Tracking)
    project_repo = ProjectRepository(db_manager, Project)
    
    try:
        from datetime import date as date_type, timedelta
        
        # Parse start date (Monday)
        if week_start:
            start_date = datetime.fromisoformat(week_start).date()
        else:
            today = datetime.now().date()
            # Get Monday of current week
            start_date = today - timedelta(days=today.weekday())
        
        end_date = start_date + timedelta(days=6)  # Sunday
        
        # Get all entries for user in date range
        all_entries = tracking_repo.get_all()
        user_entries = [e for e in all_entries if e.user_id == user_id]
        user_entries.sort(key=lambda e: e.date_time)
        
        # Group by day
        week_data = {}
        for entry in user_entries:
            entry_date = entry.date_time.date()
            if start_date <= entry_date <= end_date:
                date_str = entry_date.isoformat()
                if date_str not in week_data:
                    week_data[date_str] = []
                
                # Get project name
                project_name = None
                if entry.project_id:
                    project = project_repo.get(entry.project_id)
                    if project:
                        project_name = project.name
                
                # Ensure timestamp has UTC timezone info
                timestamp = entry.date_time
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                
                week_data[date_str].append({
                    "id": entry.id,
                    "timestamp": timestamp.isoformat(),
                    "action": entry.action,
                    "project_name": project_name,
                    "message": entry.message
                })
        
        return {
            "week_start": start_date.isoformat(),
            "week_end": end_date.isoformat(),
            "user_id": user_id,
            "days": week_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/reports/project", tags=["Reports"])
async def get_project_report(
    user_id: int,
    project_name: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    """Get report for a specific project.
    
    Returns all tracking entries for a project within date range.
    
    Args:
        user_id: The user ID
        project_name: Name of the project
        from_date: Optional start date in YYYY-MM-DD format
        to_date: Optional end date in YYYY-MM-DD format
    """
    db_manager = get_db_manager()
    tracking_repo = TrackingRepository(db_manager, Tracking)
    project_repo = ProjectRepository(db_manager, Project)
    
    try:
        # Get project
        project = project_repo.get_by_name(project_name, user_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{project_name}' not found"
            )
        
        # Parse date range
        start_date = None
        end_date = None
        if from_date:
            start_date = datetime.fromisoformat(from_date).date()
        if to_date:
            end_date = datetime.fromisoformat(to_date).date()
        
        # Get all entries for this project
        all_entries = tracking_repo.get_all()
        project_entries = [
            e for e in all_entries
            if e.user_id == user_id and e.project_id == project.id
        ]
        project_entries.sort(key=lambda e: e.date_time)
        
        # Filter by date range if specified
        filtered_entries = []
        for entry in project_entries:
            entry_date = entry.date_time.date()
            
            if start_date and entry_date < start_date:
                continue
            if end_date and entry_date > end_date:
                continue
            
            # Ensure timestamp has UTC timezone info
            timestamp = entry.date_time
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            
            filtered_entries.append({
                "id": entry.id,
                "timestamp": timestamp.isoformat(),
                "action": entry.action,
                "project_name": project_name,
                "message": entry.message
            })
        
        return {
            "project_name": project_name,
            "user_id": user_id,
            "from_date": from_date,
            "to_date": to_date,
            "entries": filtered_entries
        }
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
