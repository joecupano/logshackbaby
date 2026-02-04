#!/bin/bash

# LogShackBaby Docker Startup Script
# Starts the application using Docker containers

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
echo -e "${BLUE}  (Docker)${NC}"
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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    print_info "Run ./install-docker.sh to install all prerequisites"
    exit 1
fi

# Check if user can run docker
if ! docker ps &> /dev/null; then
    print_error "Cannot connect to Docker daemon"
    print_info "You may need to:"
    echo "   1. Start Docker: sudo systemctl start docker"
    echo "   2. Add your user to docker group: sudo usermod -aG docker $USER"
    echo "   3. Log out and back in"
    exit 1
fi

print_success "Docker is available"

# Determine compose command
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    print_error "Docker Compose is not installed"
    print_info "Run ./install-docker.sh to install all prerequisites"
    exit 1
fi

print_success "Docker Compose is available"

# Check for .env file
if [ ! -f .env ]; then
    print_error ".env file not found"
    print_info "Creating .env from template..."
    
    if [ ! -f .env.example ]; then
        print_error ".env.example not found"
        print_info "Run ./install-docker.sh to set up the environment properly"
        exit 1
    fi
    
    cp .env.example .env
    
    # Generate secrets
    if command -v python3 &> /dev/null; then
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
        DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))" 2>/dev/null || openssl rand -base64 24)
    else
        SECRET_KEY=$(openssl rand -hex 32)
        DB_PASSWORD=$(openssl rand -base64 24)
    fi
    
    # Update .env file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|DB_PASSWORD=.*|DB_PASSWORD=${DB_PASSWORD}|" .env
        sed -i '' "s|SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|" .env
    else
        sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=${DB_PASSWORD}|" .env
        sed -i "s|SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|" .env
    fi
    
    print_success "Created .env file with secure passwords"
fi

print_success ".env file exists"
echo ""

# Check if containers are already running
RUNNING=$($COMPOSE_CMD ps -q 2>/dev/null | wc -l)
if [ "$RUNNING" -gt 0 ]; then
    print_warning "Containers are already running"
    echo ""
    read -p "Do you want to restart them? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Restarting containers..."
        $COMPOSE_CMD restart
        print_success "Containers restarted"
    else
        print_info "Keeping existing containers running"
    fi
else
    # Start containers
    print_info "Starting LogShackBaby containers..."
    echo ""
    
    if $COMPOSE_CMD up -d; then
        print_success "Containers started successfully"
    else
        print_error "Failed to start containers"
        print_info "Try running: $COMPOSE_CMD logs"
        exit 1
    fi
fi

echo ""

# Wait for services to be ready
print_info "Waiting for services to initialize..."
echo -n "   "
for i in {1..10}; do
    echo -n "."
    sleep 1
done
echo ""
echo ""

# Check container status
print_info "Checking container status..."
$COMPOSE_CMD ps
echo ""

# Try to detect the application port
APP_PORT=80
if curl -s -o /dev/null -w "%{http_code}" http://localhost:80 2>/dev/null | grep -q "200\|302\|301"; then
    APP_PORT=80
elif curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null | grep -q "200\|302\|301"; then
    APP_PORT=5000
fi

# Verify application is responding
if curl -s -o /dev/null -w "%{http_code}" http://localhost:$APP_PORT 2>/dev/null | grep -q "200\|302\|301"; then
    print_success "Application is responding"
else
    print_warning "Application may still be starting up"
    print_info "Wait a few seconds and check: http://localhost:$APP_PORT"
fi

echo ""

# Display success message
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  ✅ LogShackBaby is Running!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${BLUE}📍 Access the application:${NC}"
echo "   🌐 http://localhost:$APP_PORT"
if [ "$(hostname -I 2>/dev/null | awk '{print $1}')" ]; then
    echo "   🌐 http://$(hostname -I | awk '{print $1}'):$APP_PORT"
fi
echo ""
echo -e "${BLUE}📊 Useful commands:${NC}"
echo "   View logs:        $COMPOSE_CMD logs -f"
echo "   Stop services:    ./stop-docker.sh"
echo "   Restart services: $COMPOSE_CMD restart"
echo "   View status:      $COMPOSE_CMD ps"
echo ""
echo -e "${GREEN}73! 📻${NC}"
echo ""
