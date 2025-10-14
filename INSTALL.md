# SITR Installation Guide

Complete installation guide for macOS, Linux, and Windows.

## Quick Installation (Recommended)

### Option 1: Direct Installation (Python)

```bash
# Clone the repository
git clone https://github.com/TechPrototyper/CS50TimeTracker.git
cd CS50TimeTracker

# Run the installer
./install.sh
```

After installation, the `sitr` command will be available globally:

```bash
sitr --help
sitr user add -f John -l Doe -e john@example.com
sitr start-day
```

### Option 2: Development Installation

For contributing or development:

```bash
./install.sh --dev
```

This installs SITR in editable mode, so changes to the code take effect immediately.

---

## Platform-Specific Instructions

### macOS

#### Method 1: Using the Install Script (Recommended)

```bash
git clone https://github.com/TechPrototyper/CS50TimeTracker.git
cd CS50TimeTracker
./install.sh
```

The script will:
- ✅ Check Python version (3.10+ required)
- ✅ Install SITR and dependencies
- ✅ Make `sitr` command available globally

#### Method 2: Manual pip Installation

```bash
# Install directly via pip
pip3 install .

# Or in development mode:
pip3 install -e .
```

#### Method 3: Homebrew (Coming Soon)

We're working on a Homebrew tap for easier installation:

```bash
# Future release
brew tap TechPrototyper/sitr
brew install sitr
```

#### Troubleshooting macOS

If `sitr` command is not found after installation:

```bash
# Add pip's bin directory to your PATH
echo 'export PATH="$HOME/Library/Python/3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Linux

#### Method 1: Using the Install Script

```bash
git clone https://github.com/TechPrototyper/CS50TimeTracker.git
cd CS50TimeTracker
./install.sh
```

#### Method 2: Manual Installation

```bash
# Install system-wide (requires sudo)
sudo pip3 install .

# Or user installation (no sudo):
pip3 install --user .
```

#### Troubleshooting Linux

If `sitr` is not in PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Windows

#### Using Git Bash or WSL

```bash
git clone https://github.com/TechPrototyper/CS50TimeTracker.git
cd CS50TimeTracker
./install.sh
```

#### Using Command Prompt or PowerShell

```cmd
git clone https://github.com/TechPrototyper/CS50TimeTracker.git
cd CS50TimeTracker
pip install .
```

#### Troubleshooting Windows

If `sitr` is not recognized:

1. Find Python Scripts directory:
   ```cmd
   python -m site --user-base
   ```

2. Add to PATH (typically `C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts`)

---

## Verification

After installation, verify everything works:

```bash
# Check version
sitr --help

# Should show:
# Usage: sitr [OPTIONS] COMMAND [ARGS]...
# Simple Time Tracker (SITR) - Track your work time efficiently.
```

Test a complete workflow:

```bash
# Create a user
sitr user add -f Test -l User -e test@test.com

# Select the user
sitr user select -e test@test.com

# Start your day
sitr start-day

# Check server status
sitr server status
```

---

## Uninstallation

### Using the Install Script

```bash
./install.sh --uninstall
```

### Manual Uninstall

```bash
pip3 uninstall sitr
```

### Complete Cleanup

Remove all SITR data:

```bash
# Remove database
rm sitr.db

# Remove config
rm ~/.sitrconfig

# Remove server PID file
rm -rf ~/.sitr
```

---

## Development Setup

For contributors:

```bash
# Clone repository
git clone https://github.com/TechPrototyper/CS50TimeTracker.git
cd CS50TimeTracker

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or: .venv\Scripts\activate  # Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

---

## Alternative: Running Without Installation

If you don't want to install SITR globally:

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run directly
python sitr_cli.py --help
python sitr_cli.py start-day
```

Create an alias for convenience:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias sitr="python /path/to/CS50TimeTracker/sitr_cli.py"
```

---

## Requirements

- **Python**: 3.10 or higher
- **Disk Space**: ~50MB (including dependencies)
- **RAM**: ~50MB during operation
- **OS**: macOS 10.15+, Linux (any modern distro), Windows 10+

---

## Dependencies

All dependencies are installed automatically:

- `fastapi` - REST API framework
- `uvicorn` - ASGI server
- `sqlmodel` - ORM
- `typer` - CLI framework
- `rich` - Terminal formatting
- `requests` - HTTP client
- `psutil` - Process management
- `pydantic` - Data validation
- `email-validator` - Email validation

---

## Troubleshooting

### Python Version Issues

```bash
# Check Python version
python3 --version

# Should be 3.10 or higher
```

### Permission Issues

If you get permission errors:

```bash
# Use --user flag
pip3 install --user .
```

### PATH Issues

If `sitr` command is not found:

**macOS/Linux:**
```bash
which sitr  # Find where it's installed
echo $PATH  # Check if that directory is in PATH
```

**Windows:**
```cmd
where sitr
echo %PATH%
```

### Server Won't Start

```bash
# Check if port 8000 is available
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Try restarting
sitr server restart
```

---

## Getting Help

- 📖 [README.md](README.md) - Project overview
- 🚀 [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md) - Technical documentation
- 🐛 [GitHub Issues](https://github.com/TechPrototyper/CS50TimeTracker/issues) - Report bugs

---

*For more information, see [README.md](README.md)*
