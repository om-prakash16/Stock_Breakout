# Stock_Breakout (Market Analytics System)

A high-performance, real-time stock breakout detection system for NSE and BSE markets. Built with a FastAPI backend and a Next.js (React) frontend.

![Quant Terminal Dashboard](https://via.placeholder.com/800x400?text=Quant+Terminal+UI)

## Features

*   **Real-Time Breakout Detection**: Scans 7,000+ stocks (NSE & BSE) for breakout patterns (Day High, 52 Week High, All Time High).
*   **Dual Exchange Support**: Dedicated tabs for NSE and BSE equities.
*   **Intelligent Filtering**:
    *   **Direction**: Filter by Long (Bullish) or Short (Bearish/Breakdown) signals.
    *   **Timeframe**: 1D, 2D, 10D, 30D, 100D, 52W, All Time.
*   **Data Accuracy**:
    *   Shows exact **Detection Time** for every signal.
    *   Visual "Live" indicator and system status.
*   **Interactive UI**:
    *   Sortable columns (Level, Price, %).
    *   Dismiss (Hide) functionality for noise reduction.
    *   Recovery mode for hidden stocks.
*   **Cross-Platform**: Easy setup scripts for Windows and Mac/Linux.
*   **Performance**:
    *   **Optimized Threading**: Smart resource management (`max_workers=20`) to prevent crashes.
    *   **WebSocket Ready**: Server supports `/ws` endpoint for push updates.

## Tech Stack

*   **Backend**: Python, FastAPI, Pandas, Uvicorn.
*   **Frontend**: TypeScript, Next.js, Tailwind CSS, Radix UI.
*   **Data**: Parquet (Atomic storage), Yahoo Finance (Historical Data).

## Quick Start

### Windows
1.  Run **`setup_windows.bat`** (First time setup - installs dependencies).
2.  Run **`run_windows.bat`** (Starts the servers).

### Mac / Linux
1.  Run `sh setup_mac.sh` (First time setup).
2.  Run `sh run_mac.sh` (Starts the servers).

*The dashboard will launch at [http://localhost:3000](http://localhost:3000)*

## Manual Run (For Developers)

If you prefer to run everything manually without scripts, follow these steps. You can use **Command Prompt (cmd)**, **PowerShell**, or the **VS Code Integrated Terminal**.

### 1. Prerequisite: Setup Environment
**Recommended: Python 3.10, 3.11, or 3.12**
*(Python 3.13 is supported but may require installing pre-release wheels for some libraries)*

First, create the virtual environment and install dependencies.

**Command Prompt / PowerShell / VS Code:**
```bash
# Create venv in root
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Dependencies
pip install -r backend/requirements.txt
```

### 2. Start Backend (Terminal 1)
Open a new terminal window:
```bash
# Activate venv first!
venv\Scripts\activate

# Navigate to backend
cd backend

# Run Server
python -m uvicorn src.api.main:app --reload --port 8000
```

### 3. Start Frontend (Terminal 2)
Open a second terminal window:
```bash
cd frontend
npm install  # (Only needed once)
npm run dev
```

> **Note**: On the very first run, the backend will automatically download the stock universe list (NSE/BSE). This may take 1-2 minutes. Please be patient if the "Total Scanned" count initially shows 0.

*Access the dashboard at http://localhost:3000*

## Architecture

*   **Structure**:
    *   `frontend/`: Next.js Web Application.
    *   `backend/`: Python API and Data Processing Engine.
*   **Key Components**:
    *   `backend/src/universe`: Market data fetching.
    *   `backend/src/analytics`: Breakout detection logic.
    *   `backend/data`: Parquet storage (Atomic reads/writes).

## License

MIT
