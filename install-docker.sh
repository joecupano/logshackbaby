#!/bin/bash

# LogShackBaby Docker Installation Script
# This script performs a complete Docker-based installation of LogShackBaby

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  LogShackBaby - Docker Installation${NC}"
echo -e "${BLUE}  Amateur Radio Log Server${NC}"
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

# Step 1: Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    echo ""
    print_info "Installing Docker..."
    echo ""
    
    # Detect OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    else
        print_error "Cannot detect operating system"
        exit 1
    fi
    
    case $OS in
        ubuntu|debian|raspbian)
            sudo apt-get update
            sudo apt-get install -y ca-certificates curl gnupg lsb-release
            sudo install -m 0755 -d /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/$OS/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            sudo chmod a+r /etc/apt/keyrings/docker.gpg
            echo \
              "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS \
              $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
        fedora|centos|rhel)
            sudo dnf -y install dnf-plugins-core
            sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
            sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            sudo systemctl start docker
            sudo systemctl enable docker
            ;;
        *)
            print_error "Unsupported OS: $OS"
            print_info "Please install Docker manually: https://docs.docker.com/get-docker/"
            exit 1
            ;;
    esac
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    print_success "Docker installed successfully"
    print_warning "You may need to log out and back in for Docker group permissions to take effect"
    print_info "After logging back in, run this script again"
    exit 0
else
    print_success "Docker is installed"
fi

# Check if user is in docker group
if ! groups | grep -q docker; then
    print_warning "Your user is not in the docker group"
    print_info "Adding user to docker group..."
    sudo usermod -aG docker $USER
    print_warning "You need to log out and back in for group changes to take effect"
    print_info "After logging back in, run this script again"
    exit 0
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    print_error "Docker Compose is not installed"
    echo ""
    print_info "Installing Docker Compose..."
    
    # Try to use docker compose plugin first
    if docker compose version &> /dev/null 2>&1; then
        print_success "Docker Compose (plugin) is available"
    else
        # Install standalone docker-compose
        COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d'"' -f4)
        sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        print_success "Docker Compose installed successfully"
    fi
else
    print_success "Docker Compose is installed"
fi

# Check for Python or OpenSSL (for secret generation)
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

if ! command -v openssl &> /dev/null && [ -z "$PYTHON_CMD" ]; then
    print_warning "Neither Python nor OpenSSL found. Installing OpenSSL for secret generation..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y openssl
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y openssl
    fi
fi

echo ""

# Step 2: Configure environment
echo -e "${BLUE}Step 2: Configuring environment...${NC}"
echo ""

if [ ! -f .env ]; then
    print_info "Creating .env file from template..."
    
    if [ ! -f .env.example ]; then
        print_warning ".env.example file not found, creating default..."
        cat > .env.example << 'EOF'
# Environment variables for docker-compose
# Copy this to .env and update with your secure values

# Database password
DB_PASSWORD=change_this_to_a_secure_password

# Flask secret key (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=change_this_to_a_random_secret_key_in_production
EOF
    fi
    
    cp .env.example .env
    
    # Generate secure secrets
    print_info "Generating secure random passwords..."
    
    if [ -n "$PYTHON_CMD" ]; then
        SECRET_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
        DB_PASSWORD=$($PYTHON_CMD -c "import secrets; print(secrets.token_urlsafe(24))" 2>/dev/null || openssl rand -base64 24)
    else
        SECRET_KEY=$(openssl rand -hex 32)
        DB_PASSWORD=$(openssl rand -base64 24)
    fi
    
    # Update .env file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|DB_PASSWORD=.*|DB_PASSWORD=${DB_PASSWORD}|" .env
        sed -i '' "s|SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|" .env
    else
        # Linux
        sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=${DB_PASSWORD}|" .env
        sed -i "s|SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|" .env
    fi
    
    print_success "Created .env file with secure random passwords"
else
    print_success ".env file already exists"
    print_warning "Using existing .env configuration"
fi

echo ""

# Step 3: Pull/Build Docker images
echo -e "${BLUE}Step 3: Building Docker images...${NC}"
echo ""

print_info "This may take several minutes on first run..."
echo ""

# Use docker compose if available, otherwise docker-compose
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

if $COMPOSE_CMD build; then
    print_success "Docker images built successfully"
else
    print_error "Failed to build Docker images"
    exit 1
fi

echo ""

# Step 4: Create volumes
echo -e "${BLUE}Step 4: Creating Docker volumes...${NC}"
echo ""

print_info "Creating persistent volumes for database..."
docker volume create logshackbaby_postgres_data 2>/dev/null || true
print_success "Volumes created"

echo ""

# Installation complete
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  ✅ Installation Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${BLUE}📍 To start LogShackBaby:${NC}"
echo "   ./start-docker.sh"
echo ""
echo -e "${BLUE}📍 You will be able to access it at:${NC}"
echo "   🌐 http://localhost"
echo "   🌐 http://localhost:5000 (direct app access)"
if [ "$(hostname -I 2>/dev/null | awk '{print $1}')" ]; then
    echo "   🌐 http://$(hostname -I | awk '{print $1}')"
fi
echo ""
echo -e "${BLUE}🎉 Next steps:${NC}"
echo "   1. Start the application: ./start-docker.sh"
echo "   2. Open http://localhost in your browser"
echo "   3. Click 'Register' to create an account"
echo "   4. The first user becomes the system administrator (sysop)"
echo "   5. Enable 2FA in Settings (recommended)"
echo "   6. Create an API key in the API Keys tab"
echo "   7. Upload your ADIF logs!"
echo ""
echo -e "${BLUE}📖 Documentation:${NC}"
echo "   Configuration: .env"
echo "   Docker compose: docker-compose.yml"
echo "   Read README.md for full documentation"
echo ""
echo -e "${GREEN}73! 📻${NC}"
echo ""
