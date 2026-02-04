#!/bin/bash

# LogShackBaby Local Stop Script
# Stops the locally running application

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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  LogShackBaby - Stopping Application${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Check if running via systemd
if sudo systemctl is-active --quiet logshackbaby 2>/dev/null; then
    print_info "Stopping systemd service..."
    sudo systemctl stop logshackbaby
    print_success "Systemd service stopped"
fi

# Check if running on port 5000
if lsof -i :5000 &> /dev/null; then
    print_info "Stopping process on port 5000..."
    PID=$(lsof -ti :5000)
    kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null
    sleep 1
    
    if ! lsof -i :5000 &> /dev/null; then
        print_success "Application stopped"
    else
        print_error "Failed to stop application"
        exit 1
    fi
else
    print_info "No application running on port 5000"
fi

echo ""
print_success "LogShackBaby stopped"
echo ""
