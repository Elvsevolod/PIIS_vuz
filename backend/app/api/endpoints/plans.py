from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation
from typing import List, Dict, Any, Optional

from app.core.database import get_db
from app.models.models import Discipline, StudyPlanElement, DepartmentAssignment, Group, ClassType, ControlForm, Department
from app.schemas.schemas import DisciplineCreate, DisciplineResponse, StudyPlanElementCreate, StudyPlanElementResponse, DepartmentAssignmentCreate, DepartmentAssignmentResponse
from app.api.deps import get_current_user, check_dean

router = APIRouter()

# --- Metadata Endpoints ---

@router.get("/metadata")
def get_plans_metadata(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    class_types = db.query(ClassType).all()
    control_forms = db.query(ControlForm).all()
    
    return {
        "class_types": [{"id": c.id, "name": c.name} for c in class_types],
        "control_forms": [{"id": cf.id, "name": cf.name} for cf in control_forms]
    }


# --- Disciplines Endpoints ---

@router.get("/disciplines", response_model=List[DisciplineResponse])
def list_disciplines(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    disciplines = db.query(Discipline).all()
    return [DisciplineResponse.from_orm(d) for d in disciplines]

@router.post("/disciplines", response_model=DisciplineResponse, status_code=status.HTTP_201_CREATED)
def create_discipline(discipline_in: DisciplineCreate, db: Session = Depends(get_db), current_user = Depends(check_dean)):
    existing = db.query(Discipline).filter(Discipline.name == discipline_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Discipline with this name already exists")
        
    discipline = Discipline(
        name=discipline_in.name,
        description=discipline_in.description
    )
    db.add(discipline)
    db.commit()
    db.refresh(discipline)
    return DisciplineResponse.from_orm(discipline)


# --- Study Plan Elements Endpoints ---

@router.get("/elements", response_model=List[StudyPlanElementResponse])
def list_study_plan_elements(group_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    elements = db.query(StudyPlanElement).filter(StudyPlanElement.group_id == group_id).all()
    results = []
    for e in elements:
        results.append(StudyPlanElementResponse(
            id=e.id,
            group_id=e.group_id,
            group_name=e.group.name if e.group else None,
            discipline_id=e.discipline_id,
            discipline_name=e.discipline.name if e.discipline else None,
            class_type_id=e.class_type_id,
            class_type_name=e.class_type.name if e.class_type else None,
            course=e.course,
            semester=e.semester,
            hours=e.hours,
            control_form_id=e.control_form_id,
            control_form_name=e.control_form.name if e.control_form else None
        ))
    return results

@router.post("/elements", response_model=StudyPlanElementResponse, status_code=status.HTTP_201_CREATED)
def create_study_plan_element(element_in: StudyPlanElementCreate, db: Session = Depends(get_db), current_user = Depends(check_dean)):
    # Verify group, discipline, class_type, control_form exist
    group = db.query(Group).filter(Group.id == element_in.group_id).first()
    if not group:
        raise HTTPException(status_code=400, detail="Group not found")
        
    discipline = db.query(Discipline).filter(Discipline.id == element_in.discipline_id).first()
    if not discipline:
        raise HTTPException(status_code=400, detail="Discipline not found")
        
    class_type = db.query(ClassType).filter(ClassType.id == element_in.class_type_id).first()
    if not class_type:
        raise HTTPException(status_code=400, detail="Class type not found")
        
    control_form = db.query(ControlForm).filter(ControlForm.id == element_in.control_form_id).first()
    if not control_form:
        raise HTTPException(status_code=400, detail="Control form not found")
        
    # Check uniqueness constraint: (group_id, discipline_id, class_type_id, semester)
    existing = db.query(StudyPlanElement).filter(
        StudyPlanElement.group_id == element_in.group_id,
        StudyPlanElement.discipline_id == element_in.discipline_id,
        StudyPlanElement.class_type_id == element_in.class_type_id,
        StudyPlanElement.semester == element_in.semester
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Study plan element already exists for this group, discipline, class type, and semester"
        )
        
    element = StudyPlanElement(
        group_id=element_in.group_id,
        discipline_id=element_in.discipline_id,
        class_type_id=element_in.class_type_id,
        course=element_in.course,
        semester=element_in.semester,
        hours=element_in.hours,
        control_form_id=element_in.control_form_id
    )
    db.add(element)
    db.commit()
    db.refresh(element)
    
    return StudyPlanElementResponse(
        id=element.id,
        group_id=element.group_id,
        group_name=group.name,
        discipline_id=element.discipline_id,
        discipline_name=discipline.name,
        class_type_id=element.class_type_id,
        class_type_name=class_type.name,
        course=element.course,
        semester=element.semester,
        hours=element.hours,
        control_form_id=element.control_form_id,
        control_form_name=control_form.name
    )

@router.delete("/elements/{element_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_study_plan_element(element_id: int, db: Session = Depends(get_db), current_user = Depends(check_dean)):
    element = db.query(StudyPlanElement).filter(StudyPlanElement.id == element_id).first()
    if not element:
        raise HTTPException(status_code=404, detail="Study plan element not found")
    try:
        db.delete(element)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete study plan element: it has related department assignments. Remove them first."
        )
    return None


# --- Department Assignments (Поручения) Endpoints ---

@router.get("/assignments", response_model=List[DepartmentAssignmentResponse])
def list_department_assignments(department_id: Optional[int] = None, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    query = db.query(DepartmentAssignment)
    if department_id is not None:
        query = query.filter(DepartmentAssignment.department_id == department_id)
    assignments = query.all()
    
    results = []
    for a in assignments:
        results.append(DepartmentAssignmentResponse(
            id=a.id,
            department_id=a.department_id,
            department_name=a.department.name if a.department else None,
            study_plan_element_id=a.study_plan_element_id,
            study_plan_element_discipline=a.study_plan_element.discipline.name if a.study_plan_element and a.study_plan_element.discipline else None,
            study_plan_element_group=a.study_plan_element.group.name if a.study_plan_element and a.study_plan_element.group else None,
            study_plan_element_hours=a.study_plan_element.hours if a.study_plan_element else None,
            study_plan_element_class_type=a.study_plan_element.class_type.name if a.study_plan_element and a.study_plan_element.class_type else None
        ))
    return results

@router.post("/assignments", response_model=DepartmentAssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_department_assignment(assignment_in: DepartmentAssignmentCreate, db: Session = Depends(get_db), current_user = Depends(check_dean)):
    # Verify department and study plan element exist
    department = db.query(Department).filter(Department.id == assignment_in.department_id).first()
    if not department:
        raise HTTPException(status_code=400, detail="Department not found")
        
    element = db.query(StudyPlanElement).filter(StudyPlanElement.id == assignment_in.study_plan_element_id).first()
    if not element:
        raise HTTPException(status_code=400, detail="Study plan element not found")
        
    # Check if assignment already exists for this study plan element
    existing = db.query(DepartmentAssignment).filter(
        DepartmentAssignment.study_plan_element_id == assignment_in.study_plan_element_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Study plan element is already assigned to a department"
        )
        
    assignment = DepartmentAssignment(
        department_id=assignment_in.department_id,
        study_plan_element_id=assignment_in.study_plan_element_id
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return DepartmentAssignmentResponse(
        id=assignment.id,
        department_id=assignment.department_id,
        department_name=department.name,
        study_plan_element_id=assignment.study_plan_element_id,
        study_plan_element_discipline=element.discipline.name if element.discipline else None,
        study_plan_element_group=element.group.name if element.group else None,
        study_plan_element_hours=element.hours,
        study_plan_element_class_type=element.class_type.name if element.class_type else None
    )

@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department_assignment(assignment_id: int, db: Session = Depends(get_db), current_user = Depends(check_dean)):
    assignment = db.query(DepartmentAssignment).filter(DepartmentAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Department assignment not found")
    try:
        db.delete(assignment)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete department assignment: it has related teacher load records. Remove them first."
        )
    return None