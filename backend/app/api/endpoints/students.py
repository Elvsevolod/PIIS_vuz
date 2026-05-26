from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation
from typing import List, Optional

from app.core.database import get_db
from app.models.models import Group, Student, Faculty
from app.schemas.schemas import GroupCreate, GroupResponse, StudentCreate, StudentResponse
from app.api.deps import get_current_user, check_dean

router = APIRouter()

# --- Student Groups Endpoints ---

@router.get("/groups", response_model=List[GroupResponse])
def list_groups(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    groups = db.query(Group).all()
    results = []
    for g in groups:
        results.append(GroupResponse(
            id=g.id,
            name=g.name,
            course=g.course,
            semester=g.semester,
            faculty_id=g.faculty_id,
            faculty_name=g.faculty.name if g.faculty else None,
            admission_year=g.admission_year
        ))
    return results

@router.post("/groups", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(group_in: GroupCreate, db: Session = Depends(get_db), current_user = Depends(check_dean)):
    # Verify faculty exists
    faculty = db.query(Faculty).filter(Faculty.id == group_in.faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=400, detail="Faculty not found")
    
    # Verify group name is unique
    existing = db.query(Group).filter(Group.name == group_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Group with this name already exists")
    
    group = Group(
        name=group_in.name,
        course=group_in.course,
        semester=group_in.semester,
        faculty_id=group_in.faculty_id,
        admission_year=group_in.admission_year
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    
    return GroupResponse(
        id=group.id,
        name=group.name,
        course=group.course,
        semester=group.semester,
        faculty_id=group.faculty_id,
        faculty_name=faculty.name,
        admission_year=group.admission_year
    )

@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(group_id: int, db: Session = Depends(get_db), current_user = Depends(check_dean)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    try:
        db.delete(group)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete group: it has related students or study plan elements. Remove them first."
        )
    return None


# --- Students Endpoints ---

@router.get("/", response_model=List[StudentResponse])
def list_students(
    group_id: Optional[int] = None,
    name: Optional[str] = None,
    gradebook_number: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Student)
    if group_id is not None:
        query = query.filter(Student.group_id == group_id)
    if name:
        query = query.filter(Student.full_name.ilike(f"%{name}%"))
    if gradebook_number:
        query = query.filter(Student.gradebook_number.ilike(f"%{gradebook_number}%"))
    students = query.all()
    
    results = []
    for s in students:
        results.append(StudentResponse(
            id=s.id,
            full_name=s.full_name,
            group_id=s.group_id,
            group_name=s.group.name if s.group else None,
            gradebook_number=s.gradebook_number
        ))
    return results

@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student_in: StudentCreate, db: Session = Depends(get_db), current_user = Depends(check_dean)):
    # Verify group if provided
    if student_in.group_id:
        group = db.query(Group).filter(Group.id == student_in.group_id).first()
        if not group:
            raise HTTPException(status_code=400, detail="Group not found")
    
    # Verify gradebook number is unique
    existing = db.query(Student).filter(Student.gradebook_number == student_in.gradebook_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student with this gradebook number already exists")
    
    student = Student(
        full_name=student_in.full_name,
        group_id=student_in.group_id,
        gradebook_number=student_in.gradebook_number
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    
    return StudentResponse(
        id=student.id,
        full_name=student.full_name,
        group_id=student.group_id,
        group_name=student.group.name if student.group else None,
        gradebook_number=student.gradebook_number
    )

@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_in: StudentCreate, db: Session = Depends(get_db), current_user = Depends(check_dean)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    if student_in.group_id:
        group = db.query(Group).filter(Group.id == student_in.group_id).first()
        if not group:
            raise HTTPException(status_code=400, detail="Group not found")
            
    # Check gradebook number uniqueness if changed
    if student_in.gradebook_number != student.gradebook_number:
        existing = db.query(Student).filter(Student.gradebook_number == student_in.gradebook_number).first()
        if existing:
            raise HTTPException(status_code=400, detail="Student with this gradebook number already exists")
            
    student.full_name = student_in.full_name
    student.group_id = student_in.group_id
    student.gradebook_number = student_in.gradebook_number
    
    db.commit()
    db.refresh(student)
    
    return StudentResponse(
        id=student.id,
        full_name=student.full_name,
        group_id=student.group_id,
        group_name=student.group.name if student.group else None,
        gradebook_number=student.gradebook_number
    )

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db), current_user = Depends(check_dean)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    try:
        db.delete(student)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete student: they have attestations or a diploma work. Remove those first."
        )
    return None