# SITR Quick Start Guide

Get up and running with SITR in 5 minutes! ⚡

## Installation

```bash
# Clone the repository
git clone https://github.com/TechPrototyper/CS50TimeTracker.git
cd CS50TimeTracker

# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## First Time Setup

### 1. Create Your User Profile

```bash
python sitr_cli.py user add \
  --firstname John \
  --lastname Doe \
  --email john@example.com
```

### 2. Select Yourself as Active User

```bash
python sitr_cli.py user select --email john@example.com
```

### 3. Create Some Projects

```bash
python sitr_cli.py project add --name "CS50 Final Project"
python sitr_cli.py project add --name "Documentation"
python sitr_cli.py project add --name "Learning Python"
```

## Daily Workflow

### Morning - Start Your Day

```bash
# Begin your workday
python sitr_cli.py start-day

# Start working on your first project
python sitr_cli.py start "CS50 Final Project"
```

Output:
```
✓ Workday started at 09:00
✓ Started working on 'CS50 Final Project' at 09:01
```

### During the Day - Switch Projects

```bash
# Switch to another project (automatically ends previous one)
python sitr_cli.py start "Documentation"
```

Output:
```
✓ Ended work on 'CS50 Final Project' at 11:30
✓ Started working on 'Documentation' at 11:30
```

### Take a Break

```bash
# Start your lunch break
python sitr_cli.py break start

# Resume work after break
python sitr_cli.py continue
```

Output:
```
✓ Break started at 12:00
✓ Resumed work on 'Documentation' at 13:00
```

### Evening - End Your Day

```bash
# End your workday (automatically closes all open items)
python sitr_cli.py end-day
```

Output:
```
✓ Workday ended at 17:00
```

## Common Commands

### View Your Projects

```bash
python sitr_cli.py projects
```

Output:
```
                Projects                
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┓
┃ Name                 ┃ State  ┃ Created    ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━┩
│ CS50 Final Project   │ active │ 2025-10-14 │
│ Documentation        │ active │ 2025-10-14 │
│ Learning Python      │ active │ 2025-10-14 │
└──────────────────────┴────────┴────────────┘
```

### View All Users

```bash
python sitr_cli.py user list
```

### Archive Completed Projects

```bash
python sitr_cli.py project archive --name "CS50 Final Project"
```

## Server Management (Optional)

The API server starts automatically, but you can manage it manually:

```bash
# Check server status
python sitr_cli.py server status

# Start server manually
python sitr_cli.py server start

# Stop server
python sitr_cli.py server stop

# Restart server
python sitr_cli.py server restart

# View server logs
python sitr_cli.py server logs
```

## Tips & Tricks

### 1. Use Shell Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
alias sitr="python /path/to/CS50TimeTracker/sitr_cli.py"
```

Then you can just use:
```bash
sitr start-day
sitr start "My Project"
sitr end-day
```

### 2. Command Shortcuts

Most commands have short options:

```bash
# Instead of --firstname, --lastname, --email
python sitr_cli.py user add -f John -l Doe -e john@example.com

# Instead of --name
python sitr_cli.py project add -n "Quick Project"
```

### 3. Get Help Anytime

```bash
# General help
python sitr_cli.py --help

# Command-specific help
python sitr_cli.py user --help
python sitr_cli.py project --help
python sitr_cli.py start --help
```

### 4. Check Your Configuration

Your settings are stored in `~/.sitrconfig`:

```bash
cat ~/.sitrconfig
```

Example:
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

## Complete Command Reference

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
sitr projects                    # List active projects
sitr project archive -n <name>
```

### Time Tracking
```bash
sitr start-day                   # Start workday
sitr start <project-name>        # Start project
sitr end <project-name>          # End project
sitr break start                 # Take break
sitr continue                    # Resume after break
sitr end-day                     # End workday
```

### Server Management
```bash
sitr server start
sitr server stop
sitr server status
sitr server restart
sitr server logs
```

## Troubleshooting

### Server Won't Start

```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill any process using port 8000
kill -9 <PID>

# Or restart the server
python sitr_cli.py server restart
```

### Database Issues

```bash
# Your database is stored at: ./sitr.db
# Back it up before troubleshooting:
cp sitr.db sitr.db.backup

# If needed, recreate tables (WARNING: deletes all data)
rm sitr.db
python sitr_cli.py user add -f Test -l User -e test@example.com
```

### Configuration Issues

```bash
# Reset configuration
rm ~/.sitrconfig

# Next command will recreate it automatically
python sitr_cli.py user list
```

## What's Next?

- Read the [README.md](README.md) for more details
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Review [DEVELOPMENT_NOTES.md](DEVELOPMENT_NOTES.md) for future plans

## Need Help?

- Check existing [GitHub Issues](https://github.com/TechPrototyper/CS50TimeTracker/issues)
- Create a new issue if you find a bug
- Read the API documentation: `http://127.0.0.1:8000/docs` (when server is running)

---

**Happy time tracking! 🎯**
