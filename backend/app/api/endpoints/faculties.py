from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import check_admin, get_current_user
from app.models.models import Faculty, User
from app.schemas.schemas import FacultyCreate, FacultyResponse

router = APIRouter()

@router.get("/", response_model=List[FacultyResponse])
def list_faculties(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Faculty).order_by(Faculty.name).all()

@router.post("/", response_model=FacultyResponse, status_code=status.HTTP_201_CREATED)
def create_faculty(
    faculty_in: FacultyCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_admin)
):
    existing = db.query(Faculty).filter(Faculty.name == faculty_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Faculty with this name already exists.")
    
    faculty = Faculty(name=faculty_in.name)
    db.add(faculty)
    db.commit()
    db.refresh(faculty)
    return faculty

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faculty(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_admin)
):
    faculty = db.query(Faculty).filter(Faculty.id == id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found.")
    
    db.delete(faculty)
    db.commit()
    return
