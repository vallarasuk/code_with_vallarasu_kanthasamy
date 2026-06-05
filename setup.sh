#!/bin/bash

echo "Starting setup for Daily Instagram Post Automation..."

# 1. Check and configure .env automatically
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  PLEASE EDIT .env AND ADD YOUR INSTAGRAM/GEMINI CREDENTIALS BEFORE RUNNING! ⚠️"
else
    echo ".env file already exists."
fi

# 2. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment (venv)..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# 3. Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# 4. Install dependencies
echo "Installing Python dependencies from requirements.txt..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo ""
echo "Setup complete! ✅"
echo "To run the project locally, always activate the environment first:"
echo "    source venv/bin/activate"
echo "Then run the script in dry-run mode to test using python3:"
echo "    python3 main.py --dry-run"
echo ""
