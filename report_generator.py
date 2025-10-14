"""
Report generation and formatting module for SITR.

Handles calculation of durations, grouping, and formatting reports
in multiple output formats (CSV, ASCII, Markdown, JSON).
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import json
import csv
import io


class ReportData:
    """Container for calculated report data."""
    
    def __init__(self, entries: List[Dict[str, Any]]):
        """Initialize with raw tracking entries."""
        self.entries = entries
        self.sessions = []
        self.breaks = []
        self.workday_start = None
        self.workday_end = None
        self._calculate()
    
    def _calculate(self):
        """Calculate sessions, breaks, and durations from raw entries."""
        if not self.entries:
            return
        
        current_project = None
        current_start = None
        break_start = None
        
        for entry in self.entries:
            action = entry['action']
            timestamp = datetime.fromisoformat(entry['timestamp'])
            project_name = entry.get('project_name')
            
            if action == 'Workday Start':
                self.workday_start = timestamp
            
            elif action == 'Workday End':
                self.workday_end = timestamp
                # End any open project
                if current_project and current_start:
                    self.sessions.append({
                        'project': current_project,
                        'start': current_start,
                        'end': timestamp,
                        'duration': timestamp - current_start
                    })
                    current_project = None
                    current_start = None
            
            elif action in ['Project Start', 'Project Resume']:
                current_project = project_name
                current_start = timestamp
            
            elif action == 'Project End':
                if current_project and current_start:
                    self.sessions.append({
                        'project': current_project,
                        'start': current_start,
                        'end': timestamp,
                        'duration': timestamp - current_start
                    })
                current_project = None
                current_start = None
            
            elif action == 'Break Start':
                break_start = timestamp
                # Pause current project
                if current_project and current_start:
                    self.sessions.append({
                        'project': current_project,
                        'start': current_start,
                        'end': timestamp,
                        'duration': timestamp - current_start
                    })
                    # Don't clear current_project, will resume after break
            
            elif action == 'Break End':
                if break_start:
                    self.breaks.append({
                        'start': break_start,
                        'end': timestamp,
                        'duration': timestamp - break_start
                    })
                break_start = None
        
        # Close any open session
        if current_project and current_start:
            now = datetime.now(timezone.utc)
            self.sessions.append({
                'project': current_project,
                'start': current_start,
                'end': now,
                'duration': now - current_start,
                'ongoing': True
            })
    
    def get_project_totals(self) -> Dict[str, timedelta]:
        """Get total time per project."""
        totals = {}
        for session in self.sessions:
            project = session['project']
            duration = session['duration']
            totals[project] = totals.get(project, timedelta()) + duration
        return totals
    
    def get_total_work_time(self) -> timedelta:
        """Get total work time across all projects."""
        return sum((s['duration'] for s in self.sessions), timedelta())
    
    def get_total_break_time(self) -> timedelta:
        """Get total break time."""
        return sum((b['duration'] for b in self.breaks), timedelta())


class ReportFormatter:
    """Base class for report formatters."""
    
    @staticmethod
    def format_duration(td: timedelta) -> str:
        """Format timedelta as HH:MM or Hh Mm."""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    
    @staticmethod
    def format_time(dt: datetime) -> str:
        """Format datetime as HH:MM in local timezone."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        local_dt = dt.astimezone()
        return local_dt.strftime('%H:%M')


class CSVFormatter(ReportFormatter):
    """Format reports as CSV."""
    
    @staticmethod
    def format_daily(data: ReportData, include_header: bool = True) -> str:
        """Format daily report as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        if include_header:
            writer.writerow(['Project', 'Start', 'End', 'Duration'])
        
        for session in data.sessions:
            writer.writerow([
                session['project'],
                CSVFormatter.format_time(session['start']),
                CSVFormatter.format_time(session['end']),
                CSVFormatter.format_duration(session['duration'])
            ])
        
        return output.getvalue()
    
    @staticmethod
    def format_project(data: ReportData, include_header: bool = True) -> str:
        """Format project report as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        if include_header:
            writer.writerow(['Date', 'Start', 'End', 'Duration'])
        
        for session in data.sessions:
            date_str = session['start'].strftime('%Y-%m-%d')
            writer.writerow([
                date_str,
                CSVFormatter.format_time(session['start']),
                CSVFormatter.format_time(session['end']),
                CSVFormatter.format_duration(session['duration'])
            ])
        
        return output.getvalue()
    
    @staticmethod
    def format_weekly_timesheet(data: ReportData, include_header: bool = True) -> str:
        """Format weekly report as detailed timesheet with dates."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        if include_header:
            writer.writerow(['Date', 'Project', 'Start', 'End', 'Duration'])
        
        # Group by date
        by_date = {}
        for session in data.sessions:
            date_str = session['start'].strftime('%Y-%m-%d')
            if date_str not in by_date:
                by_date[date_str] = []
            by_date[date_str].append(session)
        
        # Write sessions grouped by date
        for date_str in sorted(by_date.keys()):
            for session in by_date[date_str]:
                writer.writerow([
                    date_str,
                    session['project'],
                    CSVFormatter.format_time(session['start']),
                    CSVFormatter.format_time(session['end']),
                    CSVFormatter.format_duration(session['duration'])
                ])
            
            # Day total
            day_total = sum((s['duration'] for s in by_date[date_str]), timedelta())
            writer.writerow([
                date_str,
                'Day Total',
                '',
                '',
                CSVFormatter.format_duration(day_total)
            ])
        
        # Week total
        week_total = data.get_total_work_time()
        writer.writerow(['', 'Week Total', '', '', CSVFormatter.format_duration(week_total)])
        
        return output.getvalue()
    
    @staticmethod
    def format_weekly_summary(data: ReportData, include_header: bool = True) -> str:
        """Format weekly report as consolidated summary by project."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        if include_header:
            writer.writerow(['Project', 'Total Duration'])
        
        # Consolidate by project
        by_project = {}
        for session in data.sessions:
            project = session['project']
            if project not in by_project:
                by_project[project] = timedelta()
            by_project[project] += session['duration']
        
        # Write project totals
        for project in sorted(by_project.keys()):
            writer.writerow([
                project,
                CSVFormatter.format_duration(by_project[project])
            ])
        
        # Total
        total = data.get_total_work_time()
        writer.writerow(['Total Work Time', CSVFormatter.format_duration(total)])
        
        break_time = data.get_total_break_time()
        if break_time.total_seconds() > 0:
            writer.writerow(['Total Break Time', CSVFormatter.format_duration(break_time)])
        
        return output.getvalue()


class ASCIIFormatter(ReportFormatter):
    """Format reports as ASCII tables with Rich."""
    
    @staticmethod
    def format_daily(data: ReportData) -> str:
        """Format daily report as ASCII table."""
        from rich.console import Console
        from rich.table import Table
        
        # Use plain text console without any styling
        output = io.StringIO()
        console = Console(
            file=output,
            force_terminal=False,  # Don't force terminal for plain output
            width=80,
            legacy_windows=False,
            no_color=True  # Disable ANSI codes
        )
        
        table = Table(title="Daily Time Report", show_header=True)
        table.add_column("Project", style="cyan")
        table.add_column("Start", style="green")
        table.add_column("End", style="green")
        table.add_column("Duration", style="yellow", justify="right")
        
        for session in data.sessions:
            table.add_row(
                session['project'],
                ASCIIFormatter.format_time(session['start']),
                ASCIIFormatter.format_time(session['end']),
                ASCIIFormatter.format_duration(session['duration'])
            )
        
        # Add totals
        total_work = data.get_total_work_time()
        total_break = data.get_total_break_time()
        
        table.add_section()
        table.add_row(
            "[bold]Total Work Time[/bold]",
            "",
            "",
            f"[bold]{ASCIIFormatter.format_duration(total_work)}[/bold]"
        )
        
        if total_break.total_seconds() > 0:
            table.add_row(
                "[dim]Total Break Time[/dim]",
                "",
                "",
                f"[dim]{ASCIIFormatter.format_duration(total_break)}[/dim]"
            )
        
        console.print(table)
        return output.getvalue()
    
    @staticmethod
    def format_project(data: ReportData, project_name: str) -> str:
        """Format project report as ASCII table."""
        from rich.console import Console
        from rich.table import Table
        
        output = io.StringIO()
        console = Console(
            file=output,
            force_terminal=False,  # Don't force terminal for plain output
            width=80,
            legacy_windows=False,
            no_color=True  # Disable ANSI codes
        )
        
        table = Table(
            title=f"Project Report: {project_name}",
            show_header=True
        )
        table.add_column("Date", style="cyan")
        table.add_column("Start", style="green")
        table.add_column("End", style="green")
        table.add_column("Duration", style="yellow", justify="right")
        
        # Group by date
        by_date = {}
        for session in data.sessions:
            date_str = session['start'].strftime('%Y-%m-%d')
            if date_str not in by_date:
                by_date[date_str] = []
            by_date[date_str].append(session)
        
        for date_str in sorted(by_date.keys()):
            sessions = by_date[date_str]
            day_total = sum((s['duration'] for s in sessions), timedelta())
            
            for i, session in enumerate(sessions):
                table.add_row(
                    date_str if i == 0 else "",
                    ASCIIFormatter.format_time(session['start']),
                    ASCIIFormatter.format_time(session['end']),
                    ASCIIFormatter.format_duration(session['duration'])
                )
            
            # Day subtotal
            table.add_row(
                "",
                "",
                f"[dim]Day Total[/dim]",
                f"[bold]{ASCIIFormatter.format_duration(day_total)}[/bold]"
            )
        
        # Grand total
        total = data.get_total_work_time()
        table.add_section()
        table.add_row(
            "[bold]Total[/bold]",
            "",
            "",
            f"[bold]{ASCIIFormatter.format_duration(total)}[/bold]"
        )
        
        console.print(table)
        content = output.getvalue()
        output.close()
        return content
    
    @staticmethod
    def format_weekly_timesheet(data: ReportData) -> str:
        """Format weekly report as detailed timesheet with dates."""
        from rich.console import Console
        from rich.table import Table
        
        output = io.StringIO()
        console = Console(
            file=output,
            force_terminal=False,
            width=100,
            legacy_windows=False,
            no_color=True
        )
        
        table = Table(title="Weekly Timesheet", show_header=True)
        table.add_column("Date", style="cyan")
        table.add_column("Project", style="magenta")
        table.add_column("Start", style="green")
        table.add_column("End", style="green")
        table.add_column("Duration", style="yellow", justify="right")
        
        # Group by date
        by_date: dict = {}
        for session in data.sessions:
            date_str = session['start'].strftime('%Y-%m-%d')
            if date_str not in by_date:
                by_date[date_str] = []
            by_date[date_str].append(session)
        
        # Add sessions grouped by date
        for date_str in sorted(by_date.keys()):
            sessions = by_date[date_str]
            day_total = sum((s['duration'] for s in sessions), timedelta())
            
            for i, session in enumerate(sessions):
                table.add_row(
                    date_str if i == 0 else "",
                    session['project'],
                    ASCIIFormatter.format_time(session['start']),
                    ASCIIFormatter.format_time(session['end']),
                    ASCIIFormatter.format_duration(session['duration'])
                )
            
            # Day subtotal
            table.add_row(
                "",
                "[dim]Day Total[/dim]",
                "",
                "",
                f"[bold]{ASCIIFormatter.format_duration(day_total)}[/bold]"
            )
        
        # Week total
        week_total = data.get_total_work_time()
        table.add_section()
        table.add_row(
            "[bold]Week Total[/bold]",
            "",
            "",
            "",
            f"[bold]{ASCIIFormatter.format_duration(week_total)}[/bold]"
        )
        
        console.print(table)
        content = output.getvalue()
        output.close()
        return content
    
    @staticmethod
    def format_weekly_summary(data: ReportData) -> str:
        """Format weekly report as consolidated summary by project."""
        from rich.console import Console
        from rich.table import Table
        
        output = io.StringIO()
        console = Console(
            file=output,
            force_terminal=False,
            width=80,
            legacy_windows=False,
            no_color=True
        )
        
        table = Table(title="Weekly Work Report", show_header=True)
        table.add_column("Project", style="cyan")
        table.add_column("Total Duration", style="yellow", justify="right")
        
        # Consolidate by project
        by_project: dict = {}
        for session in data.sessions:
            project = session['project']
            if project not in by_project:
                by_project[project] = timedelta()
            by_project[project] += session['duration']
        
        # Add project rows
        for project in sorted(by_project.keys()):
            table.add_row(
                project,
                ASCIIFormatter.format_duration(by_project[project])
            )
        
        # Totals
        total_work = data.get_total_work_time()
        total_break = data.get_total_break_time()
        
        table.add_section()
        table.add_row(
            "[bold]Total Work Time[/bold]",
            f"[bold]{ASCIIFormatter.format_duration(total_work)}[/bold]"
        )
        
        if total_break.total_seconds() > 0:
            table.add_row(
                "[dim]Total Break Time[/dim]",
                f"[dim]{ASCIIFormatter.format_duration(total_break)}[/dim]"
            )
        
        console.print(table)
        content = output.getvalue()
        output.close()
        return content


class MarkdownFormatter(ReportFormatter):
    """Format reports as Markdown tables."""
    
    @staticmethod
    def format_daily(data: ReportData) -> str:
        """Format daily report as Markdown."""
        lines = []
        lines.append("# Daily Time Report")
        lines.append("")
        lines.append("| Project | Start | End | Duration |")
        lines.append("|---------|-------|-----|----------|")
        
        for session in data.sessions:
            lines.append(f"| {session['project']} | "
                        f"{MarkdownFormatter.format_time(session['start'])} | "
                        f"{MarkdownFormatter.format_time(session['end'])} | "
                        f"{MarkdownFormatter.format_duration(session['duration'])} |")
        
        lines.append("")
        total_work = data.get_total_work_time()
        total_break = data.get_total_break_time()
        lines.append(f"**Total Work Time:** {MarkdownFormatter.format_duration(total_work)}")
        
        if total_break.total_seconds() > 0:
            lines.append(f"**Total Break Time:** {MarkdownFormatter.format_duration(total_break)}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_project(data: ReportData, project_name: str) -> str:
        """Format project report as Markdown."""
        lines = []
        lines.append(f"# Project Report: {project_name}")
        lines.append("")
        lines.append("| Date | Start | End | Duration |")
        lines.append("|------|-------|-----|----------|")
        
        for session in data.sessions:
            date_str = session['start'].strftime('%Y-%m-%d')
            lines.append(f"| {date_str} | "
                        f"{MarkdownFormatter.format_time(session['start'])} | "
                        f"{MarkdownFormatter.format_time(session['end'])} | "
                        f"{MarkdownFormatter.format_duration(session['duration'])} |")
        
        lines.append("")
        total = data.get_total_work_time()
        lines.append(f"**Total:** {MarkdownFormatter.format_duration(total)}")
        
        return "\n".join(lines)


class JSONFormatter(ReportFormatter):
    """Format reports as JSON."""
    
    @staticmethod
    def format_daily(data: ReportData) -> str:
        """Format daily report as JSON."""
        sessions = []
        for session in data.sessions:
            sessions.append({
                'project': session['project'],
                'start': session['start'].isoformat(),
                'end': session['end'].isoformat(),
                'duration_seconds': int(session['duration'].total_seconds()),
                'duration_formatted': JSONFormatter.format_duration(session['duration'])
            })
        
        result = {
            'sessions': sessions,
            'summary': {
                'total_work_seconds': int(data.get_total_work_time().total_seconds()),
                'total_work_formatted': JSONFormatter.format_duration(data.get_total_work_time()),
                'total_break_seconds': int(data.get_total_break_time().total_seconds()),
                'total_break_formatted': JSONFormatter.format_duration(data.get_total_break_time())
            }
        }
        
        return json.dumps(result, indent=2)
    
    @staticmethod
    def format_project(data: ReportData, project_name: str) -> str:
        """Format project report as JSON."""
        sessions = []
        for session in data.sessions:
            sessions.append({
                'date': session['start'].strftime('%Y-%m-%d'),
                'start': session['start'].isoformat(),
                'end': session['end'].isoformat(),
                'duration_seconds': int(session['duration'].total_seconds()),
                'duration_formatted': JSONFormatter.format_duration(session['duration'])
            })
        
        result = {
            'project': project_name,
            'sessions': sessions,
            'summary': {
                'total_seconds': int(data.get_total_work_time().total_seconds()),
                'total_formatted': JSONFormatter.format_duration(data.get_total_work_time())
            }
        }
        
        return json.dumps(result, indent=2)
