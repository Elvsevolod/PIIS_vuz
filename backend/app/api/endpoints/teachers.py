from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation

from app.core.database import get_db
from app.api.deps import check_admin, get_current_user
from app.models.models import Teacher, Department, TeacherCategory, AcademicDegree, AcademicTitle, User
from app.schemas.schemas import TeacherCreate, TeacherResponse, TeacherMetadataResponse, IDNamePair

router = APIRouter()

@router.get("/metadata", response_model=TeacherMetadataResponse)
def get_teacher_metadata(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories = db.query(TeacherCategory).order_by(TeacherCategory.id).all()
    degrees = db.query(AcademicDegree).order_by(AcademicDegree.id).all()
    titles = db.query(AcademicTitle).order_by(AcademicTitle.id).all()
    departments = db.query(Department).order_by(Department.name).all()
    
    return TeacherMetadataResponse(
        categories=[IDNamePair(id=c.id, name=c.name) for c in categories],
        degrees=[IDNamePair(id=d.id, name=d.name) for d in degrees],
        titles=[IDNamePair(id=t.id, name=t.name) for t in titles],
        departments=[IDNamePair(id=dept.id, name=dept.name) for dept in departments]
    )

@router.get("/", response_model=List[TeacherResponse])
def list_teachers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    name: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None)
):
    query = db.query(Teacher)
    if name:
        query = query.filter(Teacher.full_name.ilike(f"%{name}%"))
    if department_id:
        query = query.filter(Teacher.department_id == department_id)
    if category_id:
        query = query.filter(Teacher.category_id == category_id)
        
    teachers = query.order_by(Teacher.full_name).all()
    results = []
    for t in teachers:
        results.append(TeacherResponse(
            id=t.id,
            full_name=t.full_name,
            department_id=t.department_id,
            department_name=t.department.name,
            category_id=t.category_id,
            category_name=t.category.name,
            degree_id=t.degree_id,
            degree_name=t.degree.name,
            title_id=t.title_id,
            title_name=t.title.name,
            in_postgraduate=t.in_postgraduate
        ))
    return results

@router.post("/", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(
    teacher_in: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    dept = db.query(Department).filter(Department.id == teacher_in.department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found.")
    cat = db.query(TeacherCategory).filter(TeacherCategory.id == teacher_in.category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Teacher category not found.")
    deg = db.query(AcademicDegree).filter(AcademicDegree.id == teacher_in.degree_id).first()
    if not deg:
        raise HTTPException(status_code=404, detail="Academic degree not found.")
    title = db.query(AcademicTitle).filter(AcademicTitle.id == teacher_in.title_id).first()
    if not title:
        raise HTTPException(status_code=404, detail="Academic title not found.")
        
    teacher = Teacher(
        full_name=teacher_in.full_name,
        department_id=teacher_in.department_id,
        category_id=teacher_in.category_id,
        degree_id=teacher_in.degree_id,
        title_id=teacher_in.title_id,
        in_postgraduate=teacher_in.in_postgraduate
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    
    return TeacherResponse(
        id=teacher.id,
        full_name=teacher.full_name,
        department_id=teacher.department_id,
        department_name=dept.name,
        category_id=teacher.category_id,
        category_name=cat.name,
        degree_id=teacher.degree_id,
        degree_name=deg.name,
        title_id=teacher.title_id,
        title_name=title.name,
        in_postgraduate=teacher.in_postgraduate
    )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    teacher = db.query(Teacher).filter(Teacher.id == id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found.")
        
    try:
        db.delete(teacher)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete teacher: they have assigned workload, diploma supervision, or user account. Remove those first."
        )
    return