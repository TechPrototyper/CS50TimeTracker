#!/usr/bin/env python3
"""
SITR - Simple Time Tracker CLI

A command-line interface for tracking time spent on projects.
"""
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from datetime import datetime, timezone

from api_client import get_api_client
from config_manager import get_config_manager
from server_manager import get_server_manager


def utc_to_local(utc_dt_str: str) -> datetime:
    """Convert UTC datetime string to local datetime."""
    # Handle both 'Z' suffix and no suffix (assume UTC if no timezone)
    if isinstance(utc_dt_str, str):
        utc_dt = datetime.fromisoformat(utc_dt_str.replace('Z', '+00:00'))
    else:
        # Already a datetime object
        utc_dt = utc_dt_str
    
    # If naive (no timezone), assume UTC
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    
    # Convert to local timezone
    return utc_dt.astimezone()

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
def list_users(
    show_all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Include archived users"
    )
):
    """List all users."""
    client = get_client()
    config = get_config()
    current_user_id = config.get_current_user_id()

    users = client.list_users(include_archived=show_all)
    if not users:
        console.print("[yellow]No users found.[/yellow]")
        return

    table = Table(title="Users" if not show_all else "All Users (including archived)")
    table.add_column("", style="yellow", width=2)  # Marker column
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Email", style="blue")
    table.add_column("Status", style="magenta")

    for user in users:
        name = f"{user['first_name']}"
        if user.get('middle_initial'):
            name += f" {user['middle_initial']}."
        name += f" {user['last_name']}"
        
        # Mark active user with arrow
        marker = "→" if user['id'] == current_user_id else ""
        
        # Show status
        status = "active" if user.get('active', True) else "archived"
        
        table.add_row(marker, str(user['id']), name, user['email'], status)

    console.print(table)
    
    if current_user_id:
        console.print(
            "\n[dim]→ marks the currently active user[/dim]"
        )


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
    "archive",
    help="Archive a user (hides from normal lists but keeps all data)"
)
def archive_user(
    email: str = typer.Option(..., "--email", "-e", help="Email address")
):
    """Archive a user (soft delete - keeps all tracking data)."""
    client = get_client()

    try:
        result = client.archive_user(email)
        console.print(f"[green]✓[/green] {result['message']}")
        console.print("[yellow]Note:[/yellow] User is archived but all tracking data is preserved")
        console.print("[yellow]Use 'sitr user list --all' to see archived users[/yellow]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@user_app.command(
    "restore",
    help="Restore an archived user"
)
def restore_user(
    email: str = typer.Option(..., "--email", "-e", help="Email address")
):
    """Restore an archived user."""
    client = get_client()

    try:
        result = client.restore_user(email)
        console.print(f"[green]✓[/green] {result['message']}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@user_app.command(
    "delete",
    help="⚠️  PERMANENTLY DELETE a user and ALL their data (DANGEROUS!)"
)
def delete_user(
    email: str = typer.Option(..., "--email", "-e", help="Email address"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt"
    )
):
    """
    Permanently delete a user and ALL associated data.
    
    WARNING: This will delete:
    - The user account
    - All tracking entries
    - All projects owned by this user (if no other users have tracking on them)
    
    This action CANNOT be undone!
    
    Consider using 'sitr user archive' instead to preserve data.
    """
    client = get_client()

    try:
        # Get user info first to show what will be deleted
        try:
            user_info = client.get_user_by_email(email)
        except:
            console.print(f"[red]Error:[/red] User '{email}' not found")
            raise typer.Exit(1)
        
        # Get deletion impact
        impact = client.get_user_deletion_impact(email)
        
        # Show warning
        console.print(f"\n[red bold]⚠️  WARNING: PERMANENT DELETION ⚠️[/red bold]\n")
        console.print(f"[yellow]User:[/yellow] {user_info['firstname']} {user_info['lastname']} ({email})")
        console.print(f"\n[red]This will permanently delete:[/red]")
        console.print(f"  • {impact['tracking_entries']} tracking entries")
        console.print(f"  • {impact['projects_owned']} projects owned by this user")
        if impact['projects_with_shared_tracking'] > 0:
            console.print(f"  • [yellow]Warning:[/yellow] {impact['projects_with_shared_tracking']} projects have tracking from other users")
            console.print(f"    These projects will be kept but this user's tracking will be removed")
        console.print(f"\n[red bold]THIS CANNOT BE UNDONE![/red bold]")
        console.print(f"\n[yellow]Consider using 'sitr user archive' instead to keep the data.[/yellow]\n")
        
        if not force:
            confirm = typer.confirm(
                f"Are you absolutely sure you want to delete user '{email}' and all their data?",
                default=False
            )
            
            if not confirm:
                console.print("[yellow]Deletion cancelled[/yellow]")
                raise typer.Exit(0)
            
            # Double confirmation for safety
            confirm2 = typer.confirm(
                "This is your last chance. Really delete? Type 'yes' to confirm",
                default=False
            )
            
            if not confirm2:
                console.print("[yellow]Deletion cancelled[/yellow]")
                raise typer.Exit(0)
        
        # Perform deletion
        result = client.delete_user(email, cascade=True)
        console.print(f"\n[green]✓[/green] {result['message']}")
        console.print(f"[yellow]Deleted:[/yellow] {result['deleted']['trackings']} tracking entries")
        console.print(f"[yellow]Deleted:[/yellow] {result['deleted']['projects']} projects")
        
    except typer.Exit:
        raise
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
        timestamp = utc_to_local(result['timestamp'])
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
        timestamp = utc_to_local(result['timestamp'])
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
        timestamp = utc_to_local(result['timestamp'])
        console.print(
            f"[green]✓[/green] {result['message']} at "
            f"{timestamp.strftime('%H:%M')}"
        )
        if result.get('data', {}).get('previous_project'):
            console.print(
                "[yellow]Note:[/yellow] Previous project was auto-ended."
            )
    except Exception as e:
        error_msg = str(e)
        
        # Check if error is about missing workday
        if "No open workday" in error_msg or "start your day first" in error_msg:
            # Smart prompt: offer to start workday and project together
            console.print(
                f"[yellow]⚠ Warning:[/yellow] No open workday."
            )
            
            # Ask user if they want to start workday now
            start_day = typer.confirm(
                f"Do you want to start your workday now and begin working on '{project}'?",
                default=True
            )
            
            if start_day:
                try:
                    # First, start the workday
                    day_result = client.start_day(user_id)
                    day_timestamp = utc_to_local(day_result['timestamp'])
                    console.print(
                        f"[green]✓[/green] Workday started at "
                        f"{day_timestamp.strftime('%H:%M')}"
                    )
                    
                    # Now start the project
                    result = client.start_project(user_id, project, no_confirm)
                    timestamp = utc_to_local(result['timestamp'])
                    console.print(
                        f"[green]✓[/green] {result['message']} at "
                        f"{timestamp.strftime('%H:%M')}"
                    )
                except Exception as start_error:
                    console.print(f"[red]Error:[/red] {start_error}")
                    raise typer.Exit(1)
            else:
                console.print("[dim]Cancelled. Start your day with:[/dim] sitr start-day")
                raise typer.Exit(0)
        else:
            # Other errors - just show them
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
        timestamp = utc_to_local(result['timestamp'])
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
        timestamp = utc_to_local(result['timestamp'])
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
        timestamp = utc_to_local(result['timestamp'])
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
        timestamp = utc_to_local(result['timestamp'])
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


@project_app.command("list", help="""List all your projects.
    
    \b
    By default, shows only active projects sorted by creation date.
    Use --all to include archived projects, or --alphabet for
    alphabetical sorting.
    
    \b
    Examples:
      sitr project list
      sitr project list --all
      sitr project list --alphabet
    """)
def project_list(
    all_projects: bool = typer.Option(
        False, "--all", help="Include archived projects"),
    alphabetic: bool = typer.Option(
        False, "--alphabet", help="Sort alphabetically by name")
):
    """List all projects."""
    user_id = get_current_user_id()
    client = get_client()

    try:
        # Get projects
        projects = client.list_projects(
            user_id=user_id,
            include_archived=all_projects,
            sort_alphabetically=alphabetic
        )

        if not projects:
            console.print(
                "[yellow]No projects found. "
                "Create one with 'sitr project add'[/yellow]"
            )
            return

        # Try to get current working project from tracking data
        current_project_name = None
        try:
            # Get latest tracking entry to see if working on something
            tracking = client.get_latest_tracking(user_id)
            if tracking and tracking.get('project_name'):
                # Check if it's a start/resume without matching end
                action = tracking.get('action')
                if action in ['Project Start', 'Project Resume']:
                    current_project_name = tracking['project_name']
        except Exception:
            pass  # If this fails, just don't mark anything

        # Create table
        table = Table(title="Projects", show_header=True)
        table.add_column("", style="yellow", width=2)  # Marker column
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("Created", style="dim")

        for project in projects:
            # project['state'] is 'active' or 'archived'
            is_active = project['state'] == 'active'
            status = "Active" if is_active else "Archived"
            style = "green" if is_active else "dim"
            created = project['created_at'].split('T')[0]
            
            # Mark currently working project with arrow
            marker = "→" if project['name'] == current_project_name else ""

            table.add_row(
                marker,
                project['name'],
                f"[{style}]{status}[/{style}]",
                created
            )

        console.print(table)
        
        if current_project_name:
            console.print(
                "\n[dim]→ marks the project you're currently "
                "working on[/dim]"
            )
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

        # Try to get current working project from tracking data
        current_project_name = None
        try:
            # Get latest tracking entry to see if working on something
            tracking = client.get_latest_tracking(user_id)
            if tracking and tracking.get('project_name'):
                # Check if it's a start/resume without matching end
                action = tracking.get('action')
                if action in ['Project Start', 'Project Resume']:
                    current_project_name = tracking['project_name']
        except Exception:
            pass  # If this fails, just don't mark anything

        table = Table(title="Projects")
        table.add_column("", style="yellow", width=2)  # Marker column
        table.add_column("Name", style="green")
        table.add_column("State", style="cyan")
        table.add_column("Created", style="yellow")

        for project in projects:
            created = datetime.fromisoformat(project['created_at'])
            # Mark currently active project with arrow
            marker = "→" if project['name'] == current_project_name else ""
            table.add_row(
                marker,
                project['name'],
                project['state'],
                created.strftime('%Y-%m-%d')
            )

        console.print(table)
        
        if current_project_name:
            console.print(
                "\n[dim]→ marks the project you're currently "
                "working on[/dim]"
            )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("status")
def show_status():
    """
    Show what you're currently doing.
    
    Human-readable status of your workday, current activity, and time spent.
    """
    client = get_client()
    config = get_config()
    
    try:
        # Get user info
        user_id = config.get_current_user_id()
        user_email = config.get_current_user_email()
        
        if not user_id or not user_email:
            console.print(
                "[yellow]No user selected.[/yellow] "
                "Use [cyan]sitr user select[/cyan] first."
            )
            raise typer.Exit(1)
        
        # Get user details for full name
        users = client.list_users()
        current_user = next((u for u in users if u['id'] == user_id), None)
        if current_user:
            name = f"{current_user['first_name']} {current_user['last_name']}"
        else:
            name = user_email
        
        console.print(f"[bold]You are:[/bold] {name}")
        
        # Get today's tracking entries
        today_entries = client.get_today_tracking(user_id)
        
        if not today_entries:
            console.print(
                "[dim]No active workday.[/dim] "
                "Start with [cyan]sitr start-day[/cyan]"
            )
            return
        
        # Find workday start (should be first entry)
        workday_start = None
        for entry in today_entries:
            if entry['action'] == 'Workday Start':
                workday_start = datetime.fromisoformat(entry['timestamp'])
                break
        
        if not workday_start:
            console.print(
                "[dim]No active workday.[/dim] "
                "Start with [cyan]sitr start-day[/cyan]"
            )
            return
        
        # Calculate time since workday start
        # Make sure we use timezone-aware datetime for comparison
        from datetime import timezone
        if workday_start.tzinfo is None:
            # If stored time is naive, assume UTC
            workday_start = workday_start.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        elapsed = now - workday_start
        hours = int(elapsed.total_seconds() // 3600)
        minutes = int((elapsed.total_seconds() % 3600) // 60)
        
        # Convert to local time for display
        local_start = workday_start.astimezone()
        start_time = local_start.strftime('%H:%M')
        
        console.print(
            f"[bold]Workday started:[/bold] {start_time} "
            f"({hours}h {minutes}m ago)"
        )
        
        # Analyze current state from today's entries
        # Process entries in chronological order to build up state
        current_project = None
        current_project_start = None
        on_break = False
        
        for entry in today_entries:
            action = entry['action']
            timestamp = datetime.fromisoformat(entry['timestamp'])
            
            if action == 'Break Start':
                on_break = True
                current_project = None
                current_project_start = None
            elif action == 'Break End':
                on_break = False
            elif action in ['Project Start', 'Project Resume']:
                current_project = entry['project_name']
                current_project_start = timestamp
                on_break = False
            elif action == 'Project End':
                current_project = None
                current_project_start = None
        
        # Show current activity
        if on_break:
            console.print("[bold]Currently:[/bold] [yellow]On break[/yellow]")
        elif current_project and current_project_start:
            # Ensure timezone consistency for project start time
            if current_project_start.tzinfo is None:
                current_project_start = current_project_start.replace(
                    tzinfo=timezone.utc
                )
            
            proj_elapsed = now - current_project_start
            proj_minutes = int(proj_elapsed.total_seconds() // 60)
            
            if proj_minutes < 60:
                time_str = f"{proj_minutes} minutes"
            else:
                proj_hours = proj_minutes // 60
                proj_mins = proj_minutes % 60
                time_str = f"{proj_hours}h {proj_mins}m"
            
            console.print(
                f"[bold]Working on:[/bold] [green]{current_project}[/green] "
                f"[dim](for {time_str})[/dim]"
            )
        else:
            console.print(
                "[bold]Currently:[/bold] [dim]Not working on any project[/dim]"
            )
            console.print(
                "[dim]Start with:[/dim] [cyan]sitr start <project>[/cyan]"
            )
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("info")
def show_info():
    """
    Show detailed system information and configuration.
    
    Displays:
    - Server configuration (host, port)
    - Database location
    - Config file location
    - API endpoint URLs
    """
    config = get_config()
    
    info_table = Table(title="SITR System Information", show_header=True)
    info_table.add_column("Setting", style="cyan", no_wrap=True)
    info_table.add_column("Value", style="green")
    
    # Config file
    import os
    config_file = os.path.expanduser("~/.sitrconfig")
    info_table.add_row("Config File", config_file)
    
    # Database
    from pathlib import Path
    db_file = str(Path.home() / ".sitr" / "sitr.db")
    info_table.add_row("Database", db_file)
    
    # Server
    info_table.add_row("Server Host", config.get_server_host())
    info_table.add_row("Server Port", str(config.get_server_port()))
    info_table.add_row("API URL", config.get_api_url())
    info_table.add_row("API Docs", f"{config.get_api_url()}/docs")
    info_table.add_row("Auto-start Server", str(config.get_auto_start_server()))
    
    # User
    user_email = config.get_current_user_email()
    if user_email:
        info_table.add_row("Current User", user_email)
    else:
        info_table.add_row("Current User", "[dim]Not set[/dim]")
    
    console.print(info_table)
    
    console.print("\n[dim]Tip: Use 'sitr status' for current work status[/dim]")


# Report commands
report_app = typer.Typer(help="Generate time reports in various formats")
app.add_typer(report_app, name="report")


@report_app.command("today")
def report_today(
    format: str = typer.Option(
        "ascii",
        "--format",
        "-f",
        help="Output format: csv, ascii, markdown, json"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Write to file instead of stdout"
    ),
    clipboard: bool = typer.Option(
        False,
        "--clipboard",
        "-c",
        help="Copy output to clipboard"
    ),
    no_header: bool = typer.Option(
        False,
        "--no-header",
        help="Omit header row (CSV only)"
    ),
    date: Optional[str] = typer.Option(
        None,
        "--date",
        "-d",
        help="Date in YYYY-MM-DD format (default: today)"
    )
):
    """Generate daily time report."""
    from report_generator import (
        ReportData,
        CSVFormatter,
        ASCIIFormatter,
        MarkdownFormatter,
        JSONFormatter
    )
    
    user_id = get_current_user_id()
    client = get_client()
    
    try:
        # Get report data from API
        report = client.get_daily_report(user_id, date)
        data = ReportData(report['entries'])
        
        # Format based on selection
        format_lower = format.lower()
        if format_lower == 'csv':
            result = CSVFormatter.format_daily(data, include_header=not no_header)
        elif format_lower == 'ascii':
            result = ASCIIFormatter.format_daily(data)
        elif format_lower == 'markdown':
            result = MarkdownFormatter.format_daily(data)
        elif format_lower == 'json':
            result = JSONFormatter.format_daily(data)
        else:
            console.print(f"[red]Unknown format:[/red] {format}")
            raise typer.Exit(1)
        
        # Handle output
        _handle_output(result, output, clipboard, format_lower)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@report_app.command("week")
def report_week(
    format: str = typer.Option(
        "ascii",
        "--format",
        "-f",
        help="Output format: csv, ascii, markdown, json"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Write to file instead of stdout"
    ),
    clipboard: bool = typer.Option(
        False,
        "--clipboard",
        "-c",
        help="Copy output to clipboard"
    ),
    no_header: bool = typer.Option(
        False,
        "--no-header",
        help="Omit header row (CSV only)"
    ),
    week_start: Optional[str] = typer.Option(
        None,
        "--week-start",
        "-w",
        help="Week start date (Monday) in YYYY-MM-DD format"
    ),
    timesheet: bool = typer.Option(
        False,
        "--timesheet",
        "--detailed",
        help="Detailed timesheet with dates (vs. summary by project)"
    )
):
    """Generate weekly time report.
    
    \b
    Default: Work Report (consolidated by project)
    --timesheet: Detailed timesheet with date, time, and project
    """
    from report_generator import (
        ReportData,
        CSVFormatter,
        ASCIIFormatter,
        MarkdownFormatter,
        JSONFormatter
    )
    
    user_id = get_current_user_id()
    client = get_client()
    
    try:
        # Get report data from API
        report = client.get_weekly_report(user_id, week_start)
        
        # Flatten all entries from all days
        all_entries = []
        for day_entries in report['days'].values():
            all_entries.extend(day_entries)
        
        data = ReportData(all_entries)
        
        # Choose formatter based on timesheet flag
        format_lower = format.lower()
        if timesheet:
            # Detailed timesheet with dates
            if format_lower == 'csv':
                result = CSVFormatter.format_weekly_timesheet(
                    data, include_header=not no_header
                )
            elif format_lower == 'ascii':
                result = ASCIIFormatter.format_weekly_timesheet(data)
            elif format_lower == 'markdown':
                result = MarkdownFormatter.format_daily(data)  # TODO
            elif format_lower == 'json':
                result = JSONFormatter.format_daily(data)  # TODO
            else:
                console.print(f"[red]Unknown format:[/red] {format}")
                raise typer.Exit(1)
        else:
            # Consolidated summary by project (default)
            if format_lower == 'csv':
                result = CSVFormatter.format_weekly_summary(
                    data, include_header=not no_header
                )
            elif format_lower == 'ascii':
                result = ASCIIFormatter.format_weekly_summary(data)
            elif format_lower == 'markdown':
                result = MarkdownFormatter.format_daily(data)  # TODO
            elif format_lower == 'json':
                result = JSONFormatter.format_daily(data)  # TODO
            else:
                console.print(f"[red]Unknown format:[/red] {format}")
                raise typer.Exit(1)
        
        # Handle output
        _handle_output(result, output, clipboard, format_lower)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@report_app.command("project")
def report_project(
    name: str = typer.Argument(..., help="Project name"),
    format: str = typer.Option(
        "ascii",
        "--format",
        "-f",
        help="Output format: csv, ascii, markdown, json"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Write to file instead of stdout"
    ),
    clipboard: bool = typer.Option(
        False,
        "--clipboard",
        "-c",
        help="Copy output to clipboard"
    ),
    no_header: bool = typer.Option(
        False,
        "--no-header",
        help="Omit header row (CSV only)"
    ),
    from_date: Optional[str] = typer.Option(
        None,
        "--from",
        help="Start date in YYYY-MM-DD format"
    ),
    to_date: Optional[str] = typer.Option(
        None,
        "--to",
        help="End date in YYYY-MM-DD format"
    )
):
    """Generate project time report."""
    from report_generator import (
        ReportData,
        CSVFormatter,
        ASCIIFormatter,
        MarkdownFormatter,
        JSONFormatter
    )
    
    user_id = get_current_user_id()
    client = get_client()
    
    try:
        # Get report data from API
        report = client.get_project_report(user_id, name, from_date, to_date)
        data = ReportData(report['entries'])
        
        # Format based on selection
        format_lower = format.lower()
        if format_lower == 'csv':
            result = CSVFormatter.format_project(data, include_header=not no_header)
        elif format_lower == 'ascii':
            result = ASCIIFormatter.format_project(data, name)
        elif format_lower == 'markdown':
            result = MarkdownFormatter.format_project(data, name)
        elif format_lower == 'json':
            result = JSONFormatter.format_project(data, name)
        else:
            console.print(f"[red]Unknown format:[/red] {format}")
            raise typer.Exit(1)
        
        # Handle output
        _handle_output(result, output, clipboard, format_lower)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def _handle_output(
    content: str,
    output_file: Optional[str],
    to_clipboard: bool,
    format: str
):
    """Handle output to stdout, file, or clipboard."""
    import subprocess
    import platform
    
    # Write to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            f.write(content)
        console.print(f"[green]✓[/green] Written to {output_file}")
    
    # Copy to clipboard if requested
    if to_clipboard:
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                process = subprocess.Popen(
                    ['pbcopy'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE
                )
                process.communicate(content.encode('utf-8'))
                lines = len(content.splitlines())
                console.print(
                    f"[green]✓[/green] Copied {lines} lines to clipboard"
                )
            elif system == "Linux":
                # Try xclip first, then xsel
                try:
                    process = subprocess.Popen(
                        ['xclip', '-selection', 'clipboard'],
                        stdin=subprocess.PIPE
                    )
                    process.communicate(content.encode('utf-8'))
                    lines = len(content.splitlines())
                    console.print(
                        f"[green]✓[/green] Copied {lines} lines to clipboard"
                    )
                except FileNotFoundError:
                    process = subprocess.Popen(
                        ['xsel', '--clipboard', '--input'],
                        stdin=subprocess.PIPE
                    )
                    process.communicate(content.encode('utf-8'))
                    lines = len(content.splitlines())
                    console.print(
                        f"[green]✓[/green] Copied {lines} lines to clipboard"
                    )
            elif system == "Windows":
                process = subprocess.Popen(
                    ['clip'],
                    stdin=subprocess.PIPE,
                    shell=True
                )
                process.communicate(content.encode('utf-8'))
                lines = len(content.splitlines())
                console.print(
                    f"[green]✓[/green] Copied {lines} lines to clipboard"
                )
        except Exception as e:
            console.print(
                f"[yellow]Warning:[/yellow] Could not copy to clipboard: {e}"
            )
    
    # Print to stdout only if not file/clipboard OR if ascii format
    if not output_file and not to_clipboard:
        # Always print
        console.print(content)
    elif format == 'ascii' and (output_file or to_clipboard):
        # ASCII can be printed alongside file/clipboard
        console.print(content)
    # For csv/json/markdown: only print if going to stdout


@app.command("init-db", help="Initialize database tables")
def init_db():
    """Initialize database tables."""
    from pathlib import Path
    from database_manager import DatabaseManager
    # Import models to register them with SQLModel.metadata
    import sitr_models  # noqa: F401
    
    db_path = Path.home() / ".sitr" / "sitr.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    console.print("[yellow]→ Initializing database...[/yellow]")
    console.print(f"[dim]Database: {db_path}[/dim]")
    
    try:
        db_manager = DatabaseManager(f"sqlite:///{db_path}")
        db_manager.create_tables()
        console.print("[green]✓ Database tables created successfully![/green]")
    except Exception as e:
        console.print(f"[red]✗ Error creating tables: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
