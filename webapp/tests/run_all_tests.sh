#!/bin/bash

# ArtEvoke Test Suite Runner
# Runs both backend and frontend tests with coverage

set -e  # Exit on error

echo "🧪 ArtEvoke Session Management System - Test Suite"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
}

# Change to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Backend Tests
echo "📦 Running Backend Tests..."
echo "-------------------------"
cd backend

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "Running pytest..."
pytest -v --cov=../../FastAPI --cov-report=html --cov-report=term
BACKEND_STATUS=$?

deactivate
cd ..

print_status $BACKEND_STATUS "Backend tests completed"
echo ""

# Frontend Tests
echo "⚛️  Running Frontend Tests..."
echo "-------------------------"
cd frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing npm packages...${NC}"
    npm install
fi

echo "Running Jest..."
npm test -- --coverage --watchAll=false
FRONTEND_STATUS=$?

cd ..

print_status $FRONTEND_STATUS "Frontend tests completed"
echo ""

# Summary
echo "=================================================="
echo "📊 Test Summary"
echo "=================================================="
echo ""

if [ $BACKEND_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Backend: All tests passed${NC}"
    echo "  Coverage report: tests/backend/htmlcov/index.html"
else
    echo -e "${RED}✗ Backend: Some tests failed${NC}"
fi

if [ $FRONTEND_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend: All tests passed${NC}"
    echo "  Coverage report: tests/frontend/coverage/index.html"
else
    echo -e "${RED}✗ Frontend: Some tests failed${NC}"
fi

echo ""

# Exit with error if any test suite failed
if [ $BACKEND_STATUS -ne 0 ] || [ $FRONTEND_STATUS -ne 0 ]; then
    echo -e "${RED}Some tests failed. Please fix them before committing.${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed! 🎉${NC}"
    exit 0
fi
