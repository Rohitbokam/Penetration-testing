from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.api import endpoints
import os

app = FastAPI(
    title="ThreatLens API",
    description="Real-time Penetration Testing Platform API",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "https://threatlens.example.com",
    "http://localhost:8000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router Registration
app.include_router(endpoints.router, prefix="/api/v1")

# Serve assets if they exist (assuming user puts them there or we have them)
# For now, we only have tool.html in the root.
# We will create a static mount for root to serve tool.html

@app.get("/")
async def read_root():
    return FileResponse('tool.html')

@app.get("/tool.html")
async def read_tool():
    return FileResponse('tool.html')

# Mount assets directory if needed
if os.path.exists("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "threatlens-api"}
