#!/bin/bash

# LogShackBaby Docker Stop Script
# Stops the Docker containers

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

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  LogShackBaby - Stopping Application${NC}"
echo -e "${BLUE}  (Docker)${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Determine compose command
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    print_error "Docker Compose is not installed"
    exit 1
fi

# Check if containers are running
RUNNING=$($COMPOSE_CMD ps -q 2>/dev/null | wc -l)
if [ "$RUNNING" -eq 0 ]; then
    print_info "No containers are currently running"
    exit 0
fi

print_info "Stopping LogShackBaby containers..."
echo ""

# Ask if user wants to remove volumes
read -p "Do you want to remove data volumes (will delete all data)? (y/N): " -n 1 -r
echo ""
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Stopping containers and removing volumes..."
    if $COMPOSE_CMD down -v; then
        print_success "Containers stopped and volumes removed"
        print_warning "All data has been deleted!"
    else
        print_error "Failed to stop containers"
        exit 1
    fi
else
    print_info "Stopping containers (data will be preserved)..."
    if $COMPOSE_CMD down; then
        print_success "Containers stopped"
        print_info "Data volumes preserved - data will be available when you restart"
    else
        print_error "Failed to stop containers"
        exit 1
    fi
fi

echo ""
print_success "LogShackBaby stopped"
echo ""
echo -e "${BLUE}To start again, run:${NC}"
echo "   ./start-docker.sh"
echo ""
