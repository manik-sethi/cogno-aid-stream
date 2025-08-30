from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import logging
from typing import List

from websocket.connection_manager import ConnectionManager
from bci.emotiv_connector import EmotivConnector
from bci.confusion_detector import ConfusionDetector
from ai.screenshot_analyzer import ScreenshotAnalyzer
from ai.help_generator import HelpGenerator
from database.database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="BCI Confusion Monitor API", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
manager = ConnectionManager()
emotiv_connector = EmotivConnector()
confusion_detector = ConfusionDetector()
screenshot_analyzer = ScreenshotAnalyzer()
help_generator = HelpGenerator()

# Global state
current_confusion_level = 0.0
confusion_threshold = 0.7
bci_connected = False

@app.on_event("startup")
async def startup_event():
    """Initialize database and start BCI monitoring."""
    await init_db()
    
    # Start BCI data collection in background
    asyncio.create_task(bci_data_loop())
    logger.info("BCI Confusion Monitor API started")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication with frontend."""
    await manager.connect(websocket)
    try:
        while True:
            # Send current status to client
            await websocket.send_json({
                "type": "status_update",
                "data": {
                    "confusion_level": current_confusion_level,
                    "bci_connected": bci_connected,
                    "timestamp": asyncio.get_event_loop().time()
                }
            })
            await asyncio.sleep(0.1)  # 10Hz update rate
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def bci_data_loop():
    """Main loop for processing BCI data."""
    global current_confusion_level, bci_connected
    
    while True:
        try:
            # Connect to EMOTIV if not connected
            if not bci_connected:
                bci_connected = await emotiv_connector.connect()
                
            if bci_connected:
                # Get EEG data from EMOTIV
                eeg_data = await emotiv_connector.get_eeg_data()
                
                if eeg_data:
                    # Process confusion level
                    current_confusion_level = await confusion_detector.analyze_confusion(eeg_data)
                    
                    # Check if threshold exceeded
                    if current_confusion_level > confusion_threshold:
                        await handle_confusion_threshold()
                    
                    # Broadcast to all connected clients
                    await manager.broadcast({
                        "type": "confusion_update",
                        "data": {
                            "level": current_confusion_level,
                            "timestamp": asyncio.get_event_loop().time(),
                            "threshold_exceeded": current_confusion_level > confusion_threshold
                        }
                    })
            
            await asyncio.sleep(0.1)  # 10Hz sampling
            
        except Exception as e:
            logger.error(f"Error in BCI data loop: {e}")
            bci_connected = False
            await asyncio.sleep(1)

async def handle_confusion_threshold():
    """Handle when confusion threshold is exceeded."""
    try:
        # Take screenshot
        screenshot_path = await screenshot_analyzer.capture_screen()
        
        # Analyze screenshot with LLM
        screen_analysis = await screenshot_analyzer.analyze_screenshot(screenshot_path)
        
        # Generate helpful suggestions
        help_suggestions = await help_generator.generate_help(screen_analysis, current_confusion_level)
        
        # Send help to frontend
        await manager.broadcast({
            "type": "help_suggestion",
            "data": {
                "suggestions": help_suggestions,
                "confusion_level": current_confusion_level,
                "screenshot_analysis": screen_analysis,
                "timestamp": asyncio.get_event_loop().time()
            }
        })
        
        logger.info(f"Generated help for confusion level: {current_confusion_level}")
        
    except Exception as e:
        logger.error(f"Error handling confusion threshold: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "bci_connected": bci_connected,
        "confusion_level": current_confusion_level
    }

@app.post("/threshold")
async def update_threshold(threshold: float):
    """Update confusion threshold."""
    global confusion_threshold
    confusion_threshold = max(0.0, min(1.0, threshold))
    return {"threshold": confusion_threshold}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)