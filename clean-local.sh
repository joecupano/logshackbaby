#!/bin/bash

# LogShackBaby Local Cleanup Script
# Completely removes LogShackBaby including PostgreSQL database and user
# WARNING: This will DELETE all data permanently!

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Banner
echo -e "${RED}=========================================${NC}"
echo -e "${RED}  LogShackBaby - Complete Cleanup${NC}"
echo -e "${RED}  ⚠️  WARNING: DESTRUCTIVE OPERATION ⚠️${NC}"
echo -e "${RED}=========================================${NC}"
echo ""

# Check if running with sudo
if [ "$EUID" -eq 0 ]; then 
    print_warning "Please do not run this script with sudo or as root"
    print_info "The script will prompt for sudo password when needed"
    exit 1
fi

# Get installation directory
INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$INSTALL_DIR"

# Final warning
print_warning "This script will permanently delete:"
echo "   • LogShackBaby database and all log data"
echo "   • PostgreSQL user 'logshackbaby'"
echo "   • Python virtual environment"
echo "   • Environment configuration files"
echo "   • Systemd service (if installed)"
echo "   • PID files and temporary data"
echo ""
print_error "This action CANNOT be undone!"
echo ""
read -p "Are you absolutely sure you want to continue? (type 'yes' to confirm): " -r
echo ""

if [ "$REPLY" != "yes" ]; then
    print_info "Cleanup cancelled"
    exit 0
fi

echo ""
echo -e "${BLUE}Starting cleanup process...${NC}"
echo ""

# Step 1: Stop running services
echo -e "${BLUE}Step 1: Stopping running services...${NC}"
echo ""

# Check if running via systemd
if sudo systemctl is-active --quiet logshackbaby 2>/dev/null; then
    print_info "Stopping systemd service..."
    sudo systemctl stop logshackbaby 2>/dev/null || true
    print_success "Systemd service stopped"
fi

# Check if running on port 5000
if command -v lsof &> /dev/null && lsof -i :5000 &> /dev/null; then
    print_info "Stopping process on port 5000..."
    PID=$(lsof -ti :5000)
    kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null || true
    sleep 1
    print_success "Application stopped"
fi

echo ""

# Step 2: Remove systemd service
echo -e "${BLUE}Step 2: Removing systemd service...${NC}"
echo ""

if [ -f /etc/systemd/system/logshackbaby.service ]; then
    print_info "Disabling and removing systemd service..."
    sudo systemctl disable logshackbaby 2>/dev/null || true
    sudo rm -f /etc/systemd/system/logshackbaby.service
    sudo systemctl daemon-reload
    print_success "Systemd service removed"
else
    print_info "No systemd service found (skipping)"
fi

echo ""

# Step 3: Drop PostgreSQL database and user
echo -e "${BLUE}Step 3: Removing PostgreSQL database and user...${NC}"
echo ""

DB_NAME="logshackbaby"
DB_USER="logshackbaby"

if command -v psql &> /dev/null; then
    print_info "Checking PostgreSQL status..."
    
    # Make sure PostgreSQL is running
    if ! sudo systemctl is-active --quiet postgresql 2>/dev/null; then
        print_warning "PostgreSQL is not running, attempting to start..."
        sudo systemctl start postgresql 2>/dev/null || true
        sleep 2
    fi
    
    # Drop database and user
    print_info "Dropping database '$DB_NAME' and user '$DB_USER'..."
    sudo -u postgres psql <<EOF 2>/dev/null || true
-- Terminate existing connections
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '$DB_NAME'
  AND pid <> pg_backend_pid();

-- Drop database
DROP DATABASE IF EXISTS $DB_NAME;

-- Drop user
DROP USER IF EXISTS $DB_USER;
EOF
    
    if [ $? -eq 0 ]; then
        print_success "Database and user removed successfully"
    else
        print_warning "Database cleanup encountered issues (may not exist)"
    fi
else
    print_warning "PostgreSQL not found (skipping database cleanup)"
fi

echo ""

# Step 4: Remove Python virtual environment
echo -e "${BLUE}Step 4: Removing Python virtual environment...${NC}"
echo ""

if [ -d "$INSTALL_DIR/venv" ]; then
    print_info "Removing virtual environment..."
    rm -rf "$INSTALL_DIR/venv"
    print_success "Virtual environment removed"
else
    print_info "No virtual environment found (skipping)"
fi

echo ""

# Step 5: Remove configuration files
echo -e "${BLUE}Step 5: Removing configuration files...${NC}"
echo ""

# Remove .env file
if [ -f "$INSTALL_DIR/backend/.env" ]; then
    print_info "Removing .env configuration..."
    rm -f "$INSTALL_DIR/backend/.env"
    print_success ".env file removed"
else
    print_info "No .env file found (skipping)"
fi

# Remove PID file if it exists
if [ -f "$INSTALL_DIR/backend/app.pid" ]; then
    print_info "Removing PID file..."
    rm -f "$INSTALL_DIR/backend/app.pid"
    print_success "PID file removed"
fi

echo ""

# Step 6: Remove Python cache and temporary files
echo -e "${BLUE}Step 6: Cleaning up Python cache and temporary files...${NC}"
echo ""

print_info "Removing Python cache files..."
find "$INSTALL_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$INSTALL_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$INSTALL_DIR" -type f -name "*.pyo" -delete 2>/dev/null || true
find "$INSTALL_DIR" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
print_success "Python cache files cleaned"

echo ""

# Optional: Remove PostgreSQL completely
echo -e "${BLUE}Step 7: PostgreSQL removal (optional)...${NC}"
echo ""

print_warning "PostgreSQL is still installed on your system"
print_info "If you want to completely remove PostgreSQL, you have two options:"
echo ""
read -p "Do you want to remove PostgreSQL completely? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_warning "This will remove PostgreSQL and ALL databases on the system!"
    read -p "Are you sure? (type 'yes' to confirm): " -r
    echo ""
    
    if [ "$REPLY" = "yes" ]; then
        # Detect OS
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
        fi
        
        print_info "Stopping PostgreSQL service..."
        sudo systemctl stop postgresql 2>/dev/null || true
        sudo systemctl disable postgresql 2>/dev/null || true
        
        case $OS in
            ubuntu|debian|raspbian)
                print_info "Removing PostgreSQL packages (Debian/Ubuntu)..."
                sudo apt-get remove --purge -y postgresql* 2>/dev/null || true
                sudo apt-get autoremove -y 2>/dev/null || true
                ;;
            fedora|centos|rhel)
                print_info "Removing PostgreSQL packages (Fedora/RHEL)..."
                sudo dnf remove -y postgresql* 2>/dev/null || true
                sudo dnf autoremove -y 2>/dev/null || true
                ;;
            *)
                print_warning "Unknown OS, please remove PostgreSQL manually"
                ;;
        esac
        
        # Remove PostgreSQL data directory
        if [ -d /var/lib/postgresql ]; then
            print_info "Removing PostgreSQL data directory..."
            sudo rm -rf /var/lib/postgresql
        fi
        
        # Remove PostgreSQL configuration
        if [ -d /etc/postgresql ]; then
            print_info "Removing PostgreSQL configuration..."
            sudo rm -rf /etc/postgresql
        fi
        
        print_success "PostgreSQL removed completely"
    else
        print_info "Keeping PostgreSQL installed"
    fi
else
    print_info "Keeping PostgreSQL installed"
    print_info "You can remove it manually later with:"
    echo "   Debian/Ubuntu: sudo apt-get remove --purge postgresql postgresql-contrib"
    echo "   Fedora/RHEL:   sudo dnf remove postgresql postgresql-server"
fi

echo ""

# Cleanup complete
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  ✅ Cleanup Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

print_success "LogShackBaby has been completely removed"
echo ""
print_info "Summary of removed items:"
echo "   ✓ Database 'logshackbaby' and user 'logshackbaby'"
echo "   ✓ Python virtual environment"
echo "   ✓ Configuration files (.env)"
echo "   ✓ Systemd service"
echo "   ✓ Python cache files"
if [[ $REPLY =~ ^[Yy]$ ]] && [ "$REPLY" = "yes" ]; then
    echo "   ✓ PostgreSQL (complete removal)"
fi
echo ""

print_info "Application source code remains in: $INSTALL_DIR"
print_info "You can reinstall LogShackBaby anytime by running: ./install-local.sh"
echo ""

print_warning "Note: If you want to remove the source code as well, run:"
echo "   cd .. && rm -rf $(basename $INSTALL_DIR)"
echo ""

echo -e "${BLUE}73! 📻${NC}"
echo ""
