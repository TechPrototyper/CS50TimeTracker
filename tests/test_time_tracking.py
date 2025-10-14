"""
Tests for time tracking repositories and service.
"""
import pytest
from sqlmodel import SQLModel
from database_manager import DatabaseManager
from sitr_models import User, Project, Tracking
from database_repositories import (
    UserRepository,
    ProjectRepository,
    TrackingRepository
)
from time_management_service import TimeManagementService
from enums import ActionType, ProjectState


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    database_url = "sqlite:///:memory:"
    db_manager = DatabaseManager(database_url)
    db_manager.create_tables()  # Create tables using the db_manager
    return db_manager


@pytest.fixture
def test_user(in_memory_db):
    """Create a test user."""
    user_repo = UserRepository(in_memory_db, User)
    user = user_repo.add({
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com"
    })
    return user


def test_user_crud(in_memory_db):
    """Test basic CRUD operations for users."""
    user_repo = UserRepository(in_memory_db, User)

    # Create
    user = user_repo.add({
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "middle_initial": "M"
    })
    assert user.id is not None
    assert user.first_name == "John"
    assert user.middle_initial == "M"

    # Read
    retrieved_user = user_repo.get(user.id)
    assert retrieved_user.email == "john@example.com"

    # Update
    updated_user = user_repo.update(user.id, {"middle_initial": "K"})
    assert updated_user.middle_initial == "K"

    # List all
    all_users = user_repo.get_all()
    assert len(all_users) >= 1

    # Delete
    user_repo.delete(user.id)
    deleted_user = user_repo.get(user.id)
    assert deleted_user is None


def test_project_crud(in_memory_db, test_user):
    """Test basic CRUD operations for projects."""
    project_repo = ProjectRepository(in_memory_db, Project)

    # Create
    project = project_repo.add({
        "name": "Test Project",
        "user_id": test_user.id,
        "state": ProjectState.ACTIVE.value
    })
    assert project.id is not None
    assert project.name == "Test Project"

    # Get by name
    found_project = project_repo.get_by_name("Test Project", test_user.id)
    assert found_project.id == project.id

    # Get active projects
    active_projects = project_repo.get_active_projects(test_user.id)
    assert len(active_projects) == 1

    # Archive
    project_repo.update(project.id, {
        "state": ProjectState.ARCHIVED.value
    })
    active_projects = project_repo.get_active_projects(test_user.id)
    assert len(active_projects) == 0


def test_complete_workday_flow(in_memory_db, test_user):
    """
    Test a complete workday flow:
    start day -> project A -> break -> continue -> project B -> end day
    """
    service = TimeManagementService(in_memory_db)
    user_id = test_user.id

    # Start the workday
    result = service.start_day(user_id)
    assert result['success'] is True

    # Try to start day again (should fail)
    with pytest.raises(ValueError, match="already started"):
        service.start_day(user_id)

    # Start working on Project A
    result = service.start_project(user_id, "Project A")
    assert result['success'] is True
    assert result['project_id'] is not None
    project_a_id = result['project_id']

    # Start a break
    result = service.start_break(user_id, "Coffee break")
    assert result['success'] is True

    # Continue working (should resume Project A)
    result = service.continue_project(user_id)
    assert result['success'] is True
    assert result['project_id'] == project_a_id

    # Switch to Project B (should auto-end Project A)
    result = service.start_project(user_id, "Project B")
    assert result['success'] is True
    assert result['ended_project_id'] == project_a_id

    # End the workday (should auto-close Project B)
    result = service.end_day(user_id)
    assert result['success'] is True
    assert result['closed_project'] is True


def test_tracking_state_queries(in_memory_db, test_user):
    """Test tracking repository state query methods."""
    service = TimeManagementService(in_memory_db)
    tracking_repo = TrackingRepository(in_memory_db, Tracking)
    user_id = test_user.id

    # Initially no open day
    assert not tracking_repo.has_open_day(user_id)

    # Start day
    service.start_day(user_id)
    assert tracking_repo.has_open_day(user_id)

    # Start project
    service.start_project(user_id, "Test Project")
    assert tracking_repo.is_any_project_active(user_id)

    active_project_id = tracking_repo.get_active_project_id(user_id)
    assert active_project_id is not None
    assert tracking_repo.is_project_active(user_id, active_project_id)

    # Start break
    service.start_break(user_id)
    assert tracking_repo.is_break_active(user_id)
    assert tracking_repo.is_any_project_active(user_id)  # Still active

    # Continue project
    service.continue_project(user_id)
    assert not tracking_repo.is_break_active(user_id)
    assert tracking_repo.is_any_project_active(user_id)

    # End day
    service.end_day(user_id)
    assert not tracking_repo.has_open_day(user_id)
    assert not tracking_repo.is_any_project_active(user_id)


def test_break_without_project_fails(in_memory_db, test_user):
    """Test that starting a break without an active project fails."""
    service = TimeManagementService(in_memory_db)
    user_id = test_user.id

    service.start_day(user_id)

    # Try to start break without a project
    with pytest.raises(ValueError, match="No active project"):
        service.start_break(user_id)


def test_project_without_workday_fails(in_memory_db, test_user):
    """Test that starting a project without an open workday fails."""
    service = TimeManagementService(in_memory_db)
    user_id = test_user.id

    # Try to start project without starting day
    with pytest.raises(ValueError, match="No open workday"):
        service.start_project(user_id, "Test Project")


def test_multiple_projects_tracking_count(in_memory_db, test_user):
    """Test that project tracking counts are updated correctly."""
    service = TimeManagementService(in_memory_db)
    project_repo = ProjectRepository(in_memory_db, Project)
    user_id = test_user.id

    service.start_day(user_id)

    # Start Project A
    result = service.start_project(user_id, "Project A")
    project_a_id = result['project_id']

    # Switch to Project B
    result = service.start_project(user_id, "Project B")
    project_b_id = result['project_id']

    # Switch back to Project A
    result = service.start_project(user_id, "Project A")

    # Check tracking counts
    project_a = project_repo.get(project_a_id)
    project_b = project_repo.get(project_b_id)

    assert project_a.tracking_count == 2  # Started twice
    assert project_b.tracking_count == 1  # Started once


def test_get_last_project_before_break(in_memory_db, test_user):
    """Test getting the last project before a break."""
    service = TimeManagementService(in_memory_db)
    tracking_repo = TrackingRepository(in_memory_db, Tracking)
    user_id = test_user.id

    service.start_day(user_id)

    # Start Project A
    result = service.start_project(user_id, "Project A")
    project_a_id = result['project_id']

    # Start break
    service.start_break(user_id)

    # Check that we can get the last project before break
    last_project_id = tracking_repo.get_last_project_before_break(user_id)
    assert last_project_id == project_a_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
