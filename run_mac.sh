#!/bin/bash
echo "=================================================="
echo "Market Analytics System - Launcher (Mac/Linux)"
echo "=================================================="

if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found."
    echo "Please run 'sh setup_mac.sh' first."
    exit 1
fi

echo "Activating environment..."
source venv/bin/activate

echo "Starting servers..."
echo "The dashboard will be available at http://localhost:3000"
echo "Ctrl+C to stop."
echo ""

python3 start_servers.py
