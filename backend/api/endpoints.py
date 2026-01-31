from fastapi import APIRouter, HTTPException, WebSocket, Body
from typing import List, Optional, Dict
from pydantic import BaseModel
import uuid
import asyncio
import random
from datetime import datetime

router = APIRouter()

# Models
class ScanRequest(BaseModel):
    target: str
    modules: List[str]
    scan_depth: str = "quick"
    options: Optional[dict] = {}

class ScanResponse(BaseModel):
    scanId: str
    status: str

# In-memory storage for simulation
SCANS: Dict[str, dict] = {}

# Endpoints

@router.post("/scans", response_model=ScanResponse)
async def start_scan(request: ScanRequest):
    """
    Initiates a new security scan.
    """
    scan_id = str(uuid.uuid4())

    SCANS[scan_id] = {
        "id": scan_id,
        "target": request.target,
        "modules": request.modules,
        "status": "queued",
        "progress": 0,
        "start_time": datetime.now(),
        "results": []
    }

    return {"scanId": scan_id, "status": "queued"}

@router.get("/scans/{scan_id}")
async def get_scan_status(scan_id: str):
    """
    Get current status of a scan. Simulates progress.
    """
    if scan_id not in SCANS:
        raise HTTPException(status_code=404, detail="Scan not found")

    scan = SCANS[scan_id]

    # Simulation Logic: Increment progress every time check is called (simple)
    # or based on time. Let's do a simple increment + random for realism.

    if scan["status"] in ["queued", "running", "in_progress"]:
        if scan["status"] == "queued":
            scan["status"] = "running"

        increment = random.randint(5, 15)
        scan["progress"] += increment

        if scan["progress"] >= 100:
            scan["progress"] = 100
            scan["status"] = "completed"
            # Generate fake results
            scan["results"] = [
                {"name": "XSS Vulnerability", "risk": "High", "recommendation": "Sanitize input"},
                {"name": "Open Port 22", "risk": "Low", "recommendation": "Ensure SSH is secure"},
                {"name": "Misconfigured Headers", "risk": "Medium", "recommendation": "Add CSP headers"}
            ]

    return {
        "scanId": scan_id,
        "status": scan["status"],
        "progress": scan["progress"],
        "results": scan.get("results", [])
    }

@router.post("/reports/generate")
async def generate_report(scan_id: str):
    """
    Trigger PDF report generation.
    """
    # For now, return a dummy URL.
    # Real implementation would call PDFGenerator.
    return {
        "message": "Report generation complete",
        "reportUrl": "#"  # Dummy link, or serve a real file if implemented
    }

@router.websocket("/ws/scans/{scan_id}")
async def websocket_endpoint(websocket: WebSocket, scan_id: str):
    await websocket.accept()
    try:
        progress = 0
        while progress < 100:
            await asyncio.sleep(1)
            progress += 10
            await websocket.send_json({
                "scan_id": scan_id,
                "log": f"Scanning... {progress}%",
                "level": "INFO",
                "progress": progress
            })
    except Exception:
        await websocket.close()
