#!/bin/bash

# LogShackBaby Quick Start Script
# This script helps you get started with LogShackBaby

set -e

echo "========================================="
echo "  LogShackBaby - Amateur Radio Log Server"
echo "========================================="
echo ""

# Dependencies
sudo apt-get install python3-full python3-pip -y

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    mkdir docker && cd docker
    curl -fsSL https://get.docker.com |sh
    sudo bash get-docker.sh
    # Set SUDO user to use docker
    sudo usermod -aG docker $(whoami)
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    # Docker Compose
    sudo apt install python3-pip -y
    sudo pip3 install docker-compose
    docker-compose version
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    
    # Generate random secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
    
    # Generate random password
    DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))" 2>/dev/null || openssl rand -base64 16)
    
    # Update .env file
    sed -i.bak "s/DB_PASSWORD=.*/DB_PASSWORD=${DB_PASSWORD}/" .env
    sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env
    rm -f .env.bak
    
    echo "✅ Generated secure passwords in .env file"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🚀 Starting LogShackBaby containers..."
echo ""

# Start containers
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check if containers are running
if [ "$(docker-compose ps -q | wc -l)" -eq 0 ]; then
    echo "❌ Containers failed to start. Check logs with: docker-compose logs"
    exit 1
fi

echo ""
echo "========================================="
echo "  ✅ LogShackBaby is running!"
echo "========================================="
echo ""
echo "📍 Access the application:"
echo "   http://localhost"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop the application:"
echo "   docker-compose down"
echo ""
echo "📖 Read the full documentation:"
echo "   cat README.md"
echo ""
echo "🎉 Next steps:"
echo "   1. Open http://localhost in your browser"
echo "   2. Click 'Register' to create an account"
echo "   3. Enable 2FA in Settings (recommended)"
echo "   4. Create an API key in the API Keys tab"
echo "   5. Upload your ADIF logs!"
echo ""
echo "73! 📻"
echo ""
