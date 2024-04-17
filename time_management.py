from datetime import datetime

class TimeManagement:
    def __init__(self, tracking_repository, project_repository, user_repository):
        self.tracking_repository = tracking_repository
        self.project_repository = project_repository
        self.user_repository = user_repository

    def start_day(self, user_id):
        # Überprüfung, ob der Benutzer existiert
        user = self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Überprüfung, ob bereits ein offener Tag existiert
        if self.tracking_repository.has_open_day(user_id):
            raise ValueError("The workday has already started")
        
        # Erstellung eines Tracking-Eintrags für den Start des Tages
        self.tracking_repository.add({
            "user_id": user_id,
            "action": "Workday starts",
            "date_time": datetime.now(),
            "project_id": None,
            "message": None
        })

    def end_day(self, user_id):
        # Überprüfung, ob der Benutzer existiert und ob ein Tag offen ist
        if not self.user_repository.get(user_id):
            raise ValueError("User not found")
        
        if not self.tracking_repository.has_open_day(user_id):
            raise ValueError("No open workday to end")

        # Abschluss des Tages
        self.tracking_repository.add({
            "user_id": user_id,
            "action": "Workday ends",
            "date_time": datetime.now(),
            "project_id": None,
            "message": None
        })

        # Schließen aller offenen Projekte
        open_projects = self.project_repository.get_active_projects(user_id)
        for project in open_projects:
            self.end_project(user_id, project.id)

    def start_project(self, user_id, project_name):
        # Überprüfung, ob der Benutzer existiert
        if not self.user_repository.get(user_id):
            raise ValueError("User not found")

        # Suche oder erstelle das Projekt
        project = self.project_repository.get_by_name(project_name)
        if not project:
            project = self.project_repository.add({"name": project_name, "user_id": user_id})

        # Überprüfung, ob bereits ein Projekt aktiv ist
        if self.tracking_repository.is_project_active(user_id):
            raise ValueError("Another project is already active")

        # Starten des Projekts
        self.tracking_repository.add({
            "user_id": user_id,
            "action": "Project starts",
            "date_time": datetime.now(),
            "project_id": project.id,
            "message": None
        })

    def end_project(self, user_id, project_id):
        # Stelle sicher, dass das Projekt existiert und offen ist
        project = self.project_repository.get(project_id)
        if not project or not self.tracking_repository.is_project_active(user_id, project_id):
            raise ValueError("Project is not active or does not exist")

        # Beende das Projekt
        self.tracking_repository.add({
            "user_id": user_id,
            "action": "Project ends",
            "date_time": datetime.now(),
            "project_id": project_id,
            "message": None
        })

    def start_break(self, user_id: int, message: str = None):
        if not self.tracking_repository.is_any_project_active(user_id):
            raise ValueError("No active project to pause")
        self.tracking_repository.add({
            "user_id": user_id,
            "action": "Break starts",
            "date_time": datetime.now(),
            "project_id": None,
            "message": message
        })

    def end_break(self, user_id: int):
        if not self.tracking_repository.is_break_active(user_id):
            raise ValueError("No active break to end")
        self.tracking_repository.add({
            "user_id": user_id,
            "action": "Break ends",
            "date_time": datetime.now(),
            "project_id": None,
            "message": None
        })

    def continue_project(self, user_id: int):
        last_project = self.tracking_repository.get_last_project_before_break(user_id)
        if not last_project:
            raise ValueError("No recent project to resume")
        self.tracking_repository.add({
            "user_id": user_id,
            "action": "Project resumes",
            "date_time": datetime.now(),
            "project_id": last_project.id,
            "message": None
        })

