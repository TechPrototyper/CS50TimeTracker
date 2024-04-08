from sqlmodel import SQLModel, Session, select
from .database_manager import DatabaseManager
from .sitr_models import User, Project, Tracking  # Angenommen, deine Modelle befinden sich in models.py
from typing import List, TypeVar, Generic, Type
from datetime import datetime

T = TypeVar('T', bound=SQLModel)

class BaseRepository(Generic[T]):
    def __init__(self, db_manager: DatabaseManager, model_class: Type[T]):
        self.db_manager = db_manager
        self.model_class = model_class

    def add(self, obj_data: dict) -> T:
        with self.db_manager.session() as session:
            obj = self.model_class(**obj_data)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    def get(self, obj_id: int) -> T:
        with self.db_manager.session() as session:
            obj = session.get(self.model_class, obj_id)
            return obj

    def get_all(self) -> List[T]:
        with self.db_manager.session() as session:
            result = session.exec(select(self.model_class)).all()
            return result

    def delete(self, obj_id: int) -> None:
        with self.db_manager.session() as session:
            obj = session.get(self.model_class, obj_id)
            session.delete(obj)
            session.commit()


class UserRepository(BaseRepository[User]):
    '''
    Hinzufügen und Verwalten von Benutzern:
    
    add(user_data: dict) -> User: Einen neuen Benutzer hinzufügen.
    get(user_id: int) -> User: Einen Benutzer anhand seiner ID abrufen.
    update(user_id: int, user_data: dict) -> User: Benutzerdaten aktualisieren.
    delete(user_id: int) -> None: Einen Benutzer löschen.
    get_all() -> List[User]: Liste aller Benutzer abrufen.

    '''

    pass # Implementierung der Methoden in abstrakter Basisklasse hinreichend

class ProjectRepository(BaseRepository[Project]):
    '''
    Verwalten von Projekten:

    add(project_data: dict) -> Project: Ein neues Projekt hinzufügen.
    get(project_id: int) -> Project: Ein Projekt anhand seiner ID abrufen.
    update(project_id: int, project_data: dict) -> Project: Projektdaten aktualisieren.
    delete(project_id: int) -> None: Ein Projekt löschen.
    get_all() -> List[Project]: Liste aller Projekte abrufen.
    get_active_projects() -> List[Project]: Liste aller aktiven (nicht archivierten) Projekte abrufen.

    '''
    def get_active_projects(self) -> List[Project]:
        with self.db_manager.session() as session:
            result = session.exec(select(Project).where(Project.state == "active")).all()
            return result

class TrackingRepository(BaseRepository[Tracking]):
    '''
    Tracking von Aktivitäten:

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
        with self.db_manager.session() as session:
            result = session.exec(
                select(Tracking).where(Tracking.project_id == project_id)
            ).all()
            return result

    def get_by_user(self, user_id: int) -> List[Tracking]:
        with self.db_manager.session() as session:
            result = session.exec(
                select(Tracking).where(Tracking.user_id == user_id)
            ).all()
            return result

    def get_trackings_in_time_range(self, start_date: datetime, end_date: datetime) -> List[Tracking]:
        with self.db_manager.session() as session:
            result = session.exec(
                select(Tracking)
                .where(Tracking.date_time >= start_date, Tracking.date_time < end_date)
            ).all()
            return result