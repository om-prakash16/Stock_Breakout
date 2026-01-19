from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add project root to path to ensure imports work
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

app = FastAPI(
    title="Quant Terminal API",
    description="Backend API for Market Analytics System",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Next.js frontend
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.api.endpoints import router as api_router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "online", "system": "Quant Terminal API"}

from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from typing import List

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or handle client messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)

from src.api.scheduler import start_scheduler
# Import service to fetch data for broadcast
from src.analytics.service import BreakoutService
import json

# Background task to broadcast updates
async def broadcast_updates():
    service = BreakoutService()
    while True:
        try:
            # Fetch latest data (lightweight scan or cache check)
            # For now, we simulate a push by broadcasting a "refresh" signal
            # or we can send the actual data if efficient.
            # Let's send a ping/update signal so frontend knows to re-fetch or invalidates cache.
            # Real implementation would push diffs.
            await manager.broadcast(json.dumps({"type": "update", "timestamp": str(asyncio.get_event_loop().time())}))
        except Exception as e:
            print(f"Broadcast error: {e}")
        await asyncio.sleep(10) # Push every 10s

@app.on_event("startup")
async def startup_event():
    start_scheduler()
    asyncio.create_task(broadcast_updates())

