from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base, SessionLocal
from app.core.seed import seed_db
from app.api.endpoints import auth

# Auto-create tables on startup (convenient for prototyping and development)
Base.metadata.create_all(bind=engine)

# Run database seeding
db = SessionLocal()
try:
    seed_db(db)
finally:
    db.close()

app = FastAPI(
    title="University Information System (UIS) API",
    description="Backend API for managing faculties, departments, students, teachers, study plans, workload, and sessions.",
    version="1.0.0"
)

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the University Information System (UIS) API. Visit /docs for documentation."}
