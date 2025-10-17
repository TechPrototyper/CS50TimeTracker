#!/bin/bash
#
# SITR Installation Script
# Supports macOS, Linux, and Windows (via Git Bash/WSL)
#
# Usage:
#   ./install.sh              - Interactive installation
#   ./install.sh --fresh      - Fresh install with demo data
#   ./install.sh --update     - Update keeping existing database
#   ./install.sh --dev        - Development mode installation
#   ./install.sh --uninstall  - Remove SITR
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Database location
DB_DIR="$HOME/.sitr"
DB_FILE="$DB_DIR/sitr.db"
OLD_DB_FILE="./sitr.db"  # Legacy location

# Check if database exists
check_database() {
    if [ -f "$DB_FILE" ]; then
        return 0  # Database exists
    elif [ -f "$OLD_DB_FILE" ]; then
        return 0  # Old database exists
    else
        return 1  # No database
    fi
}

# Backup existing database
backup_database() {
    if [ -f "$DB_FILE" ]; then
        BACKUP_FILE="${DB_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}→ Creating database backup...${NC}"
        cp "$DB_FILE" "$BACKUP_FILE"
        echo -e "${GREEN}✓ Database backed up to: $BACKUP_FILE${NC}"
    fi
}

# Setup fresh database
setup_fresh_database() {
    echo -e "\n${YELLOW}→ Setting up fresh database...${NC}"
    
    # Remove old database if exists
    if [ -f "$DB_FILE" ]; then
        rm "$DB_FILE"
        echo -e "${GREEN}✓ Removed old database${NC}"
    fi
    
    # Reset config file to clear user selection
    CONFIG_FILE="$HOME/.sitrconfig"
    if [ -f "$CONFIG_FILE" ]; then
        rm "$CONFIG_FILE"
        echo -e "${GREEN}✓ Reset configuration${NC}"
    fi
    
    # Remove legacy current_user file
    CURRENT_USER_FILE="$DB_DIR/current_user"
    if [ -f "$CURRENT_USER_FILE" ]; then
        rm "$CURRENT_USER_FILE"
        echo -e "${GREEN}✓ Removed legacy user file${NC}"
    fi
    
    # Create directory if not exists
    mkdir -p "$DB_DIR"
    
    echo -e "${GREEN}✓ Fresh database will be created on first use${NC}"
}

# Migrate legacy database
migrate_legacy_database() {
    if [ -f "$OLD_DB_FILE" ] && [ ! -f "$DB_FILE" ]; then
        echo -e "\n${YELLOW}→ Migrating legacy database...${NC}"
        mkdir -p "$DB_DIR"
        cp "$OLD_DB_FILE" "$DB_FILE"
        echo -e "${GREEN}✓ Database migrated to: $DB_FILE${NC}"
    fi
}

# Ask about demo data
ask_demo_data() {
    echo -e "\n${BLUE}Would you like to create demo user and projects?${NC}"
    echo "  This will create:"
    echo "  - Demo user (demo@example.com)"
    echo "  - 3 sample projects"
    echo ""
    read -p "Create demo data? (y/N): " create_demo
    
    case $create_demo in
        [Yy]*)
            export SITR_CREATE_DEMO_DATA="true"
            echo -e "${GREEN}✓ Demo data will be created on first start${NC}"
            ;;
        *)
            export SITR_CREATE_DEMO_DATA="false"
            echo -e "${YELLOW}→ Skipping demo data${NC}"
            ;;
    esac
}

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Darwin*)    echo "macos";;
        Linux*)     echo "linux";;
        CYGWIN*|MINGW*|MSYS*) echo "windows";;
        *)          echo "unknown";;
    esac
}

OS=$(detect_os)

echo -e "${GREEN}🚀 SITR Installation Script${NC}"
echo -e "${GREEN}======================================${NC}\n"

# Check Python version
check_python() {
    echo -e "${YELLOW}→ Checking Python installation...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}✗ Python 3 is not installed${NC}"
        echo -e "${YELLOW}  Please install Python 3.10 or higher first${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Found Python $PYTHON_VERSION${NC}"
    
    # Check if version is >= 3.10
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
        echo -e "${RED}✗ Python 3.10 or higher is required (found $PYTHON_VERSION)${NC}"
        exit 1
    fi
}

# Install using pip
install_sitr() {
    echo -e "\n${YELLOW}→ Installing SITR...${NC}"
    
    # Install in editable mode for development, or regular mode for production
    if [ "$1" == "--dev" ]; then
        echo -e "${YELLOW}  Installing in development mode...${NC}"
        pip3 install -e .
    else
        echo -e "${YELLOW}  Installing SITR package...${NC}"
        pip3 install .
    fi
    
    echo -e "${GREEN}✓ SITR installed successfully${NC}"
}

# Verify installation
verify_installation() {
    echo -e "\n${YELLOW}→ Verifying installation...${NC}"
    
    if command -v sitr &> /dev/null; then
        echo -e "${GREEN}✓ SITR command is available${NC}"
        
        # Test the command
        echo -e "\n${YELLOW}→ Testing SITR...${NC}"
        sitr --help > /dev/null 2>&1 && echo -e "${GREEN}✓ SITR is working correctly${NC}"
    else
        echo -e "${YELLOW}⚠ SITR command not found in PATH${NC}"
        echo -e "${YELLOW}  You may need to add pip's bin directory to your PATH${NC}"
        
        case $OS in
            macos|linux)
                echo -e "${YELLOW}  Try adding this to your ~/.bashrc or ~/.zshrc:${NC}"
                echo -e "${YELLOW}  export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
                ;;
            windows)
                echo -e "${YELLOW}  The Scripts directory should be in your PATH${NC}"
                ;;
        esac
    fi
}

# Main installation flow
main() {
    local INSTALL_MODE="$1"
    
    echo -e "${YELLOW}OS detected: $OS${NC}\n"
    
    check_python
    
    # Determine installation mode
    if [ "$INSTALL_MODE" == "--fresh" ]; then
        echo -e "${BLUE}Fresh Installation Mode${NC}\n"
        backup_database
        setup_fresh_database
        ask_demo_data
        install_sitr
        
    elif [ "$INSTALL_MODE" == "--update" ]; then
        echo -e "${BLUE}Update Mode${NC}\n"
        if check_database; then
            backup_database
            echo -e "${GREEN}✓ Keeping existing database${NC}"
        else
            echo -e "${YELLOW}⚠ No existing database found${NC}"
        fi
        install_sitr
        
    elif [ "$INSTALL_MODE" == "--dev" ]; then
        echo -e "${BLUE}Development Mode${NC}\n"
        if check_database; then
            backup_database
            echo -e "${GREEN}✓ Keeping existing database${NC}"
        fi
        install_sitr "--dev"
        
    else
        # Interactive mode
        if check_database; then
            echo -e "${BLUE}Existing database detected${NC}\n"
            echo "Choose installation type:"
            echo "  1) Update (keep existing database)"
            echo "  2) Fresh install (backup and reset database)"
            echo "  3) Development mode (keep database, editable install)"
            read -p "Enter choice (1-3): " choice
            
            case $choice in
                1)
                    backup_database
                    echo -e "${GREEN}✓ Keeping existing database${NC}"
                    install_sitr
                    ;;
                2)
                    backup_database
                    setup_fresh_database
                    ask_demo_data
                    install_sitr
                    ;;
                3)
                    backup_database
                    echo -e "${GREEN}✓ Keeping existing database${NC}"
                    install_sitr "--dev"
                    ;;
                *)
                    echo -e "${RED}Invalid choice${NC}"
                    exit 1
                    ;;
            esac
        else
            echo -e "${BLUE}No existing database found - Fresh Installation${NC}\n"
            echo "Choose installation type:"
            echo "  1) Regular installation"
            echo "  2) Development installation (editable)"
            read -p "Enter choice (1 or 2): " choice
            
            case $choice in
                1)
                    ask_demo_data
                    install_sitr
                    ;;
                2)
                    ask_demo_data
                    install_sitr "--dev"
                    ;;
                *)
                    echo -e "${RED}Invalid choice${NC}"
                    exit 1
                    ;;
            esac
        fi
    fi
    
    migrate_legacy_database
    
    # Initialize database tables
    echo -e "\n${YELLOW}→ Initializing database tables...${NC}"
    sitr init-db
    
    verify_installation
    
    echo -e "\n${GREEN}======================================${NC}"
    echo -e "${GREEN}✓ Installation complete!${NC}"
    echo -e "\n${YELLOW}Database location:${NC} $DB_FILE"
    
    if [ "$SITR_CREATE_DEMO_DATA" == "true" ]; then
        echo -e "\n${YELLOW}Demo data will be created on first start${NC}"
        echo -e "${YELLOW}Demo user: demo@example.com${NC}"
    fi
    
    echo -e "\n${YELLOW}Quick start:${NC}"
    if [ "$SITR_CREATE_DEMO_DATA" != "true" ]; then
        echo -e "  sitr user add -f John -l Doe -e john@example.com"
        echo -e "  sitr user select -e john@example.com"
    else
        echo -e "  sitr user select -e demo@example.com"
    fi
    echo -e "  sitr start-day"
    echo -e "\n${YELLOW}For more information:${NC}"
    echo -e "  sitr --help"
    echo -e "  cat QUICKSTART.md"
    echo -e "\n${GREEN}Happy time tracking! 🎯${NC}\n"
}

# Handle script arguments
case "$1" in
    --uninstall)
        echo -e "${YELLOW}→ Uninstalling SITR...${NC}"
        pip3 uninstall -y sitr
        echo -e "${GREEN}✓ SITR uninstalled${NC}"
        echo -e "${YELLOW}Note: Database at $DB_FILE was not removed${NC}"
        exit 0
        ;;
    --fresh|--update|--dev)
        main "$1"
        ;;
    --help|-h)
        echo "SITR Installation Script"
        echo ""
        echo "Usage:"
        echo "  ./install.sh              Interactive installation"
        echo "  ./install.sh --fresh      Fresh install (backup & reset DB)"
        echo "  ./install.sh --update     Update (keep existing DB)"
        echo "  ./install.sh --dev        Development mode (editable install)"
        echo "  ./install.sh --uninstall  Remove SITR"
        echo "  ./install.sh --help       Show this help"
        exit 0
        ;;
    *)
        main
        ;;
esac
