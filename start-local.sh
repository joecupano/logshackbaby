#!/bin/bash

# LogShackBaby Local Startup Script
# Starts the application locally (without Docker)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  LogShackBaby - Starting Application${NC}"
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

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found"
    print_info "Please run ./install.sh first to set up the environment"
    exit 1
fi

print_success "Virtual environment found"

# Check if PostgreSQL is running
if ! sudo systemctl is-active --quiet postgresql; then
    print_warning "PostgreSQL is not running"
    print_info "Starting PostgreSQL..."
    sudo systemctl start postgresql
    sleep 2
fi

if sudo systemctl is-active --quiet postgresql; then
    print_success "PostgreSQL is running"
else
    print_error "Failed to start PostgreSQL"
    exit 1
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    print_error "Configuration file backend/.env not found"
    print_info "Please run ./install.sh first to set up the environment"
    exit 1
fi

print_success "Configuration file found"

# Activate virtual environment
source venv/bin/activate

# Check if there's already a running instance
if lsof -i :5000 &> /dev/null; then
    print_warning "Port 5000 is already in use"
    echo ""
    read -p "Do you want to stop the existing process? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Stopping existing process..."
        PID=$(lsof -ti :5000)
        kill $PID 2>/dev/null || true
        sleep 2
    else
        print_error "Cannot start - port 5000 is in use"
        exit 1
    fi
fi

echo ""
print_info "Starting LogShackBaby..."
echo ""

# Change to backend directory
cd backend

# Start the application
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  Application Starting...${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo -e "${GREEN}📍 Access LogShackBaby at:${NC}"
echo "   🌐 http://localhost:5000"
if [ "$(hostname -I 2>/dev/null | awk '{print $1}')" ]; then
    echo "   🌐 http://$(hostname -I | awk '{print $1}'):5000"
fi
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""
echo -e "${BLUE}=========================================${NC}"
echo ""

# Run with gunicorn for production
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 --access-logfile - --error-logfile - app:app
