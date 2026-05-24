import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from app.core.database import engine, Base, SessionLocal
from app.core.seed import seed_db
from app.api.endpoints import auth

# Try to connect to the database with a retry loop (handles PostgreSQL startup delay)
max_retries = 10
db_connected = False
for retry in range(max_retries):
    try:
        # Auto-create tables on startup
        Base.metadata.create_all(bind=engine)
        
        # Run database seeding
        db = SessionLocal()
        try:
            seed_db(db)
        finally:
            db.close()
        
        print("Database initialized and seeded successfully!")
        db_connected = True
        break
    except OperationalError as e:
        if retry == max_retries - 1:
            print("Could not connect to the database. Max retries exceeded.")
            raise e
        print(f"Database not ready yet (PostgreSQL is starting up). Retrying in 2 seconds... (Attempt {retry + 1}/{max_retries})")
        time.sleep(2)

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
