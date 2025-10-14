#!/usr/bin/env python3
"""
SITR API Client

HTTP client for communicating with SITR API server.
Includes auto-start logic for seamless user experience.
"""
import requests
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from config_manager import get_config_manager
from server_manager import get_server_manager


class APIClient:
    """HTTP client for SITR API."""

    def __init__(self):
        """Initialize API client."""
        self.config = get_config_manager()
        self.server_manager = get_server_manager(
            host=self.config.get_server_host(),
            port=self.config.get_server_port()
        )
        self.base_url = self.config.get_api_url()
        self.timeout = 10  # seconds
        self.max_retries = 2

    def _ensure_server_running(self) -> bool:
        """
        Ensure server is running, start if needed.

        Returns:
            True if server is running, False otherwise
        """
        if self.server_manager.is_running():
            return True

        # Auto-start if enabled
        if self.config.get_auto_start_server():
            print("Starting SITR server...")
            success, msg = self.server_manager.start()
            if success:
                # Wait for server to be ready
                time.sleep(2)
                return self.server_manager.is_running()
            else:
                print(f"Failed to start server: {msg}")
                return False

        return False

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API with auto-retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters

        Returns:
            Response data

        Raises:
            Exception: If request fails after retries
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(self.max_retries):
            try:
                # Ensure server is running
                if not self._ensure_server_running():
                    raise ConnectionError("Server is not running")

                # Make request
                response = requests.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    timeout=self.timeout
                )

                # Check for errors
                if response.status_code >= 400:
                    error_detail = response.json().get("detail", "Unknown error")
                    raise ValueError(error_detail)

                return response.json()

            except requests.ConnectionError:
                if attempt < self.max_retries - 1:
                    # Try to restart server
                    print("Connection failed, restarting server...")
                    self.server_manager.restart()
                    time.sleep(2)
                else:
                    raise ConnectionError(
                        "Could not connect to server after retries"
                    )
            except requests.Timeout:
                raise TimeoutError(f"Request to {endpoint} timed out")

    # User Management Methods

    def create_user(
        self,
        firstname: str,
        lastname: str,
        email: str,
        middleinitial: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new user."""
        return self._make_request(
            "POST",
            "/api/users",
            data={
                "first_name": firstname,
                "last_name": lastname,
                "email": email,
                "middle_initial": middleinitial
            }
        )

    def list_users(self) -> List[Dict[str, Any]]:
        """Get all users."""
        return self._make_request("GET", "/api/users")

    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Get user by email."""
        return self._make_request("GET", f"/api/users/email/{email}")

    def update_user(
        self,
        email: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        middleinitial: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update user information."""
        data = {}
        if firstname is not None:
            data["first_name"] = firstname
        if lastname is not None:
            data["last_name"] = lastname
        if middleinitial is not None:
            data["middle_initial"] = middleinitial

        return self._make_request("PUT", f"/api/users/{email}", data=data)

    def delete_user(self, email: str) -> Dict[str, Any]:
        """Delete a user."""
        return self._make_request("DELETE", f"/api/users/{email}")

    def select_user(self, email: str) -> Dict[str, Any]:
        """Mark user as selected."""
        return self._make_request("POST", f"/api/users/select/{email}")

    # Workday Methods

    def start_day(self, user_id: int) -> Dict[str, Any]:
        """Start a new work day."""
        return self._make_request(
            "POST",
            "/api/workday/start",
            data={"user_id": user_id}
        )

    def end_day(self, user_id: int) -> Dict[str, Any]:
        """End the current work day."""
        return self._make_request(
            "POST",
            "/api/workday/end",
            data={"user_id": user_id}
        )

    # Project Tracking Methods

    def start_project(
        self,
        user_id: int,
        project_name: str,
        no_confirm: bool = False
    ) -> Dict[str, Any]:
        """Start working on a project."""
        return self._make_request(
            "POST",
            "/api/projects/start",
            data={
                "user_id": user_id,
                "project_name": project_name,
                "no_confirm": no_confirm
            }
        )

    def end_project(self, user_id: int, project_name: str) -> Dict[str, Any]:
        """End working on a project."""
        return self._make_request(
            "POST",
            "/api/projects/end",
            data={
                "user_id": user_id,
                "project_name": project_name
            }
        )

    # Break Methods

    def start_break(
        self,
        user_id: int,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a break."""
        return self._make_request(
            "POST",
            "/api/breaks/start",
            data={
                "user_id": user_id,
                "message": message
            }
        )

    def end_break(self, user_id: int) -> Dict[str, Any]:
        """End a break."""
        return self._make_request(
            "POST",
            "/api/breaks/end",
            data={"user_id": user_id}
        )

    def continue_project(self, user_id: int) -> Dict[str, Any]:
        """End break and resume previous project."""
        return self._make_request(
            "POST",
            "/api/projects/continue",
            data={"user_id": user_id}
        )

    # Project Management Methods

    def create_project(self, name: str, user_id: int) -> Dict[str, Any]:
        """Create a new project."""
        return self._make_request(
            "POST",
            "/api/projects",
            data={
                "name": name,
                "user_id": user_id
            }
        )

    def list_projects(
        self,
        user_id: int,
        include_archived: bool = False,
        sort_alphabetically: bool = False
    ) -> List[Dict[str, Any]]:
        """List projects for a user."""
        return self._make_request(
            "GET",
            "/api/projects",
            params={
                "user_id": user_id,
                "include_archived": include_archived,
                "sort_alphabetically": sort_alphabetically
            }
        )

    def archive_project(
        self,
        project_name: str,
        user_id: int,
        unarchive: bool = False
    ) -> Dict[str, Any]:
        """Archive or unarchive a project."""
        return self._make_request(
            "POST",
            "/api/projects/archive",
            data={
                "project_name": project_name,
                "user_id": user_id,
                "unarchive": unarchive
            }
        )


# Singleton instance
_api_client: Optional[APIClient] = None


def get_api_client() -> APIClient:
    """Get singleton API client instance."""
    global _api_client
    if _api_client is None:
        _api_client = APIClient()
    return _api_client
