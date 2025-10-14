from sitr_models import User, Project, Tracking
from database_manager import DatabaseManager

db=DatabaseManager("sqlite:///.myLocalDatabase.db")
db.create_tables()



