from datetime import datetime, timezone
from typing import Optional
from database_manager import DatabaseManager
from database_repositories import (
    UserRepository,
    ProjectRepository,
    TrackingRepository
)
from sitr_models import User, Project, Tracking
from enums import ActionType, ProjectState


class TimeManagementService:
    """
    Service layer for time management operations.

    Handles workday, project, and break management with proper
    transactional control and business logic.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the service with a database manager.

        Args:
            db_manager (DatabaseManager): The database manager instance.
        """
        self.db_manager = db_manager

    def start_day(self, user_id: int) -> dict:
        """
        Start a new workday for the user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            dict: Status information about the operation.

        Raises:
            ValueError: If user not found or day already started.
        """
        with self.db_manager.session() as session:
            user_repo = UserRepository(
                self.db_manager, User, session=session
            )
            tracking_repo = TrackingRepository(
                self.db_manager, Tracking, session=session
            )

            # Check if user exists
            user = user_repo.get(user_id)
            if not user:
                raise ValueError("User not found")

            # Check if day already started
            if tracking_repo.has_open_day(user_id):
                raise ValueError("The workday has already started")

            # Create workday start tracking
            now = datetime.now(timezone.utc)
            tracking_repo.add({
                "user_id": user_id,
                "action": ActionType.WORKDAY_START.value,
                "date_time": now,
                "project_id": None,
                "message": None
            })

            # Update user's last_active
            user_repo.update(user_id, {"last_active": now})

            return {
                "success": True,
                "message": "Workday started",
                "timestamp": now
            }

    def end_day(self, user_id: int) -> dict:
        """
        End the workday for the user.

        Automatically closes any open projects or breaks.

        Args:
            user_id (int): The ID of the user.

        Returns:
            dict: Status information about the operation.

        Raises:
            ValueError: If user not found or no open workday.
        """
        with self.db_manager.session() as session:
            user_repo = UserRepository(
                self.db_manager, User, session=session
            )
            tracking_repo = TrackingRepository(
                self.db_manager, Tracking, session=session
            )

            # Check if user exists
            user = user_repo.get(user_id)
            if not user:
                raise ValueError("User not found")

            # Check if there's an open workday
            if not tracking_repo.has_open_day(user_id):
                raise ValueError("No open workday to end")

            now = datetime.now(timezone.utc)

            # Close any active break
            if tracking_repo.is_break_active(user_id):
                tracking_repo.add({
                    "user_id": user_id,
                    "action": ActionType.BREAK_END.value,
                    "date_time": now,
                    "project_id": None,
                    "message": "Auto-closed at end of day"
                })

            # Close any active project
            active_project_id = tracking_repo.get_active_project_id(user_id)
            if active_project_id:
                tracking_repo.add({
                    "user_id": user_id,
                    "action": ActionType.PROJECT_END.value,
                    "date_time": now,
                    "project_id": active_project_id,
                    "message": "Auto-closed at end of day"
                })

            # End the workday
            tracking_repo.add({
                "user_id": user_id,
                "action": ActionType.WORKDAY_END.value,
                "date_time": now,
                "project_id": None,
                "message": None
            })

            # Update user's last_active
            user_repo.update(user_id, {"last_active": now})

            return {
                "success": True,
                "message": "Workday ended",
                "timestamp": now,
                "closed_project": active_project_id is not None,
                "closed_break": tracking_repo.is_break_active(user_id)
            }

    def start_project(
        self,
        user_id: int,
        project_name: str,
        auto_create: bool = True
    ) -> dict:
        """
        Start working on a project.

        If another project is active, it will be automatically ended
        (handover logic).

        Args:
            user_id (int): The ID of the user.
            project_name (str): The name of the project.
            auto_create (bool): Whether to auto-create project if not found.

        Returns:
            dict: Status information about the operation.

        Raises:
            ValueError: If user not found, no open workday, or project
                not found and auto_create is False.
        """
        with self.db_manager.session() as session:
            user_repo = UserRepository(
                self.db_manager, User, session=session
            )
            project_repo = ProjectRepository(
                self.db_manager, Project, session=session
            )
            tracking_repo = TrackingRepository(
                self.db_manager, Tracking, session=session
            )

            # Check if user exists
            user = user_repo.get(user_id)
            if not user:
                raise ValueError("User not found")

            # Check if workday is open
            if not tracking_repo.has_open_day(user_id):
                raise ValueError(
                    "No open workday. Please start your day first."
                )

            # Get or create project
            project = project_repo.get_by_name(project_name, user_id)
            if not project:
                if auto_create:
                    project = project_repo.add({
                        "name": project_name,
                        "user_id": user_id,
                        "state": ProjectState.ACTIVE.value
                    })
                else:
                    raise ValueError(f"Project '{project_name}' not found")

            now = datetime.now(timezone.utc)
            ended_project_id = None

            # Handover: End any currently active project
            active_project_id = tracking_repo.get_active_project_id(user_id)
            if active_project_id:
                if active_project_id == project.id:
                    return {
                        "success": False,
                        "message": f"Project '{project_name}' is already active"
                    }

                tracking_repo.add({
                    "user_id": user_id,
                    "action": ActionType.PROJECT_END.value,
                    "date_time": now,
                    "project_id": active_project_id,
                    "message": "Auto-ended for project switch"
                })
                ended_project_id = active_project_id

            # End any active break
            if tracking_repo.is_break_active(user_id):
                tracking_repo.add({
                    "user_id": user_id,
                    "action": ActionType.BREAK_END.value,
                    "date_time": now,
                    "project_id": None,
                    "message": "Auto-ended for project start"
                })

            # Start the new project
            tracking_repo.add({
                "user_id": user_id,
                "action": ActionType.PROJECT_START.value,
                "date_time": now,
                "project_id": project.id,
                "message": None
            })

            # Update project tracking count
            project_repo.update(
                project.id,
                {"tracking_count": project.tracking_count + 1}
            )

            # Update user's last_active
            user_repo.update(user_id, {"last_active": now})

            return {
                "success": True,
                "message": f"Started working on '{project_name}'",
                "timestamp": now,
                "project_id": project.id,
                "ended_project_id": ended_project_id,
                "was_created": not project
            }

    def end_project(
        self,
        user_id: int,
        project_name: Optional[str] = None
    ) -> dict:
        """
        End the currently active project.

        Args:
            user_id (int): The ID of the user.
            project_name (str, optional): Specific project to end.
                If None, ends the currently active project.

        Returns:
            dict: Status information about the operation.

        Raises:
            ValueError: If no active project or project not found.
        """
        with self.db_manager.session() as session:
            user_repo = UserRepository(
                self.db_manager, User, session=session
            )
            project_repo = ProjectRepository(
                self.db_manager, Project, session=session
            )
            tracking_repo = TrackingRepository(
                self.db_manager, Tracking, session=session
            )

            # Check if user exists
            user = user_repo.get(user_id)
            if not user:
                raise ValueError("User not found")

            # Determine which project to end
            if project_name:
                project = project_repo.get_by_name(project_name, user_id)
                if not project:
                    raise ValueError(f"Project '{project_name}' not found")
                if not tracking_repo.is_project_active(user_id, project.id):
                    raise ValueError(
                        f"Project '{project_name}' is not active"
                    )
                project_id = project.id
            else:
                project_id = tracking_repo.get_active_project_id(user_id)
                if not project_id:
                    raise ValueError("No active project to end")
                project = project_repo.get(project_id)

            now = datetime.now(timezone.utc)

            # End the project
            tracking_repo.add({
                "user_id": user_id,
                "action": ActionType.PROJECT_END.value,
                "date_time": now,
                "project_id": project_id,
                "message": None
            })

            # Update user's last_active
            user_repo.update(user_id, {"last_active": now})

            return {
                "success": True,
                "message": f"Ended work on '{project.name}'",
                "timestamp": now,
                "project_id": project_id
            }

    def start_break(
        self,
        user_id: int,
        message: Optional[str] = None
    ) -> dict:
        """
        Start a break (pauses the current project).

        Args:
            user_id (int): The ID of the user.
            message (str, optional): A message/reason for the break.

        Returns:
            dict: Status information about the operation.

        Raises:
            ValueError: If no active project or break already active.
        """
        with self.db_manager.session() as session:
            user_repo = UserRepository(
                self.db_manager, User, session=session
            )
            tracking_repo = TrackingRepository(
                self.db_manager, Tracking, session=session
            )

            # Check if user exists
            user = user_repo.get(user_id)
            if not user:
                raise ValueError("User not found")

            # Check if there's an active project
            if not tracking_repo.is_any_project_active(user_id):
                raise ValueError("No active project to pause for break")

            # Check if break is already active
            if tracking_repo.is_break_active(user_id):
                raise ValueError("A break is already active")

            now = datetime.now(timezone.utc)

            # Start the break
            tracking_repo.add({
                "user_id": user_id,
                "action": ActionType.BREAK_START.value,
                "date_time": now,
                "project_id": None,
                "message": message
            })

            # Update user's last_active
            user_repo.update(user_id, {"last_active": now})

            return {
                "success": True,
                "message": "Break started",
                "timestamp": now
            }

    def end_break(self, user_id: int) -> dict:
        """
        End the current break (does not resume project automatically).

        Args:
            user_id (int): The ID of the user.

        Returns:
            dict: Status information about the operation.

        Raises:
            ValueError: If no active break.
        """
        with self.db_manager.session() as session:
            user_repo = UserRepository(
                self.db_manager, User, session=session
            )
            tracking_repo = TrackingRepository(
                self.db_manager, Tracking, session=session
            )

            # Check if user exists
            user = user_repo.get(user_id)
            if not user:
                raise ValueError("User not found")

            # Check if there's an active break
            if not tracking_repo.is_break_active(user_id):
                raise ValueError("No active break to end")

            now = datetime.now(timezone.utc)

            # End the break
            tracking_repo.add({
                "user_id": user_id,
                "action": ActionType.BREAK_END.value,
                "date_time": now,
                "project_id": None,
                "message": None
            })

            # Update user's last_active
            user_repo.update(user_id, {"last_active": now})

            return {
                "success": True,
                "message": "Break ended",
                "timestamp": now
            }

    def continue_project(self, user_id: int) -> dict:
        """
        Resume work on the project that was active before the break.

        Args:
            user_id (int): The ID of the user.

        Returns:
            dict: Status information about the operation.

        Raises:
            ValueError: If no recent project to resume or no active break.
        """
        with self.db_manager.session() as session:
            user_repo = UserRepository(
                self.db_manager, User, session=session
            )
            project_repo = ProjectRepository(
                self.db_manager, Project, session=session
            )
            tracking_repo = TrackingRepository(
                self.db_manager, Tracking, session=session
            )

            # Check if user exists
            user = user_repo.get(user_id)
            if not user:
                raise ValueError("User not found")

            # Check if there's an active break
            if not tracking_repo.is_break_active(user_id):
                raise ValueError("No active break to end")

            # Get the project to resume
            project_id = tracking_repo.get_last_project_before_break(user_id)
            if not project_id:
                raise ValueError("No recent project to resume")

            project = project_repo.get(project_id)
            if not project:
                raise ValueError("Previous project not found")

            now = datetime.now(timezone.utc)

            # End the break
            tracking_repo.add({
                "user_id": user_id,
                "action": ActionType.BREAK_END.value,
                "date_time": now,
                "project_id": None,
                "message": "Auto-ended for project resume"
            })

            # Resume the project
            tracking_repo.add({
                "user_id": user_id,
                "action": ActionType.PROJECT_RESUME.value,
                "date_time": now,
                "project_id": project_id,
                "message": None
            })

            # Update user's last_active
            user_repo.update(user_id, {"last_active": now})

            return {
                "success": True,
                "message": f"Resumed work on '{project.name}'",
                "timestamp": now,
                "project_id": project_id
            }
