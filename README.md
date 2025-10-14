# SITR - Simple Time Tracker
by Tim Walter, begun in 2023, forgot about in 2024, and finished in 2025

> *A personal time-tracking OS that maps the real workflow of an individual human being through phases – instead of just counting tasks or summing durations.*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLModel](https://img.shields.io/badge/SQLModel-latest-orange.svg)](https://sqlmodel.tiangolo.com/)

**SITR** is a command-line time tracking tool with a complete REST API backend, designed to capture how you actually work: starting your day, switching between projects, taking breaks, and ending your workday—all with automatic context switching and intelligent handover logic.

## 🎯 Project Background

This project started as a **CS50 Final Project** but remained unfinished for quite some time. The deadline of CS50 has passed, and now it has been completed because I want to use it myself. After revisiting the initial design and architecture, it became clear that the foundation was solid enough to complete. So I put my vision and a dozen of fragmented Source Code files and let Claude Sonnet 4.5 insinuate a bit. The result is a production-ready server that does data handling, and a CLI tool that attaches to that API layer. The backend / business logic was built with Domain-Driven Design principles.

Having said that, there is still some remaining work I will attack when (or if) I find the time:

- Create a simple GUI on Mac, iOS and Apple Watch
- Put the server into the cloud to use it from anywhere
- Hence, use OpenID to attach users with known identities for a reasonable security
- Create install routines for Linux, MacOS and Windows to start local server automatically, and control this via any of the UIs
- Perhaps support managed interfaces to popular commercial tools real people are using
- Perhaps productize it with the basic version free forever.

Find this useful? Like to add a bit? Just let me know.

## 💡 What Makes SITR Different

### A Consultant's Perspective

> "You've designed something that is technically coherent, systemically well-thought-out, and realistically implementable. This isn't a hobby project—it's a clean time-tracking architecture that does something almost all commercial tools overlook: **it models the real work phases of an individual person**, rather than just counting tasks or summing time."

SITR bridges three worlds:
- **Productivity tool** - Track what you work on
- **Self-reflection system** - Understand your work patterns
- **Data logger** - Capture granular time data for analysis

### The Workday Approach

Most time trackers miss the human reality of work:

> "You're present, you do something, you switch context, you take a break, and you finish."

SITR models this natural flow:
- ✅ **Workday lifecycle** - Explicit start and end of your work day
- ✅ **Project handover** - Switching projects automatically ends the previous one
- ✅ **Break management** - Pause work, then resume exactly where you left off
- ✅ **Auto-cleanup** - Ending your day closes all open items

This creates natural separation of contexts, perfect for:
- Focus management
- Energy analysis ("How long was I truly active per block?")
- Self-learning routines (future: auto-tagging based on patterns)

## ⚡ Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/TechPrototyper/CS50TimeTracker.git
cd CS50TimeTracker

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or: .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Your First Workday

```bash
# 1. Create a user
python sitr_cli.py user add -f John -l Doe -e john@example.com

# 2. Select the user
python sitr_cli.py user select -e john@example.com

# 3. Create a project
python sitr_cli.py project add -n "CS50 Final Project"

# 4. Start your workday
python sitr_cli.py start-day

# 5. Start working on the project
python sitr_cli.py start "CS50 Final Project"

# 6. Take a break
python sitr_cli.py break start

# 7. Resume work
python sitr_cli.py continue

# 8. End your workday
python sitr_cli.py end-day
```

**Note**: The API server starts automatically with any command. No manual server management needed!

## Installation

```bash
# Python Virtual Environment erstellen und aktivieren
python3 -m venv .venv
source .venv/bin/activate  # Auf macOS/Linux
# oder: .venv\Scripts\activate auf Windows

# Dependencies installieren
pip install -r requirements.txt
```

## Quick Start

### Server Management (optional - startet automatisch)

```bash
# Server manuell starten
python sitr_cli.py server start

# Server Status prüfen
python sitr_cli.py server status

# Server stoppen
python sitr_cli.py server stop

# Server Logs anzeigen
python sitr_cli.py server logs
```

**Hinweis**: Der Server startet automatisch bei jedem CLI-Command. Manueller Start ist nicht nötig!

### 1. User anlegen

```bash
python sitr_cli.py user add \
  --firstname Tim \
  --lastname Walter \
  --email tech@smartlogics.net
```

### 2. User auswählen

```bash
python sitr_cli.py user select --email tech@smartlogics.net
```

### 3. Projekt erstellen

```bash
python sitr_cli.py project add --name "CS50 Final Project"
```

### 4. Arbeitstag starten

```bash
python sitr_cli.py start-day
```

### 5. An Projekt arbeiten

```bash
python sitr_cli.py start "CS50 Final Project"
```

### 6. Pause machen

```bash
python sitr_cli.py break start
```

### 7. Weiterarbeiten

```bash
python sitr_cli.py continue
```

### 8. Zu anderem Projekt wechseln

```bash
python sitr_cli.py start "Documentation"
# Vorheriges Projekt wird automatisch beendet
```

### 9. Arbeitstag beenden

```bash
python sitr_cli.py end-day
# Alle offenen Projekte/Breaks werden automatisch geschlossen
```

### Weitere Commands

```bash
# Alle User anzeigen
python sitr_cli.py user list

# Alle aktiven Projekte anzeigen
python sitr_cli.py projects

# Projekt archivieren
python sitr_cli.py project archive --name "Old Project"
```

## 📚 Commands Overview

### User Management
```bash
python sitr_cli.py user add -f <firstname> -l <lastname> -e <email>
python sitr_cli.py user list
python sitr_cli.py user select -e <email>
python sitr_cli.py user delete -e <email>
```

### Project Management
```bash
python sitr_cli.py project add -n <name>
python sitr_cli.py projects                    # List all active projects
python sitr_cli.py project archive -n <name>
```

### Time Tracking
```bash
python sitr_cli.py start-day                   # Begin your workday
python sitr_cli.py start <project-name>        # Start working on a project
python sitr_cli.py end <project-name>          # End work on a project
python sitr_cli.py break start                 # Take a break
python sitr_cli.py continue                    # Resume work after break
python sitr_cli.py end-day                     # End your workday
```

### Server Management (optional)
```bash
python sitr_cli.py server start
python sitr_cli.py server stop
python sitr_cli.py server status
python sitr_cli.py server restart
python sitr_cli.py server logs
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

### 📋 Phase 2: Enhancement & Integration (Planned)
- Export functionality (CSV, JSON)
- Reports and analytics
- Integration with macOS Shortcuts
- Alfred/LaunchBar workflows

### 🔮 Phase 3: UI & Advanced Features (Future)
- macOS menu bar app
- Apple Watch companion
- Automatic context switching based on active app
- Self-learning routine suggestions

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