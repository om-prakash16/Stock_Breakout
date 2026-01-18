#!/bin/bash
echo "=================================================="
echo "Market Analytics System - Initial Setup (Mac/Linux)"
echo "=================================================="

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check for Node
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed."
    echo "Please install Node.js and try again."
    exit 1
fi

echo ""
echo "[1/3] Setting up Python Virtual Environment..."
if [ ! -d "venv" ]; then
    echo "Creating venv..."
    python3 -m venv venv
fi
source venv/bin/activate

echo ""
echo "[2/3] Installing Python Dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install Python dependencies."
    exit 1
fi

echo ""
echo "[3/3] Installing Frontend Dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing node modules..."
    npm install
fi
cd ..

echo ""
echo "=================================================="
echo "Setup Complete!"
echo "You can now run 'sh run_mac.sh' to start the system."
echo "=================================================="
