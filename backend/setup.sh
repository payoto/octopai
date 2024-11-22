#!/bin/bash

# colors
RED='\033[0;31m'
GREEN='\033[0;32m'
GRAY='\033[0;30m'
NC='\033[0m'

# Check if python is installed
echo -e "${GRAY}Checking if python is installed${NC}"
if ! command -v python3 &> /dev/null
then
    echo -e "${RED}❗️ Python is not installed${NC}"
else
    echo -e "${GREEN}✅ Python${NC}"
fi

# Check if conda is installed
# echo -e "${GRAY}Checking if conda is installed${NC}"
# if ! command -v conda &> /dev/null
# then
#     echo -e "${RED}❗️ Conda is not installed${NC}"
#     exit 1
# else
#     echo -e "${GREEN}✅ Conda${NC}"
# fi

# Set up the environment
echo -e "${GRAY}Setting up .env${NC}"

if [ -f ".env" ]; then
    echo -e "${RED}❗️ .env already exists${NC}"
else
    cp .env.example .env && echo -e "${GREEN}✅ .env${NC}"
fi

# Create conda environment
echo -e "${GRAY}Creating conda environment${NC}"

ENVNAME="octopai_env"

curl -LsSf https://astral.sh/uv/install.sh | sh
if ! command -v uv &> /dev/null
then
    echo -e "${RED}❗️ uv is not installed${NC} 0 try restarting the terminal"
    exit 1
else
    echo -e "${GREEN}✅ uv${NC}"
fi


# Install the required packages
echo -e "${GRAY}Installing the required packages${NC}"
uv venv
source .venv/bin/activate
python -m ensurepip
uv pip install --no-cache-dir -r requirements.txt && echo -e "${GREEN}✅ requirements.txt${NC}"

echo -e "${GRAY}\n--- --- --- --- ---\n${NC}"
echo -e "${GREEN}✅ Setup complete\n${NC}"
