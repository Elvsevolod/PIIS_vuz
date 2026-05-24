from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import check_admin, get_current_user
from app.models.models import Department, Faculty, User
from app.schemas.schemas import DepartmentCreate, DepartmentResponse

router = APIRouter()

@router.get("/", response_model=List[DepartmentResponse])
def list_departments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    departments = db.query(Department).order_by(Department.name).all()
    results = []
    for dept in departments:
        results.append(DepartmentResponse(
            id=dept.id,
            name=dept.name,
            faculty_id=dept.faculty_id,
            faculty_name=dept.faculty.name
        ))
    return results

@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    dept_in: DepartmentCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_admin)
):
    faculty = db.query(Faculty).filter(Faculty.id == dept_in.faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found.")
        
    existing = db.query(Department).filter(
        Department.name == dept_in.name, 
        Department.faculty_id == dept_in.faculty_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Department with this name already exists in this faculty.")
    
    dept = Department(name=dept_in.name, faculty_id=dept_in.faculty_id)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    
    return DepartmentResponse(
        id=dept.id,
        name=dept.name,
        faculty_id=dept.faculty_id,
        faculty_name=faculty.name
    )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_admin)
):
    dept = db.query(Department).filter(Department.id == id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found.")
    
    db.delete(dept)
    db.commit()
    return
