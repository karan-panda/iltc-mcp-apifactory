#!/bin/bash

# Demo script to run the complete policy wording assistant

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a command was successful
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Success${NC}"
    else
        echo -e "${RED}✗ Failed${NC}"
        exit 1
    fi
}

# Print header
echo -e "${BLUE}====================================${NC}"
echo -e "${BLUE}   IL Take Care  Assistant  Demo    ${NC}"
echo -e "${BLUE}====================================${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "\n${YELLOW}Creating virtual environment...${NC}"
    python -m venv venv
    check_status
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
check_status

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt
check_status

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Creating .env file...${NC}"
    cp .env.example .env || echo -e "PINECONE_API_KEY=your_pinecone_api_key_here\nPINECONE_ENVIRONMENT=your_pinecone_environment_here\nHUGGINGFACE_API_TOKEN=your_huggingface_api_token_here\nINDEX_NAME=policy-assistant" > .env
    check_status
    
    echo -e "\n${RED}Please edit the .env file with your API keys!${NC}"
    echo -e "${YELLOW}Press Enter to continue, or Ctrl+C to exit and edit the file...${NC}"
    read
fi

# Run initialization script
echo -e "\n${YELLOW}Initializing project...${NC}"
python setup.py --create-samples
check_status

# Check if data directory has PDF files
if [ ! -f "app/data/travel_insurance.pdf" ] || [ ! -f "app/data/health_insurance.pdf" ]; then
    echo -e "\n${RED}PDF files not found in app/data directory!${NC}"
    echo -e "${YELLOW}Please add your PDF files to the app/data directory.${NC}"
    echo -e "${YELLOW}Press Enter to continue, or Ctrl+C to exit and add files...${NC}"
    read
fi

# Ingest documents
echo -e "\n${YELLOW}Ingesting documents...${NC}"
python -m app.backend.ingest
check_status

# Start backend server in background
echo -e "\n${YELLOW}Starting backend server...${NC}"
python main.py &
BACKEND_PID=$!
sleep 3
check_status

# Start frontend server in background
echo -e "\n${YELLOW}Starting frontend server...${NC}"
python -m app.frontend.serve &
FRONTEND_PID=$!
sleep 2
check_status

# Print instructions
echo -e "\n${GREEN}Everything is up and running!${NC}"
echo -e "\n${BLUE}Backend API:${NC} http://localhost:8000"
echo -e "${BLUE}Frontend:${NC} http://localhost:8080"
echo -e "\n${YELLOW}Press Ctrl+C to stop all servers when done${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n\n${YELLOW}Stopping servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}Servers stopped${NC}"
    exit 0
}

# Register cleanup function
trap cleanup INT

# Wait for Ctrl+C
wait $BACKEND_PID
