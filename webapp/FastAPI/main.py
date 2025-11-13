from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
from routes import art_routes, doctor_routes, patient_routes, session_routes, memory_reconstruction, vr_routes, art_exploration, evaluation_routes
import database

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.getenv("STATIC_DIR", "../data/static")

# Only mount static directories if they exist
wikiart_dir = os.path.join(STATIC_DIR, "wikiart")
semart_dir = os.path.join(STATIC_DIR, "semart")

app.mount(
    "/art-images/wikiart",
    StaticFiles(directory=wikiart_dir),
    name="wikiart_images",
)

app.mount(
    "/art-images/semart", 
    StaticFiles(directory=semart_dir),
    name="semart_images",
)

# Include routers
app.include_router(art_routes.router, prefix="/api", tags=["Art"])
app.include_router(doctor_routes.router, prefix="/api/doctors", tags=["Doctor"])
app.include_router(patient_routes.router, prefix="/api/patients", tags=["Patient"])
app.include_router(session_routes.router, prefix="/api", tags=["Sessions"])
app.include_router(memory_reconstruction.router, prefix="/api/memory", tags=["Memory Reconstruction"])
app.include_router(art_exploration.router, prefix="/api/art", tags=["Art Exploration"])
app.include_router(vr_routes.router, prefix="/api/vr", tags=["VR"])
app.include_router(evaluation_routes.router, prefix="/api/evaluation", tags=["Evaluation"])


@app.on_event("startup")
async def startup_event():
    await database.connect_to_mysql()


@app.on_event("shutdown")
async def shutdown_event():
    await database.disconnect_from_mysql()


@app.get("/")
async def root():
    return {"message": "Welcome to the home page!"}
