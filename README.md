# SITR - Simple Time Tracker

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLModel](https://img.shields.io/badge/SQLModel-latest-orange.svg)](https://sqlmodel.tiangolo.com/)

## What is SITR?

**SITR** (Simple Time Tracker) is a command-line time tracking tool that captures how you actually work. It tracks your workday lifecycle—starting your day, switching between projects, taking breaks, and ending your workday—with automatic context switching and intelligent handover logic.

## What makes it different?

Most time trackers just count hours on tasks. **SITR models the real phases of work**:

- ✅ **Workday lifecycle** - Explicit start and end of your work day
- ✅ **Automatic handover** - Switching projects automatically ends the previous one
- ✅ **Break management** - Pause work, then resume exactly where you left off
- ✅ **Auto-cleanup** - Ending your day closes all open items
- ✅ **Multiple report formats** - ASCII tables, CSV, Markdown, JSON with clipboard support

> *"This isn't a hobby project—it's a clean time-tracking architecture that does something almost all commercial tools overlook: **it models the real work phases of an individual person**, rather than just counting tasks or summing time."*

Perfect for:
- **Focus management** - Natural separation of work contexts
- **Energy analysis** - How long were you truly active per block?
- **Self-reflection** - Understand your work patterns
- **Client billing** - Export timesheets in multiple formats

## How it came to be

This project started as a **CS50P Final Project** for Harvard's "Introduction to Programming with Python" course. Life set other priorities, and it remained unfinished for almost two years. But I still wanted it for myself, so I finally completed it in 2025.

I took my original product vision and a dozen fragmented source files, paired them with Claude Sonnet 4.5, and after a few hours of collaboration, the result is a production-ready server with a REST API backend and a CLI tool—built with Domain-Driven Design principles, exactly as envisioned.

**Future plans:**
- GUI for Mac, iOS, and Apple Watch
- Cloud deployment with OpenID authentication
- Auto-start server on Linux, macOS, and Windows
- Integration with commercial time-tracking tools
- Free forever basic version

Find this useful? Want to contribute? Just let me know.

**by Tim Walter** - *begun in 2023, forgot about in 2024, and finished in 2025*

## ⚡ Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/TechPrototyper/CS50TimeTracker.git
cd CS50TimeTracker

# Run the installer
./install.sh

# Or install manually:
pip3 install .
```

After installation, the `sitr` command is available globally:

```bash
sitr --help
sitr start-day
```

For detailed installation instructions, see [INSTALL.md](INSTALL.md).

### Your First Workday

```bash
# 1. Create a user
sitr user add -f John -l Doe -e john@example.com

# 2. Select the user
sitr user select -e john@example.com

# 3. Create a project
sitr project add -n "CS50 Final Project"

# 4. Start your workday
sitr start-day

# 5. Start working on the project
sitr start "CS50 Final Project"

# 6. Take a break
sitr break start

# 7. Resume work
sitr continue

# 8. Check your progress
sitr status

# 9. Generate a report
sitr report today

# 10. End your workday
sitr end-day
```

**Note**: The API server starts automatically with any command. No manual server management needed!

### Example Report Output

After working on multiple projects, get a beautiful summary:

```bash
$ sitr report today
```

```
               Daily Time Report               
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━┓
┃ Project          ┃ Start ┃ End   ┃ Duration ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━┩
│ CS50 Final       │ 09:15 │ 11:30 │   2h 15m │
│ Documentation    │ 11:45 │ 12:20 │   0h 35m │
│ Code Review      │ 13:30 │ 15:45 │   2h 15m │
├──────────────────┼───────┼───────┼──────────┤
│ Total Work Time  │       │       │   5h 5m  │
│ Total Break Time │       │       │   0h 45m │
└──────────────────┴───────┴───────┴──────────┘
```

Export formats available: CSV, Markdown, JSON, or copy to clipboard for easy reporting!

### Server Management (optional - auto-starts)

```bash
# Start server manually
sitr server start

# Check server status
sitr server status

# Stop server
sitr server stop

# View server logs
sitr server logs
```

**Note**: The server starts automatically with any CLI command. Manual start is not necessary!

### 1. Create User

```bash
sitr user add \
  --firstname Tim \
  --lastname Walter \
  --email tech@smartlogics.net
```

### 2. Select User

```bash
sitr user select --email tech@smartlogics.net
```

### 3. Create Project

```bash
sitr project add --name "CS50 Final Project"
```

### 4. Start Workday

```bash
sitr start-day
```

### 5. Work on Project

```bash
sitr start "CS50 Final Project"
```

### 6. Take a Break

```bash
sitr break start
```

### 7. Resume Work

```bash
sitr continue
```

### 8. Switch to Another Project

```bash
sitr start "Documentation"
# Previous project will be automatically ended
```

### 9. End Workday

```bash
sitr end-day
# All open projects/breaks will be automatically closed
```

### Additional Commands

```bash
# List all users
sitr user list

# List all active projects
sitr projects

# Archive project
sitr project archive --name "Old Project"
```

## 📚 Commands Overview

### User Management
```bash
sitr user add -f <firstname> -l <lastname> -e <email>
sitr user list
sitr user select -e <email>
sitr user delete -e <email>
```

### Project Management
```bash
sitr project add -n <name>
sitr projects                    # List all active projects
sitr project archive -n <name>
```

### Time Tracking
```bash
sitr start-day                   # Begin your workday
sitr start <project-name>        # Start working on a project
sitr end <project-name>          # End work on a project
sitr break start                 # Take a break
sitr continue                    # Resume work after break
sitr end-day                     # End your workday
sitr status                      # Check current status
sitr info                        # Technical system information
```

### Reports & Analytics
```bash
sitr report today                # Today's work summary (ASCII table)
sitr report today --format csv   # Export as CSV
sitr report today --format markdown  # Markdown table
sitr report today --format json  # JSON output
sitr report week                 # This week's summary
sitr report project "MyProject"  # Project-specific report

# Output options
sitr report today --output timesheet.csv  # Save to file
sitr report today --clipboard    # Copy to clipboard (macOS)
sitr report today --no-header    # CSV without header row
```

### Server Management (optional)
```bash
sitr server start
sitr server stop
sitr server status
sitr server restart
sitr server logs
```

## 🔧 Configuration

SITR uses a configuration file at `~/.sitrconfig`:

```json
{
  "api_url": "http://127.0.0.1:8000",
  "auto_start_server": true,
  "current_user_id": 1,
  "current_user_email": "john@example.com",
  "server_host": "127.0.0.1",
  "server_port": 8000
}
```

The configuration is automatically created on first use and migrates settings from older versions if found.

## 🏗️ Architecture

SITR follows Domain-Driven Design (DDD) principles with a clean layered architecture:

```
┌─────────────────────────────────────┐
│   CLI Interface (Typer + Rich)      │
└──────────────┬──────────────────────┘
               │ HTTP/REST
┌──────────────▼──────────────────────┐
│   API Client (requests)             │
│   • Auto-start logic                │
│   • Retry mechanisms                │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   FastAPI Server (uvicorn)          │
│   • 16 REST endpoints               │
│   • CORS enabled                    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Service Layer                     │
│   • TimeManagementService           │
│   • Business logic & validation     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Repository Layer                  │
│   • UserRepository                  │
│   • ProjectRepository               │
│   • TrackingRepository              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Database (SQLite + SQLModel)      │
│   • User, Project, Tracking models  │
└─────────────────────────────────────┘
```

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 🚀 Roadmap

### ✅ Phase 1: CLI Production Ready (Complete)
- Full command-line interface
- Complete time tracking workflow
- REST API backend
- Auto-start server management
- Configuration system

### ✅ Phase 2: Enhancement & Integration (Complete)
- ✅ Export functionality (CSV, JSON, Markdown)
- ✅ Reports and analytics (daily, weekly, project-specific)

### 📋 Phase 3: Integration & Workflows (Planned)
- Alfred/LaunchBar workflows
- Enhanced export templates
- Additional report formats
- API documentation and client libraries

### 🔮 Phase 4: Advanced Features (Future)
- macOS menu bar app
- Automatic context switching based on active app
- Self-learning routine suggestions
- Team collaboration features
- Cloud sync and multi-device support

### 🧪 Experimental Development Tracks
There are parallel development efforts exploring:
- **Apple ecosystem integration** - Native apps for iOS, watchOS, and Siri integration
- **AI assistant integration** - Tools for LLM and AI assistant access
- **Third-party integrations** - Connections to commercial time tracking platforms

These experimental tracks are in early stages and may become available as separate products or integrations in the future.

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **CLI** | Typer, Rich |
| **API** | FastAPI, Uvicorn |
| **Database** | SQLModel (SQLAlchemy + Pydantic) |
| **Client** | Requests |
| **Server Mgmt** | psutil |
| **Testing** | pytest |
| **Data Validation** | Pydantic v2 |

## 📖 Documentation

- [Architecture Documentation](ARCHITECTURE.md) - Detailed technical architecture
- [Initial Description](Initial%20Description.md) - Original project vision
- [Project Completion Summary](PROJECT_COMPLETE.md) - Implementation details

## 🤝 Contributing

This project started as a personal CS50 final project and is now open for contributions. Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Special thanks to the consultant who saw the potential in this design and encouraged its completion. The architecture validation and strategic guidance were instrumental in transforming this from an abandoned CS50 project into a production-ready tool.

---

*Built with ❤️ for people who want to understand not just what they do, but how they work.*
