#!/bin/bash
# K8s Health Check - Quick Start Script

set -e

echo "========================================"
echo "  K8s Health Check - Quick Start"
echo "========================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python
echo -e "${YELLOW}[1/4] Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 not found!${NC}"
    exit 1
fi
python3 --version

# Create virtual environment
echo -e "${YELLOW}[2/4] Setting up virtual environment...${NC}"
if [ ! -d "backend/venv" ]; then
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -e .
    pip install email-validator
    cd ..
    echo -e "${GREEN}Virtual environment created!${NC}"
else
    echo "Virtual environment already exists."
fi

# Create .env if not exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp backend/.env.example backend/.env
fi

# Check Node.js
echo -e "${YELLOW}[3/4] Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js not found!${NC}"
    exit 1
fi
node --version

# Install frontend dependencies
echo -e "${YELLOW}[4/4] Installing frontend dependencies...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
else
    echo "Dependencies already installed."
fi
cd ..

echo ""
echo "========================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "========================================"
echo ""
echo "To start the backend:"
echo "  cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "To start the frontend (in another terminal):"
echo "  cd frontend && npm run dev"
echo ""
echo "Default admin credentials:"
echo "  Username: admin"
echo "  Password: Admin@123"
echo ""
echo "========================================"
