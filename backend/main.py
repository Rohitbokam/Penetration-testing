from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import endpoints

app = FastAPI(
    title="ThreatLens API",
    description="Real-time Penetration Testing Platform API",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "https://threatlens.example.com",
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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "threatlens-api"}
