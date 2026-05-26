from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional

from app.core.database import get_db
from app.models.models import (
    Teacher, TeacherLoad, DepartmentAssignment, StudyPlanElement,
    Department, DiplomaWork, Student, Group,
    Attestation,
)
from app.api.deps import get_current_user

router = APIRouter()


# --- Teacher Workload Report ---

@router.get("/teacher-workload")
def teacher_workload_report(
    teacher_id: Optional[int] = Query(None),
    department_id: Optional[int] = Query(None),
    semester: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Отчёт по нагрузке преподавателей за семестр."""
    query = (
        db.query(TeacherLoad)
        .options(
            joinedload(TeacherLoad.assignment).joinedload(DepartmentAssignment.study_plan_element),
            joinedload(TeacherLoad.teacher).joinedload(Teacher.department),
        )
        .join(DepartmentAssignment)
        .join(StudyPlanElement)
        .join(Teacher)
    )

    if teacher_id is not None:
        query = query.filter(TeacherLoad.teacher_id == teacher_id)
    if department_id is not None:
        query = query.filter(Teacher.department_id == department_id)
    if semester is not None:
        query = query.filter(StudyPlanElement.semester == semester)

    loads = query.all()

    results = []
    for l in loads:
        element = l.assignment.study_plan_element
        results.append({
            "teacher_id": l.teacher_id,
            "teacher_name": l.teacher.full_name,
            "department_name": l.teacher.department.name,
            "discipline_name": element.discipline.name if element and element.discipline else "—",
            "class_type_name": element.class_type.name if element and element.class_type else "—",
            "semester": element.semester if element else 0,
            "hours": element.hours if element else 0,
        })

    total_hours = sum(r["hours"] for r in results)
    teachers_involved = len(set(r["teacher_id"] for r in results))

    return {
        "items": results,
        "total_hours": total_hours,
        "teachers_count": teachers_involved,
    }


# --- Diploma Distribution Report ---

@router.get("/diploma-distribution")
def diploma_distribution_report(
    faculty_id: Optional[int] = Query(None),
    department_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Отчёт по распределению дипломников по кафедрам."""
    query = (
        db.query(
            Department.id.label("department_id"),
            Department.name.label("department_name"),
            func.count(DiplomaWork.student_id).label("diploma_count"),
        )
        .join(Teacher, Teacher.department_id == Department.id)
        .join(DiplomaWork, DiplomaWork.supervisor_id == Teacher.id)
    )

    if faculty_id is not None:
        query = query.filter(Department.faculty_id == faculty_id)
    if department_id is not None:
        query = query.filter(Department.id == department_id)

    query = query.group_by(Department.id, Department.name).order_by(func.count(DiplomaWork.student_id).desc())

    rows = query.all()
    results = []
    for row in rows:
        results.append({
            "department_id": row.department_id,
            "department_name": row.department_name,
            "diploma_count": row.diploma_count,
        })

    total_diplomas = sum(r["diploma_count"] for r in results)

    # Detailed list with eager loading
    diplomas_query = (
        db.query(DiplomaWork)
        .options(
            joinedload(DiplomaWork.student),
            joinedload(DiplomaWork.supervisor).joinedload(Teacher.department),
        )
    )
    if faculty_id is not None:
        diplomas_query = diplomas_query.join(Student).join(Group).filter(Group.faculty_id == faculty_id)
    if department_id is not None:
        diplomas_query = diplomas_query.join(Teacher).filter(Teacher.department_id == department_id)

    diplomas = diplomas_query.all()
    details = []
    for d in diplomas:
        details.append({
            "student_id": d.student_id,
            "student_name": d.student.full_name if d.student else "—",
            "title": d.title,
            "supervisor_name": d.supervisor.full_name if d.supervisor else "—",
            "department_name": d.supervisor.department.name if d.supervisor and d.supervisor.department else "—",
        })

    return {
        "summary": results,
        "total_diplomas": total_diplomas,
        "details": details,
    }


# --- Group Performance Report ---

@router.get("/group-performance")
def group_performance_report(
    group_id: int = Query(...),
    semester: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Сводная ведомость успеваемости группы."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found.")

    students = db.query(Student).filter(Student.group_id == group_id).all()

    plan_elements_query = (
        db.query(StudyPlanElement)
        .options(
            joinedload(StudyPlanElement.discipline),
            joinedload(StudyPlanElement.class_type),
            joinedload(StudyPlanElement.control_form),
        )
        .filter(StudyPlanElement.group_id == group_id)
    )
    if semester is not None:
        plan_elements_query = plan_elements_query.filter(StudyPlanElement.semester == semester)
    plan_elements = plan_elements_query.all()

    # Bulk load all attestations for this group's students — single query
    student_ids = [s.id for s in students]
    element_ids = [e.id for e in plan_elements]
    all_attestations = (
        db.query(Attestation)
        .options(joinedload(Attestation.grade))
        .filter(
            Attestation.student_id.in_(student_ids),
            Attestation.study_plan_element_id.in_(element_ids),
        )
        .all()
    )
    # Index by (student_id, element_id) for O(1) lookup
    attestation_map = {(a.student_id, a.study_plan_element_id): a for a in all_attestations}

    total_elements = len(plan_elements)
    results = []
    for student in students:
        student_row = {
            "student_id": student.id,
            "student_name": student.full_name,
            "gradebook_number": student.gradebook_number,
            "grades": [],
        }
        graded_count = 0

        for element in plan_elements:
            key = (student.id, element.id)
            attestation = attestation_map.get(key)

            if attestation:
                graded_count += 1
                student_row["grades"].append({
                    "discipline_name": element.discipline.name if element.discipline else "—",
                    "class_type_name": element.class_type.name if element.class_type else "—",
                    "semester": element.semester,
                    "control_form_name": element.control_form.name if element.control_form else "—",
                    "grade": attestation.grade.value if attestation.grade else "—",
                    "date_assigned": attestation.date_assigned.isoformat(),
                })
            else:
                student_row["grades"].append({
                    "discipline_name": element.discipline.name if element.discipline else "—",
                    "class_type_name": element.class_type.name if element.class_type else "—",
                    "semester": element.semester,
                    "control_form_name": element.control_form.name if element.control_form else "—",
                    "grade": "Не аттестован",
                    "date_assigned": None,
                })

        student_row["completion_pct"] = round(graded_count / total_elements * 100) if total_elements > 0 else 0
        results.append(student_row)

    return {
        "group_id": group.id,
        "group_name": group.name,
        "total_students": len(students),
        "total_elements": total_elements,
        "students": results,
    }
