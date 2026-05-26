from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.models.models import Student, Teacher, DiplomaWork, Attestation, StudyPlanElement, AcceptableGrade, ControlForm
from app.schemas.schemas import DiplomaWorkCreate, DiplomaWorkResponse, AttestationCreate, AttestationResponse, AcceptableGradeResponse
from app.api.deps import get_current_user, check_department_head, check_teacher_or_admin

router = APIRouter()

# --- Diploma Works Endpoints ---

@router.get("/diplomas", response_model=List[DiplomaWorkResponse])
def list_diploma_works(
    faculty_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(DiplomaWork)
    if faculty_id is not None:
        query = query.join(Student).join(Student.group).filter(Student.group.faculty_id == faculty_id)
        
    diplomas = query.all()
    results = []
    for d in diplomas:
        results.append(DiplomaWorkResponse(
            student_id=d.student_id,
            student_name=d.student.full_name if d.student else "Неизвестно",
            title=d.title,
            supervisor_id=d.supervisor_id,
            supervisor_name=d.supervisor.full_name if d.supervisor else "Неизвестно"
        ))
    return results

@router.post("/diplomas", response_model=DiplomaWorkResponse, status_code=status.HTTP_201_CREATED)
def assign_diploma_supervisor(
    diploma_in: DiplomaWorkCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_department_head)
):
    student = db.query(Student).filter(Student.id == diploma_in.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден.")
        
    supervisor = db.query(Teacher).filter(Teacher.id == diploma_in.supervisor_id).first()
    if not supervisor:
        raise HTTPException(status_code=404, detail="Руководитель не найден.")
        
    # Validation Rule: Supervisor must belong to a department of the student's group faculty
    if not student.group or student.group.faculty_id != supervisor.department.faculty_id:
        raise HTTPException(
            status_code=400,
            detail="Руководитель дипломной работы должен быть преподавателем кафедры факультета обучения студента."
        )
        
    # Check if a diploma work already exists for this student
    diploma = db.query(DiplomaWork).filter(DiplomaWork.student_id == diploma_in.student_id).first()
    if diploma:
        # Update details
        diploma.title = diploma_in.title
        diploma.supervisor_id = diploma_in.supervisor_id
    else:
        # Create new
        diploma = DiplomaWork(
            student_id=diploma_in.student_id,
            title=diploma_in.title,
            supervisor_id=diploma_in.supervisor_id
        )
        db.add(diploma)
        
    db.commit()
    db.refresh(diploma)
    
    return DiplomaWorkResponse(
        student_id=diploma.student_id,
        student_name=student.full_name,
        title=diploma.title,
        supervisor_id=diploma.supervisor_id,
        supervisor_name=supervisor.full_name
    )

@router.delete("/diplomas/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diploma_work(
    student_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(check_department_head)
):
    diploma = db.query(DiplomaWork).filter(DiplomaWork.student_id == student_id).first()
    if not diploma:
        raise HTTPException(status_code=404, detail="Дипломная работа не найдена.")
        
    try:
        db.delete(diploma)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete diploma work due to existing references."
        )
    return None


# --- Attestations & Grades Endpoints ---

@router.get("/grades", response_model=List[AcceptableGradeResponse])
def list_acceptable_grades(
    control_form_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(AcceptableGrade)
    if control_form_id is not None:
        query = query.filter(AcceptableGrade.control_form_id == control_form_id)
    grades = query.all()
    return [AcceptableGradeResponse.from_orm(g) for g in grades]

@router.get("/attestations", response_model=List[AttestationResponse])
def list_attestations(
    group_id: Optional[int] = None,
    study_plan_element_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Attestation)
    if group_id is not None:
        query = query.join(Student).filter(Student.group_id == group_id)
    if study_plan_element_id is not None:
        query = query.filter(Attestation.study_plan_element_id == study_plan_element_id)
        
    attestations = query.all()
    results = []
    for a in attestations:
        results.append(AttestationResponse(
            id=a.id,
            student_id=a.student_id,
            student_name=a.student.full_name if a.student else "Неизвестно",
            study_plan_element_id=a.study_plan_element_id,
            grade_id=a.grade_id,
            grade_value=a.grade.value if a.grade else "Неизвестно",
            date_assigned=a.date_assigned.isoformat()
        ))
    return results

@router.post("/attestations", response_model=AttestationResponse, status_code=status.HTTP_201_CREATED)
def assign_grade(
    attestation_in: AttestationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_teacher_or_admin)
):
    student = db.query(Student).filter(Student.id == attestation_in.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден.")
        
    element = db.query(StudyPlanElement).filter(StudyPlanElement.id == attestation_in.study_plan_element_id).first()
    if not element:
        raise HTTPException(status_code=404, detail="Элемент плана не найден.")
        
    grade = db.query(AcceptableGrade).filter(AcceptableGrade.id == attestation_in.grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Оценка не найдена.")
        
    # Validation Rule: Grade must match the form of control of the plan element
    if grade.control_form_id != element.control_form_id:
        raise HTTPException(
            status_code=400,
            detail="Выбранная оценка недопустима для данной формы контроля."
        )
        
    # Check if grade already exists for this student and plan element
    attestation = db.query(Attestation).filter(
        Attestation.student_id == attestation_in.student_id,
        Attestation.study_plan_element_id == attestation_in.study_plan_element_id
    ).first()
    
    if attestation:
        # Update
        attestation.grade_id = attestation_in.grade_id
        attestation.date_assigned = date.today()
    else:
        # Create new
        attestation = Attestation(
            student_id=attestation_in.student_id,
            study_plan_element_id=attestation_in.study_plan_element_id,
            grade_id=attestation_in.grade_id,
            date_assigned=date.today()
        )
        db.add(attestation)
        
    db.commit()
    db.refresh(attestation)
    
    return AttestationResponse(
        id=attestation.id,
        student_id=attestation.student_id,
        student_name=student.full_name,
        study_plan_element_id=attestation.study_plan_element_id,
        grade_id=attestation.grade_id,
        grade_value=grade.value,
        date_assigned=attestation.date_assigned.isoformat()
    )