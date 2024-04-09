from sqlmodel import SQLModel, Session, select
from database_manager import DatabaseManager
from sitr_models import User, Project, Tracking  # Angenommen, deine Modelle befinden sich in models.py
from typing import List, TypeVar, Generic, Type
from datetime import datetime

T = TypeVar('T', bound=SQLModel)

class BaseRepository(Generic[T]):
    """
    A base repository class that implements generic CRUD operations for any SQLModel entity.

    Attributes:
        db_manager (DatabaseManager): The database manager instance for database operations.
        model_class (Type[T]): The SQLModel class of the repository entity.
    """

    def __init__(self, db_manager: DatabaseManager, model_class: Type[T], session=None):
        """
        Initializes the base repository with a database manager and model class.

        Args:
            db_manager (DatabaseManager): The database manager to use.
            model_class (Type[T]): The model class of the entity.
        """

        self.db_manager = db_manager
        self.model_class = model_class
        self._session = session

    def _get_session(self):
        # create english docstring for this method

        if self._session is not None:
            return self._session
        else:
            return self.db_manager.session()
        
    def add(self, obj_data: dict) -> T:
        """
        Adds a new entity to the database.

        Args:
            obj_data (dict): The data for the entity to add.

        Returns:
            T: The added entity.
        """

        with self._get_session() as session:
            obj = self.model_class(**obj_data)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

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

    def delete(self, obj_id: int) -> None:
        """
        Deletes an entity by its ID.

        Args:
            obj_id (int): The ID of the entity to delete.
        """

        with self._get_session() as session:
            obj = session.get(self.model_class, obj_id)
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

    '''

    pass # Implementierung der Methoden in abstrakter Basisklasse hinreichend

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
    def get_active_projects(self) -> List[Project]:
        '''
        Retrieves all active (not archived) projects.

        Returns:
            List[Project]: A list of all active projects.
        '''

        with self._get_session() as session:
            result = session.exec(select(Project).where(Project.state == "active")).all()
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

    def get_trackings_in_time_range(self, start_date: datetime, end_date: datetime) -> List[Tracking]:
        '''
        Retrieves tracking entries within a specific time range.

        Args:
            start_date (datetime): The start date of the time range.
            end_date (datetime): The end date of the time range.

        Returns:
            List[Tracking]: A list of tracking entries within the specified time range.
        '''
        
        with self._get_session() as session:
            result = session.exec(
                select(Tracking)
                .where(Tracking.date_time >= start_date, Tracking.date_time < end_date)
            ).all()
            return result