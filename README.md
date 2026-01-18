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

## Tech Stack

*   **Backend**: Python, FastAPI, Pandas, Uvicorn.
*   **Frontend**: TypeScript, Next.js, Tailwind CSS, Radix UI.
*   **Data**: Parquet (Atomic storage), Yahoo Finance (Historical Data).

## Quick Start

### Windows
1.  Run **`setup_windows.bat`** (First time setup).
2.  Run **`run_windows.bat`** (To start the app).

### Mac / Linux
1.  Run `sh setup_mac.sh` (First time setup).
2.  Run `sh run_mac.sh` (To start the app).

*The dashboard will launch at [http://localhost:3000](http://localhost:3000)*

## Architecture

*   **Phase 1 (Universe)**: Fetches symbol lists from NSE/BSE.
*   **Phase 2 (History)**: optimized background download of historical price data.
*   **Phase 3 (Scanner)**: Vectorized analysis to detect breakouts relative to sliding windows.
*   **API**: Serves JSON data to the frontend via REST endpoints.

## License

MIT
