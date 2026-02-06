#!/bin/bash
#
# LogShackBaby Database Reset Script
# This script resets the PostgreSQL database to a fresh install
#
# Usage: ./reset-database.sh
# Use with caution: This will delete all data!
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DB_NAME="logshackbaby"
DB_USER="logshackbaby"
DB_PASSWORD="${DB_PASSWORD:-logshackbaby_password}"
CONTAINER_NAME="logshackbaby-db"

echo -e "${YELLOW}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║  LogShackBaby Database Reset Script                   ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running in Docker environment
if docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${GREEN}✓ Docker container detected${NC}"
    USE_DOCKER=true
elif systemctl is-active --quiet postgresql 2>/dev/null || pg_isready -U $DB_USER -d $DB_NAME 2>/dev/null; then
    echo -e "${GREEN}✓ Local PostgreSQL installation detected${NC}"
    USE_DOCKER=false
else
    echo -e "${RED}✗ No PostgreSQL instance found${NC}"
    echo "Please ensure either Docker containers are running or PostgreSQL is installed locally."
    exit 1
fi

# Confirmation prompt
echo ""
echo -e "${RED}WARNING: This will permanently delete ALL data in the database!${NC}"
echo ""
echo "This includes:"
echo "  - All user accounts"
echo "  - All log entries"
echo "  - All API keys"
echo "  - All sessions"
echo "  - All uploaded logs"
echo "  - All custom report templates"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}Database reset cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Proceeding with database reset...${NC}"
echo ""

# Function to execute SQL in Docker
exec_docker_sql() {
    docker exec -i $CONTAINER_NAME psql -U $DB_USER -d postgres -c "$1" 2>&1
}

# Function to execute SQL locally
exec_local_sql() {
    PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d postgres -c "$1" 2>&1
}

if [ "$USE_DOCKER" = true ]; then
    echo "Step 1/4: Terminating active connections..."
    exec_docker_sql "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" > /dev/null || true
    
    echo "Step 2/4: Dropping database..."
    exec_docker_sql "DROP DATABASE IF EXISTS $DB_NAME;"
    
    echo "Step 3/4: Creating fresh database..."
    exec_docker_sql "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    
    echo "Step 4/4: Initializing database schema..."
    # Wait a moment for database to be ready
    sleep 2
    docker exec -i logshackbaby-app flask --app app init-db
else
    echo "Step 1/4: Terminating active connections..."
    exec_local_sql "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" > /dev/null || true
    
    echo "Step 2/4: Dropping database..."
    exec_local_sql "DROP DATABASE IF EXISTS $DB_NAME;"
    
    echo "Step 3/4: Creating fresh database..."
    exec_local_sql "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    
    echo "Step 4/4: Initializing database schema..."
    # Navigate to backend directory and initialize
    cd backend
    export DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
    flask --app app init-db
    cd ..
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Database successfully reset to fresh install!         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "The database has been reset with:"
echo "  ✓ Clean schema"
echo "  ✓ Default report templates"
echo "  ✓ No user accounts (you can now create new users)"
echo ""
echo -e "${YELLOW}Note: You may need to restart the application if it's running.${NC}"
