from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation
from typing import List, Optional

from app.core.database import get_db
from app.models.models import Teacher, DepartmentAssignment, TeacherLoad, StudyPlanElement, ClassType, AcademicTitle, TeacherCategory
from sqlalchemy.orm import joinedload
from app.schemas.schemas import TeacherLoadCreate, TeacherLoadResponse, TeacherAssignmentValidationResponse
from app.api.deps import get_current_user, check_department_head

router = APIRouter()

# Helper function to compute current workload hours for a teacher
def get_teacher_workload(db: Session, teacher_id: int) -> int:
    loads = (
        db.query(TeacherLoad)
        .options(
            joinedload(TeacherLoad.assignment).joinedload(DepartmentAssignment.study_plan_element)
        )
        .filter(TeacherLoad.teacher_id == teacher_id)
        .all()
    )
    total_hours = 0
    for l in loads:
        if l.assignment and l.assignment.study_plan_element:
            total_hours += l.assignment.study_plan_element.hours
    return total_hours

# Validation engine strictly implementing all business rules
def validate_teacher_assignment(db: Session, teacher_id: int, assignment_id: int):
    # 1. Fetch teacher & details
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден.")
        
    # 2. Fetch assignment & plan element details
    assignment = db.query(DepartmentAssignment).filter(DepartmentAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Поручение не найдено.")
        
    element = assignment.study_plan_element
    if not element:
        raise HTTPException(status_code=404, detail="Элемент учебного плана не найден.")
        
    # Rule 0: Teacher must belong to the department of the assignment
    if teacher.department_id != assignment.department_id:
        raise HTTPException(
            status_code=400,
            detail="Преподаватель должен быть сотрудником кафедры, выполняющей поручение."
        )
        
    # Get names in lowercase for robust comparison
    category = teacher.category.name.lower()
    class_type = element.class_type.name.lower()
    title = teacher.title.name.lower()
    
    # Rule 1: Ассистент не может вести лекции
    if category == "ассистент" and class_type == "лекция":
        raise HTTPException(
            status_code=400,
            detail="Ассистент не имеет права вести лекционные занятия."
        )
        
    # Rule 2: Профессор не ведет лабораторные работы
    if category == "профессор" and class_type == "лабораторная работа":
        raise HTTPException(
            status_code=400,
            detail="Профессор не ведет лабораторные работы."
        )
        
    # Rule 3: Доцент требует ученого звания доцента (или профессора)
    if category == "доцент" and title not in ["доцент", "профессор"]:
        raise HTTPException(
            status_code=400,
            detail="Для назначения на должность доцента необходимо ученое звание доцента."
        )
        
    # Rule 4: Профессор требует ученого звания профессора
    if category == "профессор" and title != "профессор":
        raise HTTPException(
            status_code=400,
            detail="Для назначения на должность профессора необходимо ученое звание профессора."
        )

# --- Endpoints ---

@router.get("/teachers-validation", response_model=List[TeacherAssignmentValidationResponse])
def get_teachers_with_validation(
    assignment_id: int,
    department_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Fetch teachers of the specific department
    teachers = db.query(Teacher).filter(Teacher.department_id == department_id).all()
    results = []
    
    for t in teachers:
        can_assign = True
        reason = None
        
        # Run validation in dry-run mode (using try-except to extract detail messages)
        try:
            validate_teacher_assignment(db, t.id, assignment_id)
        except HTTPException as e:
            can_assign = False
            reason = e.detail
            
        load_hours = get_teacher_workload(db, t.id)
        
        results.append(TeacherAssignmentValidationResponse(
            id=t.id,
            full_name=t.full_name,
            category_name=t.category.name,
            title_name=t.title.name,
            current_load_hours=load_hours,
            can_assign=can_assign,
            reason=reason
        ))
        
    return results

@router.get("/", response_model=List[TeacherLoadResponse])
def list_teacher_loads(
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(TeacherLoad)
    if department_id is not None:
        query = query.join(DepartmentAssignment).filter(DepartmentAssignment.department_id == department_id)
        
    loads = query.all()
    results = []
    for l in loads:
        element = l.assignment.study_plan_element
        results.append(TeacherLoadResponse(
            id=l.id,
            teacher_id=l.teacher_id,
            teacher_name=l.teacher.full_name,
            assignment_id=l.assignment_id,
            discipline_name=element.discipline.name if element and element.discipline else "Неизвестно",
            class_type_name=element.class_type.name if element and element.class_type else "Неизвестно",
            hours=element.hours if element else 0,
            semester=element.semester if element else 0
        ))
    return results

@router.post("/", response_model=TeacherLoadResponse, status_code=status.HTTP_201_CREATED)
def create_teacher_load(
    load_in: TeacherLoadCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_department_head)
):
    # 1. Run strict business rule validation
    validate_teacher_assignment(db, load_in.teacher_id, load_in.assignment_id)
    
    # 2. Check if assignment is already assigned to a teacher
    existing = db.query(TeacherLoad).filter(TeacherLoad.assignment_id == load_in.assignment_id).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Это поручение уже распределено на другого преподавателя."
        )
        
    # 3. Create assignment load
    load = TeacherLoad(
        teacher_id=load_in.teacher_id,
        assignment_id=load_in.assignment_id
    )
    db.add(load)
    db.commit()
    db.refresh(load)
    
    element = load.assignment.study_plan_element
    return TeacherLoadResponse(
        id=load.id,
        teacher_id=load.teacher_id,
        teacher_name=load.teacher.full_name,
        assignment_id=load.assignment_id,
        discipline_name=element.discipline.name if element and element.discipline else "Неизвестно",
        class_type_name=element.class_type.name if element and element.class_type else "Неизвестно",
        hours=element.hours if element else 0,
        semester=element.semester if element else 0
    )

@router.delete("/{load_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher_load(
    load_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(check_department_head)
):
    load = db.query(TeacherLoad).filter(TeacherLoad.id == load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail="Распределение нагрузки не найдено.")
    try:
        db.delete(load)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete teacher load due to existing references."
        )
    return None