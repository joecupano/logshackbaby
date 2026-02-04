#!/bin/bash

# LogShackBaby Local Installation Script
# This script performs a complete local installation of LogShackBaby (without Docker)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  LogShackBaby - Local Installation${NC}"
echo -e "${BLUE}  Amateur Radio Log Server${NC}"
echo -e "${BLUE}  (Native - No Docker)${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

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

# Check if running with sudo
if [ "$EUID" -eq 0 ]; then 
    print_warning "Please do not run this script with sudo or as root"
    print_info "The script will prompt for sudo password when needed"
    exit 1
fi

# Save installation directory
INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$INSTALL_DIR"

# Step 1: Check and install prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    OS_VERSION=$VERSION_ID
else
    print_error "Cannot detect operating system"
    exit 1
fi

print_info "Detected OS: $OS"

# Check for Python 3
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python 3 is installed (version $PYTHON_VERSION)"
else
    print_error "Python 3 is not installed"
    print_info "Installing Python 3..."
    
    case $OS in
        ubuntu|debian|raspbian)
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv python3-dev
            ;;
        fedora|centos|rhel)
            sudo dnf install -y python3 python3-pip python3-devel
            ;;
        *)
            print_error "Unsupported OS: $OS"
            exit 1
            ;;
    esac
    PYTHON_CMD="python3"
    print_success "Python 3 installed successfully"
fi

# Check for pip
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    print_info "Installing pip..."
    case $OS in
        ubuntu|debian|raspbian)
            sudo apt-get install -y python3-pip
            ;;
        fedora|centos|rhel)
            sudo dnf install -y python3-pip
            ;;
    esac
fi
print_success "pip is available"

# Check for PostgreSQL
if ! command -v psql &> /dev/null; then
    print_error "PostgreSQL is not installed"
    print_info "Installing PostgreSQL..."
    
    case $OS in
        ubuntu|debian|raspbian)
            sudo apt-get update
            sudo apt-get install -y postgresql postgresql-contrib libpq-dev
            ;;
        fedora|centos|rhel)
            sudo dnf install -y postgresql-server postgresql-contrib postgresql-devel
            sudo postgresql-setup --initdb
            ;;
        *)
            print_error "Unsupported OS: $OS"
            exit 1
            ;;
    esac
    
    # Start and enable PostgreSQL
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    print_success "PostgreSQL installed successfully"
else
    print_success "PostgreSQL is installed"
    
    # Make sure PostgreSQL is running
    if ! sudo systemctl is-active --quiet postgresql; then
        print_info "Starting PostgreSQL..."
        sudo systemctl start postgresql
    fi
fi

# Check for other dependencies
case $OS in
    ubuntu|debian|raspbian)
        print_info "Installing additional dependencies..."
        sudo apt-get install -y build-essential libssl-dev libffi-dev
        ;;
    fedora|centos|rhel)
        print_info "Installing additional dependencies..."
        sudo dnf install -y gcc openssl-devel libffi-devel
        ;;
esac

print_success "All system prerequisites installed"
echo ""

# Step 2: Set up PostgreSQL database
echo -e "${BLUE}Step 2: Setting up PostgreSQL database...${NC}"
echo ""

# Generate database password
DB_NAME="logshackbaby"
DB_USER="logshackbaby"
DB_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-25)

print_info "Creating database and user..."

# Create database and user
sudo -u postgres psql <<EOF
-- Drop existing database and user if they exist (for clean reinstall)
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;

-- Create user
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Create database
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

if [ $? -eq 0 ]; then
    print_success "Database created successfully"
else
    print_error "Failed to create database"
    exit 1
fi

echo ""

# Step 3: Configure environment
echo -e "${BLUE}Step 3: Configuring environment...${NC}"
echo ""

# Generate secret key
SECRET_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_hex(32))")

# Create .env file for backend
print_info "Creating .env file..."
cat > backend/.env << EOF
# LogShackBaby Configuration
# Auto-generated on $(date)

# Database configuration
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_NAME=$DB_NAME
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME

# Flask secret key
SECRET_KEY=$SECRET_KEY

# Flask environment
FLASK_ENV=production

# Port configuration (change if needed)
PORT=5000
EOF

print_success "Environment configuration created"
echo ""

# Step 4: Create Python virtual environment
echo -e "${BLUE}Step 4: Setting up Python virtual environment...${NC}"
echo ""

# Remove old venv if it exists
if [ -d "venv" ]; then
    print_warning "Removing old virtual environment..."
    rm -rf venv
fi

print_info "Creating virtual environment..."
$PYTHON_CMD -m venv venv

if [ ! -d "venv" ]; then
    print_error "Failed to create virtual environment"
    exit 1
fi

print_success "Virtual environment created"

# Activate virtual environment
source venv/bin/activate

print_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

if [ $? -eq 0 ]; then
    print_success "Python dependencies installed successfully"
else
    print_error "Failed to install Python dependencies"
    exit 1
fi

echo ""

# Step 5: Initialize database
echo -e "${BLUE}Step 5: Initializing database schema...${NC}"
echo ""

print_info "Creating database tables..."
cd backend
$PYTHON_CMD -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created!')
"

if [ $? -eq 0 ]; then
    print_success "Database schema initialized"
else
    print_error "Failed to initialize database schema"
    cd ..
    exit 1
fi

cd ..
echo ""

# Step 6: Create systemd service (optional)
echo -e "${BLUE}Step 6: Creating systemd service...${NC}"
echo ""

read -p "Would you like to create a systemd service for automatic startup? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Creating systemd service..."
    
    # Create service file
    sudo tee /etc/systemd/system/logshackbaby.service > /dev/null <<EOF
[Unit]
Description=LogShackBaby Amateur Radio Log Server
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR/backend
Environment="PATH=$INSTALL_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$INSTALL_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    sudo systemctl daemon-reload
    sudo systemctl enable logshackbaby
    
    print_success "Systemd service created and enabled"
    print_info "You can manage the service with:"
    echo "   Start:   sudo systemctl start logshackbaby"
    echo "   Stop:    sudo systemctl stop logshackbaby"
    echo "   Status:  sudo systemctl status logshackbaby"
    echo "   Logs:    sudo journalctl -u logshackbaby -f"
else
    print_info "Skipping systemd service creation"
    print_info "You can start the app manually with: ./start-local.sh"
fi

echo ""

# Installation complete
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  ✅ Installation Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
print_info "Installation directory: $INSTALL_DIR"
print_info "Database: $DB_NAME (user: $DB_USER)"
print_info "Virtual environment: $INSTALL_DIR/venv"
echo ""
echo -e "${BLUE}📍 To start LogShackBaby:${NC}"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   sudo systemctl start logshackbaby"
    echo "   OR"
fi
echo "   ./start-local.sh"
echo ""
echo -e "${BLUE}📍 Access LogShackBaby:${NC}"
echo "   🌐 http://localhost:5000"
if [ "$(hostname -I 2>/dev/null | awk '{print $1}')" ]; then
    echo "   🌐 http://$(hostname -I | awk '{print $1}'):5000"
fi
echo ""
echo -e "${BLUE}🎉 Next steps:${NC}"
echo "   1. Start the application: ./start-local.sh"
echo "   2. Open http://localhost:5000 in your browser"
echo "   3. Click 'Register' to create an account"
echo "   4. The first user becomes the system administrator (sysop)"
echo "   5. Enable 2FA in Settings (recommended)"
echo "   6. Create an API key in the API Keys tab"
echo "   7. Upload your ADIF logs!"
echo ""
echo -e "${BLUE}📖 Documentation:${NC}"
echo "   Configuration: backend/.env"
echo "   Database: PostgreSQL on localhost:5432"
echo "   Logs: Use './start-local.sh' and check terminal output"
echo ""
echo -e "${GREEN}73! 📻${NC}"
echo ""
