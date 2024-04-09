import pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from database_manager import DatabaseManager
from sitr_models import User, Project
from database_repositories import UserRepository, ProjectRepository

# Konfiguriere eine Testdatenbank (SQLite In-Memory)
# DATABASE_URL = "sqlite:///.myLocalDatabase.db"
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SQLModel.metadata.create_all(engine)

# Fixture für DatabaseManager
@pytest.fixture
def db_manager():
    db = DatabaseManager(DATABASE_URL)
    return db

# def db_session():
#     session = SessionLocal()
#     try:
#         yield session
#     finally:
#         session.close()


def test_user_project_operations(db_manager: db_manager):
    # UserRepository und ProjectRepository initialisieren

    db_manager.create_tables()

    test_session = Session(bind=engine, autocommit=False, autoflush=False)

    user_repo = UserRepository(db_manager=db_manager, model_class=User, session=test_session)
    project_repo = ProjectRepository(db_manager=db_manager, model_class=Project, session=test_session)

    for project in project_repo.get_all():
        print(f"Deleting project {project.id}..", end="")
        project_repo.delete(project.id)
        print(".")

    # _ = input("ENTER to continue")

    for user in user_repo.get_all():
        print(user.first_name, user.last_name, user.email)

    # _ = input("ENTER to continue")

    for user in user_repo.get_all():
        print(f"Deleting user {user.id}..", end="")
        user_repo.delete(user.id)
        print(".")

    # _ = input("ENTER to continue")


    user1 = user_repo.add({"first_name": "User1", "last_name": "Test1", "email": "user1@example.com"})
    user2 = user_repo.add({"first_name": "User2", "last_name": "Test2", "email": "user2@example.com"})
    user3 = user_repo.add({"first_name": "User3", "last_name": "Test3", "email": "user3@example.com"})

    # _ = input("ENTER to continue")


    # # Zwei User löschen
    user_repo.delete(user2.id)
    user_repo.delete(user3.id)

    # _ = input("ENTER to continue")



    # # Drei Projekte für den verbleibenden User anlegen
    project1 = project_repo.add({"name": "Project1", "user_id": user1.id})
    project2 = project_repo.add({"name": "Project2", "user_id": user1.id})
    project3 = project_repo.add({"name": "Project3", "user_id": user1.id})

    # _ = input("ENTER to continue")


    # # Ein Projekt löschen
    project_repo.delete(project2.id)

    # _ = input("ENTER to continue")


    # # Assertions, um zu überprüfen, ob die Operationen wie erwartet funktioniert haben
    assert len(user_repo.get_all()) == 1
    assert user_repo.get(user1.id).first_name == "User1"
    assert len(project_repo.get_all()) == 2
    assert project_repo.get(project1.id).name == "Project1"

    # Ausgabe zur Verifizierung
    print("Verbleibende User:", user_repo.get_all())
    print("Projekte des verbleibenden Users:", project_repo.get_all())
