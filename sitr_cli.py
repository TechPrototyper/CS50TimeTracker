#!/usr/bin/env python3
"""
SITR - Simple Time Tracker CLI

A command-line interface for tracking time spent on projects.
"""
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from datetime import datetime

from api_client import get_api_client
from config_manager import get_config_manager
from server_manager import get_server_manager

app = typer.Typer(
    name="sitr",
    help="""Simple Time Tracker (SITR) - Track your work time efficiently.

    \b
    Quick Start:
      1. Add a user:        sitr user add -f Tim -l Walter -e tim@example.com
      2. Select user:       sitr user select -e tim@example.com
      3. Start your day:    sitr start-day
      4. Work on project:   sitr start "My Project"
      5. Take a break:      sitr break start
      6. Resume work:       sitr continue
      7. End your day:      sitr end-day
    
    \b
    Features:
      • Automatic project switching (handover logic)
      • Break management with project resume
      • Auto-cleanup when ending day
      • Rich terminal output with colors
    
    \b
    For detailed help on any command, use:
      sitr COMMAND --help
    """,
    epilog="Made with ❤️  for efficient time tracking",
    no_args_is_help=True
)
console = Console()

# Initialize global singletons
api_client = None
config = None


def get_client():
    """Get API client instance."""
    global api_client
    if api_client is None:
        api_client = get_api_client()
    return api_client


def get_config():
    """Get config manager instance."""
    global config
    if config is None:
        config = get_config_manager()
    return config


def get_current_user_id() -> int:
    """Get current user ID from config."""
    user_id = get_config().get_current_user_id()
    if user_id is None:
        console.print(
            "[yellow]No user selected. Please use 'sitr user select'"
            " to choose a user.[/yellow]"
        )
        raise typer.Exit(1)
    return user_id


def set_current_user_id(user_id: int):
    """Save current user ID to config."""
    get_config().set_current_user_id(user_id)


# Server management commands
server_app = typer.Typer(help="Manage the SITR API server")
app.add_typer(server_app, name="server")


@server_app.command("start")
def server_start():
    """Start the SITR API server."""
    server_mgr = get_server_manager(
        host=get_config().get_server_host(),
        port=get_config().get_server_port()
    )
    
    success, msg = server_mgr.start()
    if success:
        console.print(f"[green]✓[/green] {msg}")
    else:
        console.print(f"[red]Error:[/red] {msg}")
        raise typer.Exit(1)


@server_app.command("stop")
def server_stop():
    """Stop the SITR API server."""
    server_mgr = get_server_manager(
        host=get_config().get_server_host(),
        port=get_config().get_server_port()
    )
    
    success, msg = server_mgr.stop()
    if success:
        console.print(f"[green]✓[/green] {msg}")
    else:
        console.print(f"[yellow]Note:[/yellow] {msg}")


@server_app.command("status")
def server_status():
    """Check if the SITR API server is running."""
    server_mgr = get_server_manager(
        host=get_config().get_server_host(),
        port=get_config().get_server_port()
    )
    
    is_running, msg = server_mgr.status()
    if is_running:
        console.print(f"[green]✓[/green] {msg}")
    else:
        console.print(f"[yellow]ℹ[/yellow] {msg}")


@server_app.command("restart")
def server_restart():
    """Restart the SITR API server."""
    server_mgr = get_server_manager(
        host=get_config().get_server_host(),
        port=get_config().get_server_port()
    )
    
    success, msg = server_mgr.restart()
    if success:
        console.print(f"[green]✓[/green] {msg}")
    else:
        console.print(f"[red]Error:[/red] {msg}")
        raise typer.Exit(1)


@server_app.command("logs")
def server_logs(
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines")
):
    """Show server logs."""
    server_mgr = get_server_manager(
        host=get_config().get_server_host(),
        port=get_config().get_server_port()
    )
    
    logs = server_mgr.get_logs(lines)
    console.print(logs)


# User management commands
user_app = typer.Typer(
    help="""Manage users for time tracking.
    
    \b
    Users are identified by their email address. You must select
    an active user before tracking time.
    
    \b
    Examples:
      sitr user add -f John -l Doe -e john@example.com
      sitr user select -e john@example.com
      sitr user list
    """
)
app.add_typer(user_app, name="user")


@user_app.command("add", help="Create a new user for time tracking")
def add_user(
    firstname: str = typer.Option(
        ..., "--firstname", "-f", help="First name"),
    lastname: str = typer.Option(
        ..., "--lastname", "-l", help="Last name"),
    email: str = typer.Option(
        ..., "--email", "-e", help="Email address (unique identifier)")
):
    """Add a new user."""
    client = get_client()

    try:
        user = client.create_user(
            firstname=firstname,
            lastname=lastname,
            email=email
        )
        console.print(
            f"[green]✓[/green] User {user['first_name']} "
            f"{user['last_name']} ({user['email']}) created."
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@user_app.command("list", help="Show all registered users")
def list_users():
    """List all users."""
    client = get_client()

    users = client.list_users()
    if not users:
        console.print("[yellow]No users found.[/yellow]")
        return

    table = Table(title="Users")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Email", style="blue")

    for user in users:
        name = f"{user['first_name']}"
        if user.get('middle_initial'):
            name += f" {user['middle_initial']}."
        name += f" {user['last_name']}"
        table.add_row(str(user['id']), name, user['email'])

    console.print(table)


@user_app.command(
    "select",
    help="Set the active user for time tracking (required before tracking)"
)
def select_user(
    email: str = typer.Option(..., "--email", "-e", help="Email address")
):
    """Select the active user."""
    client = get_client()

    try:
        result = client.select_user(email)
        user_id = result['user_id']
        set_current_user_id(user_id)
        
        # Also store email in config
        get_config().set_current_user_email(email)
        
        console.print(
            f"[green]✓[/green] Selected user: {email}"
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@user_app.command(
    "delete",
    help="Remove a user (WARNING: This deletes all their tracking data!)"
)
def delete_user(
    email: str = typer.Option(..., "--email", "-e", help="Email address")
):
    """Delete a user."""
    client = get_client()

    try:
        result = client.delete_user(email)
        console.print(f"[green]✓[/green] {result['message']}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


# Workday commands
@app.command("start-day", help="""Start a new work day.
    
    \b
    This command begins time tracking for the day. You must start a day
    before you can track projects or breaks. Only one day can be open
    at a time.
    
    \b
    Workflow:
      1. Start day       -> sitr start-day
      2. Work on project -> sitr start "My Project"
      3. Take break      -> sitr break start "Coffee"
      4. Continue work   -> sitr continue
      5. End day         -> sitr end-day
    """)
def start_day():
    """Start your workday."""
    user_id = get_current_user_id()
    client = get_client()

    try:
        result = client.start_day(user_id)
        timestamp = datetime.fromisoformat(result['timestamp'])
        console.print(
            f"[green]✓[/green] {result['message']} at "
            f"{timestamp.strftime('%H:%M')}"
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("end-day", help="""End your work day.
    
    \b
    Automatically closes any active projects and breaks, then marks
    the day as complete. All tracking data is saved.
    """)
def end_day():
    """End your workday."""
    user_id = get_current_user_id()
    client = get_client()

    try:
        result = client.end_day(user_id)
        timestamp = datetime.fromisoformat(result['timestamp'])
        console.print(
            f"[green]✓[/green] {result['message']} at "
            f"{timestamp.strftime('%H:%M')}"
        )
        if result.get('data', {}).get('closed_project'):
            console.print(
                "[yellow]Note:[/yellow] Active project was auto-closed."
            )
        if result.get('data', {}).get('closed_break'):
            console.print(
                "[yellow]Note:[/yellow] Active break was auto-closed."
            )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


# Project commands
@app.command("start", help="""Start working on a project.
    
    \b
    Automatically ends any currently active project (handover).
    Also ends active breaks. The project will be created if it
    doesn't exist yet.
    
    \b
    Example:
      sitr start "Write Documentation"
      sitr start "Bug Fixes" --noconf
    """)
def start_project(
    project: str = typer.Argument(..., help="Project name"),
    no_confirm: bool = typer.Option(
        False,
        "--noconf",
        help="Don't ask for confirmation when ending active project"
    )
):
    """Start working on a project."""
    user_id = get_current_user_id()
    client = get_client()

    try:
        result = client.start_project(user_id, project, no_confirm)
        timestamp = datetime.fromisoformat(result['timestamp'])
        console.print(
            f"[green]✓[/green] {result['message']} at "
            f"{timestamp.strftime('%H:%M')}"
        )
        if result.get('data', {}).get('previous_project'):
            console.print(
                "[yellow]Note:[/yellow] Previous project was auto-ended."
            )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("end", help="""End working on a project.
    
    \b
    Stops time tracking for the specified project. The project must
    be currently active.
    
    \b
    Example:
      sitr end "Write Documentation"
    """)
def end_project(
    project: str = typer.Argument(..., help="Project name")
):
    """End working on a project."""
    user_id = get_current_user_id()
    client = get_client()

    try:
        result = client.end_project(user_id, project)
        timestamp = datetime.fromisoformat(result['timestamp'])
        console.print(
            f"[green]✓[/green] {result['message']} at "
            f"{timestamp.strftime('%H:%M')}"
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


# Break commands
break_app = typer.Typer(
    help="""Manage breaks during your workday.
    
    \b
    Breaks pause project work. Use 'continue' to resume your last
    project after a break.
    
    \b
    Examples:
      sitr break start "Lunch"
      sitr break end
      sitr continue
    """
)
app.add_typer(break_app, name="break")


@break_app.command("start", help="""Start a break.
    
    \b
    Pauses any active project work. You can optionally specify a
    reason for the break.
    
    \b
    Example:
      sitr break start -m "Lunch"
      sitr break start --message "Coffee"
    """)
def break_start(
    message: Optional[str] = typer.Option(
        None,
        "--message",
        "-m",
        help="Reason for break (e.g., 'Lunch', 'Coffee')"
    )
):
    """Start a break."""
    user_id = get_current_user_id()
    client = get_client()

    try:
        result = client.start_break(user_id, message)
        timestamp = datetime.fromisoformat(result['timestamp'])
        console.print(
            f"[green]✓[/green] {result['message']} at "
            f"{timestamp.strftime('%H:%M')}"
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@break_app.command("end", help="""End a break without resuming work.
    
    \b
    Stops the break timer but does NOT automatically resume project
    work. Use 'sitr continue' if you want to resume your last project.
    """)
def break_end():
    """End a break (use 'continue' to also resume project)."""
    user_id = get_current_user_id()
    client = get_client()

    try:
        result = client.end_break(user_id)
        timestamp = datetime.fromisoformat(result['timestamp'])
        console.print(
            f"[green]✓[/green] {result['message']} at "
            f"{timestamp.strftime('%H:%M')}"
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("continue", help="""End break and resume previous project.
    
    \b
    Automatically ends the current break and resumes the project you
    were working on before the break started. This is the recommended
    way to return to work after a break.
    
    \b
    Example:
      sitr start "Write Code"
      sitr break start "Lunch"
      sitr continue                # Resumes "Write Code"
    """)
def continue_project():
    """End break and resume previous project."""
    user_id = get_current_user_id()
    client = get_client()

    try:
        result = client.continue_project(user_id)
        timestamp = datetime.fromisoformat(result['timestamp'])
        console.print(
            f"[green]✓[/green] {result['message']} at "
            f"{timestamp.strftime('%H:%M')}"
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


# Project management commands
project_app = typer.Typer(
    help="""Manage your projects (add, archive, list).
    
    \b
    Projects can be created on-the-fly with 'sitr start', or
    pre-created with 'sitr project add'. Use 'archive' to hide
    completed projects from the active list.
    
    \b
    Examples:
      sitr project add -n "New Feature"
      sitr project archive -n "Old Project"
      sitr projects
    """
)
app.add_typer(project_app, name="project")


@project_app.command("add", help="Create a new project (optional)")
def project_add(
    name: str = typer.Option(..., "--name", "-n", help="Project name")
):
    """Add a new project."""
    user_id = get_current_user_id()
    client = get_client()

    try:
        project = client.create_project(name, user_id)
        console.print(f"[green]✓[/green] Project '{project['name']}' created.")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@project_app.command("archive", help="""Archive or restore a project.
    
    \b
    Archived projects are hidden from the active list but remain
    in the database with all their tracking history.
    
    \b
    Examples:
      sitr project archive -n "Old Project"
      sitr project archive -n "Old Project" --unarchive
    """)
def project_archive(
    name: str = typer.Option(..., "--name", "-n", help="Project name"),
    unarchive: bool = typer.Option(
        False, "--unarchive", help="Restore archived project")
):
    """Archive or unarchive a project."""
    user_id = get_current_user_id()
    client = get_client()

    try:
        result = client.archive_project(name, user_id, unarchive)
        console.print(f"[green]✓[/green] {result['message']}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("projects", help="""List all your projects.
    
    \b
    By default, shows only active projects sorted by creation date.
    Use --all to include archived projects, or --alphabet for
    alphabetical sorting.
    
    \b
    Examples:
      sitr projects
      sitr projects --all
      sitr projects --alphabet
    """)
def list_projects(
    alphabet: bool = typer.Option(
        False,
        "--alphabet",
        help="Sort alphabetically"
    ),
    all_projects: bool = typer.Option(
        False,
        "--all",
        help="Include archived projects"
    )
):
    """List all projects."""
    user_id = get_current_user_id()
    client = get_client()

    try:
        projects = client.list_projects(
            user_id,
            include_archived=all_projects,
            sort_alphabetically=alphabet
        )

        if not projects:
            console.print("[yellow]No projects found.[/yellow]")
            return

        table = Table(title="Projects")
        table.add_column("Name", style="green")
        table.add_column("State", style="cyan")
        table.add_column("Created", style="yellow")

        for project in projects:
            created = datetime.fromisoformat(project['created_at'])
            table.add_row(
                project['name'],
                project['state'],
                created.strftime('%Y-%m-%d')
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
