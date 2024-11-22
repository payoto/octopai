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
echo -e "${GRAY}Checking if conda is installed${NC}"
if ! command -v conda &> /dev/null
then
    echo -e "${RED}❗️ Conda is not installed${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Conda${NC}"
fi

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

if conda info --envs | grep -q $ENVNAME; then
    echo -e "${RED}❗️ Conda environment '$ENVNAME' already exists${NC}"
else
    conda create -n $ENVNAME python=3.11 -y && echo -e "${GREEN}✅ Conda environment${NC}"
fi

# Install the required packages
echo -e "${GRAY}Installing the required packages${NC}"

eval "$(conda shell.bash hook)"
conda activate $ENVNAME && echo -e "${GREEN}✅ Conda environment activated${NC}"
conda install pip -y && echo -e "${GREEN}✅ Pip installed${NC}"
pip install --no-cache-dir -r requirements.txt && echo -e "${GREEN}✅ requirements.txt${NC}"

echo -e "${GRAY}\n--- --- --- --- ---\n${NC}"
echo -e "${GREEN}✅ Setup complete\n${NC}"
