from sqlmodel import SQLModel, Session, select
from database_manager import DatabaseManager
from sitr_models import User, Project, Tracking
from typing import List, TypeVar, Generic, Type, Optional
from datetime import datetime, timezone

T = TypeVar('T', bound=SQLModel)

class BaseRepository(Generic[T]):
    """
    A base repository class that implements generic CRUD operations for any SQLModel entity.

    Attributes:
        db_manager (DatabaseManager): The database manager instance for database operations.
        model_class (Type[T]): The SQLModel class of the repository entity.
    """

    def __init__(
        self,
        db_manager: DatabaseManager,
        model_class: Type[T],
        session: Session = None
    ):
        """
        Initializes the base repository with a database manager
        and model class.

        Args:
            db_manager (DatabaseManager): The database manager to use.
            model_class (Type[T]): The model class of the entity.
            session (Session): Optional session for transactional operations.
        """
        self.db_manager = db_manager
        self.model_class = model_class
        self._session = session

    def _get_session(self):
        """
        Returns a session context manager for database operations.

        If an explicit session was provided during initialization,
        it will be wrapped in a simple context manager that doesn't
        commit or close automatically (for transactional control).
        Otherwise, returns the database manager's session context.

        Returns:
            Context manager yielding a Session.
        """
        from contextlib import contextmanager

        if self._session is not None:
            # Use provided session without auto-commit
            @contextmanager
            def provided_session():
                yield self._session
            return provided_session()
        else:
            # Use database manager's session with auto-commit
            return self.db_manager.session()
        
    def add(self, obj_data: dict) -> T:
        """
        Adds a new entity to the database.

        Args:
            obj_data (dict): The data for the entity to add.

        Returns:
            T: The added entity with id set.
        """
        with self._get_session() as session:
            obj = self.model_class(**obj_data)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            
            # Make a simple dict copy to avoid detached instance errors
            result_data = {
                c.name: getattr(obj, c.name)
                for c in obj.__table__.columns
            }
        
        # Create a new instance from the data
        return self.model_class(**result_data)

    def get(self, obj_id: int) -> T:
        """
        Retrieves an entity by its ID.

        Args:
            obj_id (int): The ID of the entity to retrieve.

        Returns:
            T: The entity with the specified ID.
        """

        with self._get_session() as session:
            obj = session.get(self.model_class, obj_id)
            return obj

    def get_all(self) -> List[T]:
        """
        Retrieves all entities of the repository's model class.

        Returns:
            List[T]: A list of all entities.
        """

        with self._get_session() as session:
            result = session.exec(select(self.model_class)).all()
            return result

    def update(self, obj_id: int, obj_data: dict) -> T:
        """
        Updates an entity with the provided data.

        Args:
            obj_id (int): The ID of the entity to update.
            obj_data (dict): The data to update on the entity.

        Returns:
            T: The updated entity.
        """
        with self._get_session() as session:
            obj = session.get(self.model_class, obj_id)
            if obj is None:
                raise ValueError(
                    f"{self.model_class.__name__} with id {obj_id} not found"
                )
            for key, value in obj_data.items():
                setattr(obj, key, value)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    def delete(self, obj_id: int) -> None:
        """
        Deletes an entity by its ID.

        Args:
            obj_id (int): The ID of the entity to delete.
        """
        with self._get_session() as session:
            obj = session.get(self.model_class, obj_id)
            if obj is None:
                raise ValueError(
                    f"{self.model_class.__name__} with id {obj_id} not found"
                )
            session.delete(obj)
            session.commit()


class UserRepository(BaseRepository[User]):
    '''
    Repository for User entities, implementing custom operations for users.
    Inherits generic CRUD operations from BaseRepository.

    List of operations:

    add(user_data: dict) -> User: Einen neuen Benutzer hinzufügen.
    get(user_id: int) -> User: Einen Benutzer anhand seiner ID abrufen.
    update(user_id: int, user_data: dict) -> User: Benutzerdaten aktualisieren.
    delete(user_id: int) -> None: Einen Benutzer löschen.
    get_all() -> List[User]: Liste aller Benutzer abrufen.
    get_by_email(email: str) -> User | None: Benutzer anhand der E-Mail abrufen.

    '''

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User if found, None otherwise
        """
        with self._get_session() as session:
            result = session.query(User).filter(User.email == email).first()
            return result
    
    def get_active_users(self) -> List[User]:
        """
        Get all active (non-archived) users.
        
        Returns:
            List of active users
        """
        with self._get_session() as session:
            result = session.query(User).filter(User.active == True).all()
            return result
    
    def archive_user(self, user_id: int) -> User:
        """
        Archive/deactivate a user (soft delete).
        
        Args:
            user_id: ID of user to archive
            
        Returns:
            Updated user object
        """
        with self._get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.active = False
                user.archived_at = datetime.now(timezone.utc)
                session.commit()
                session.refresh(user)
            return user
    
    def restore_user(self, user_id: int) -> User:
        """
        Restore/reactivate an archived user.
        
        Args:
            user_id: ID of user to restore
            
        Returns:
            Updated user object
        """
        with self._get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.active = True
                user.archived_at = None
                session.commit()
                session.refresh(user)
            return user


class ProjectRepository(BaseRepository[Project]):
    '''
    Repository for Project entities, implementing custom operations for projects.
    Inherits generic CRUD operations from BaseRepository.

    List of operations:

    add(project_data: dict) -> Project: Ein neues Projekt hinzufügen.
    get(project_id: int) -> Project: Ein Projekt anhand seiner ID abrufen.
    update(project_id: int, project_data: dict) -> Project: Projektdaten aktualisieren.
    delete(project_id: int) -> None: Ein Projekt löschen.
    get_all() -> List[Project]: Liste aller Projekte abrufen.
    get_active_projects() -> List[Project]: Liste aller aktiven (nicht archivierten) Projekte abrufen.

    '''
    def get_active_projects(
        self,
        user_id: Optional[int] = None
    ) -> List[Project]:
        '''
        Retrieves all active (not archived) projects.

        Args:
            user_id (int, optional): Filter by user ID. If None, returns all.

        Returns:
            List[Project]: A list of all active projects.
        '''
        from enums import ProjectState

        with self._get_session() as session:
            query = select(Project).where(
                Project.state == ProjectState.ACTIVE.value
            )
            if user_id is not None:
                query = query.where(Project.user_id == user_id)
            result = session.exec(query).all()
            return result

    def get_by_name(
        self,
        project_name: str,
        user_id: Optional[int] = None
    ) -> Project:
        '''
        Retrieves a project by its name.

        Args:
            project_name (str): The name of the project.
            user_id (int, optional): Filter by user ID. If None, searches all.

        Returns:
            Project | None: The project if found, None otherwise.
        '''
        with self._get_session() as session:
            query = select(Project).where(Project.name == project_name)
            if user_id is not None:
                query = query.where(Project.user_id == user_id)
            result = session.exec(query).first()
            return result


class TrackingRepository(BaseRepository[Tracking]):
    '''
    Repository for Tracking entries, implementing custom operations for tracking activities.
    Inherits generic CRUD operations from BaseRepository.

    List of operations:

    add(tracking_data: dict) -> Tracking: Ein neues Tracking-Ereignis hinzufügen.
    get(tracking_id: int) -> Tracking: Ein Tracking-Ereignis anhand seiner ID abrufen.
    update(tracking_id: int, tracking_data: dict) -> Tracking: Tracking-Daten aktualisieren.
    delete(tracking_id: int) -> None: Ein Tracking-Ereignis löschen.
    get_all() -> List[Tracking]: Liste aller Tracking-Einträge abrufen.
    get_by_project(project_id: int) -> List[Tracking]: Liste aller Tracking-Einträge für ein spezifisches Projekt abrufen.
    get_by_user(user_id: int) -> List[Tracking]: Liste aller Tracking-Einträge für einen spezifischen Benutzer abrufen.
    get_trackings_in_time_range(start_date: datetime, end_date: datetime) -> List[Tracking]: Tracking-Einträge in einem spezifischen Zeitraum abrufen.

    '''
    
    def get_by_project(self, project_id: int) -> List[Tracking]:
        '''
        Retrieves all tracking entries for a specific project.

        Args:
            project_id (int): The ID of the project for which to retrieve tracking entries.

        Returns:
            List[Tracking]: A list of tracking entries for the specified project.
        '''
        
        with self._get_session() as session:
            result = session.exec(
                select(Tracking).where(Tracking.project_id == project_id)
            ).all()
            return result

    def get_by_user(self, user_id: int) -> List[Tracking]:
        '''
        Retrieves all tracking entries for a specific user.

        Args:
            user_id (int): The ID of the user for which to retrieve tracking entries.

        Returns:
            List[Tracking]: A list of tracking entries for the specified user.
        '''

        with self._get_session() as session:
            result = session.exec(
                select(Tracking).where(Tracking.user_id == user_id)
            ).all()
            return result

    def get_trackings_in_time_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Tracking]:
        '''
        Retrieves tracking entries within a specific time range.

        Args:
            start_date (datetime): The start date of the time range.
            end_date (datetime): The end date of the time range.

        Returns:
            List[Tracking]: A list of tracking entries within
                the specified time range.
        '''
        with self._get_session() as session:
            result = session.exec(
                select(Tracking)
                .where(
                    Tracking.date_time >= start_date,
                    Tracking.date_time < end_date
                )
            ).all()
            return result

    def has_open_day(self, user_id: int) -> bool:
        '''
        Checks if the user has an open workday (started but not ended).

        Args:
            user_id (int): The ID of the user.

        Returns:
            bool: True if there's an open workday, False otherwise.
        '''
        from enums import ActionType

        with self._get_session() as session:
            # Get last workday action for this user
            last_workday_action = session.exec(
                select(Tracking)
                .where(
                    Tracking.user_id == user_id,
                    Tracking.action.in_([
                        ActionType.WORKDAY_START.value,
                        ActionType.WORKDAY_END.value
                    ])
                )
                .order_by(Tracking.date_time.desc())
            ).first()

            if last_workday_action is None:
                return False

            return last_workday_action.action == ActionType.WORKDAY_START.value

    def is_any_project_active(self, user_id: int) -> bool:
        '''
        Checks if any project is currently active for the user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            bool: True if any project is active, False otherwise.
        '''
        from enums import ActionType

        with self._get_session() as session:
            # Get last project-related action
            last_project_action = session.exec(
                select(Tracking)
                .where(
                    Tracking.user_id == user_id,
                    Tracking.project_id.isnot(None),
                    Tracking.action.in_([
                        ActionType.PROJECT_START.value,
                        ActionType.PROJECT_END.value,
                        ActionType.PROJECT_RESUME.value
                    ])
                )
                .order_by(Tracking.date_time.desc())
            ).first()

            if last_project_action is None:
                return False

            return last_project_action.action in [
                ActionType.PROJECT_START.value,
                ActionType.PROJECT_RESUME.value
            ]

    def is_project_active(self, user_id: int, project_id: int) -> bool:
        '''
        Checks if a specific project is currently active for the user.

        Args:
            user_id (int): The ID of the user.
            project_id (int): The ID of the project.

        Returns:
            bool: True if the project is active, False otherwise.
        '''
        from enums import ActionType

        with self._get_session() as session:
            # Get last action for this specific project
            last_action = session.exec(
                select(Tracking)
                .where(
                    Tracking.user_id == user_id,
                    Tracking.project_id == project_id,
                    Tracking.action.in_([
                        ActionType.PROJECT_START.value,
                        ActionType.PROJECT_END.value,
                        ActionType.PROJECT_RESUME.value
                    ])
                )
                .order_by(Tracking.date_time.desc())
            ).first()

            if last_action is None:
                return False

            return last_action.action in [
                ActionType.PROJECT_START.value,
                ActionType.PROJECT_RESUME.value
            ]

    def get_active_project_id(self, user_id: int) -> int | None:
        '''
        Returns the ID of the currently active project for the user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            int | None: The ID of the active project, or None if no
                project is active.
        '''
        from enums import ActionType

        with self._get_session() as session:
            # Get last project-related action
            last_project_action = session.exec(
                select(Tracking)
                .where(
                    Tracking.user_id == user_id,
                    Tracking.project_id.isnot(None),
                    Tracking.action.in_([
                        ActionType.PROJECT_START.value,
                        ActionType.PROJECT_END.value,
                        ActionType.PROJECT_RESUME.value
                    ])
                )
                .order_by(Tracking.date_time.desc())
            ).first()

            if last_project_action is None:
                return None

            if last_project_action.action in [
                ActionType.PROJECT_START.value,
                ActionType.PROJECT_RESUME.value
            ]:
                return last_project_action.project_id

            return None

    def get_last_project_before_break(self, user_id: int) -> int | None:
        '''
        Gets the project ID that was active before the current break started.

        Args:
            user_id (int): The ID of the user.

        Returns:
            int | None: The project ID, or None if no suitable project found.
        '''
        from enums import ActionType

        with self._get_session() as session:
            # First, check if there's an active break
            last_break_action = session.exec(
                select(Tracking)
                .where(
                    Tracking.user_id == user_id,
                    Tracking.action.in_([
                        ActionType.BREAK_START.value,
                        ActionType.BREAK_END.value
                    ])
                )
                .order_by(Tracking.date_time.desc())
            ).first()

            if (last_break_action is None or
                    last_break_action.action != ActionType.BREAK_START.value):
                return None

            # Find the last project that was active before this break
            last_project_before_break = session.exec(
                select(Tracking)
                .where(
                    Tracking.user_id == user_id,
                    Tracking.project_id.isnot(None),
                    Tracking.date_time < last_break_action.date_time,
                    Tracking.action.in_([
                        ActionType.PROJECT_START.value,
                        ActionType.PROJECT_RESUME.value
                    ])
                )
                .order_by(Tracking.date_time.desc())
            ).first()

            if last_project_before_break:
                return last_project_before_break.project_id

            return None

    def is_break_active(self, user_id: int) -> bool:
        '''
        Checks if a break is currently active for the user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            bool: True if a break is active, False otherwise.
        '''
        from enums import ActionType

        with self._get_session() as session:
            # Get last break action
            last_break_action = session.exec(
                select(Tracking)
                .where(
                    Tracking.user_id == user_id,
                    Tracking.action.in_([
                        ActionType.BREAK_START.value,
                        ActionType.BREAK_END.value
                    ])
                )
                .order_by(Tracking.date_time.desc())
            ).first()

            if last_break_action is None:
                return False

            return last_break_action.action == ActionType.BREAK_START.value
