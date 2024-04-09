import pytest
from sqlmodel import SQLModel, create_engine
from database_manager import DatabaseManager
from sitr_models import User, Project
from database_repositories import UserRepository, ProjectRepository

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, echo=True)
SQLModel.metadata.create_all(engine)

@pytest.fixture
def db_manager():
    return DatabaseManager(DATABASE_URL)

def test_user_project_operations(db_manager):
    db_manager.engine = engine  # Stelle sicher, dass der Engine gesetzt ist
    with db_manager.session() as session:
        # UserRepository und ProjectRepository mit db_manager und session initialisieren
        user_repo = UserRepository(db_manager=db_manager, model_class=User)
        project_repo = ProjectRepository(db_manager=db_manager, model_class=Project)

        # Drei User anlegen
        user1 = user_repo.add({"first_name": "User1", "last_name": "Test1", "email": "user1@example.com"}, session=session)
        user2 = user_repo.add({"first_name": "User2", "last_name": "Test2", "email": "user2@example.com"}, session=session)
        user3 = user_repo.add({"first_name": "User3", "last_name": "Test3", "email": "user3@example.com"}, session=session)

        # Zwei User löschen
        user_repo.delete(user2.id, session=session)
        user_repo.delete(user3.id, session=session)

        # Drei Projekte für den verbleibenden User anlegen
        project1 = project_repo.add({"name": "Project1", "user_id": user1.id}, session=session)
        project2 = project_repo.add({"name": "Project2", "user_id": user1.id}, session=session)
        project3 = project_repo.add({"name": "Project3", "user_id": user1.id}, session=session)

        # Ein Projekt löschen
        project_repo.delete(project2.id, session=session)

        # Assertions, um zu überprüfen, ob die Operationen wie erwartet funktioniert haben
        assert len(user_repo.get_all(session=session)) == 1
        assert user_repo.get(user1.id, session=session).first_name == "User1"
        assert len(project_repo.get_all(session=session)) == 2
        assert project_repo.get(project1.id, session=session).name == "Project1"
