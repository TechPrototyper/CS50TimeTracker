from sqlmodel import create_engine, Session, SQLModel
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None

    def create_engine(self):
        self.engine = create_engine(self.database_url, echo=True)

    def create_tables(self):
        if self.engine is None:
            raise ValueError("Engine ist nicht initialisiert.")
        SQLModel.metadata.create_all(self.engine)

    @contextmanager
    def session(self):
        session = Session(bind=self.engine)
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()