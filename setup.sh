#!/bin/bash

echo "Starting setup for Daily Instagram Post Automation..."

# 1. Install system dependencies (ffmpeg)
if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg not found. Attempting to install it..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y ffmpeg
    elif command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "⚠️  Could not automatically install ffmpeg. Please install it manually! ⚠️"
    fi
else
    echo "ffmpeg is already installed."
fi

# 2. Check and configure .env automatically
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  PLEASE EDIT .env AND ADD YOUR INSTAGRAM/GEMINI CREDENTIALS BEFORE RUNNING! ⚠️"
else
    echo ".env file already exists."
fi

# 3. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment (venv)..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# 4. Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# 5. Install dependencies
echo "Installing Python dependencies from requirements.txt..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo ""
echo "Setup complete! ✅"
echo "To run the project locally, always activate the environment first:"
echo "    source venv/bin/activate"
echo "Then you can run either the image poster or video poster in dry-run mode:"
echo "    python3 post_image.py --dry-run   (For Photo Posts)"
echo "    python3 main.py --dry-run         (For Video Reels)"
echo ""
