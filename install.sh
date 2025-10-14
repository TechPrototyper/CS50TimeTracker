#!/bin/bash
#
# SITR Installation Script
# Supports macOS, Linux, and Windows (via Git Bash/WSL)
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
    echo -e "${YELLOW}OS detected: $OS${NC}\n"
    
    check_python
    
    # Ask for installation type
    if [ "$1" == "--dev" ]; then
        install_sitr "--dev"
    else
        echo -e "\n${YELLOW}Choose installation type:${NC}"
        echo "  1) Regular installation (recommended)"
        echo "  2) Development installation (editable)"
        read -p "Enter choice (1 or 2): " choice
        
        case $choice in
            1) install_sitr ;;
            2) install_sitr "--dev" ;;
            *) echo -e "${RED}Invalid choice${NC}"; exit 1 ;;
        esac
    fi
    
    verify_installation
    
    echo -e "\n${GREEN}======================================${NC}"
    echo -e "${GREEN}✓ Installation complete!${NC}"
    echo -e "\n${YELLOW}Quick start:${NC}"
    echo -e "  sitr user add -f John -l Doe -e john@example.com"
    echo -e "  sitr user select -e john@example.com"
    echo -e "  sitr start-day"
    echo -e "\n${YELLOW}For more information:${NC}"
    echo -e "  sitr --help"
    echo -e "  cat QUICKSTART.md"
    echo -e "\n${GREEN}Happy time tracking! 🎯${NC}\n"
}

# Handle script arguments
if [ "$1" == "--uninstall" ]; then
    echo -e "${YELLOW}→ Uninstalling SITR...${NC}"
    pip3 uninstall -y sitr
    echo -e "${GREEN}✓ SITR uninstalled${NC}"
    exit 0
fi

main "$@"
