from pydantic import BaseModel
from typing import Optional, List

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    linked_entity_id: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    linked_entity_id: Optional[int] = None

    class Config:
        from_attributes = True


# --- Faculty Schemas ---
class FacultyCreate(BaseModel):
    name: str

class FacultyResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# --- Department Schemas ---
class DepartmentCreate(BaseModel):
    name: str
    faculty_id: int

class DepartmentResponse(BaseModel):
    id: int
    name: str
    faculty_id: int
    faculty_name: Optional[str] = None

    class Config:
        from_attributes = True


# --- Teacher Schemas ---
class TeacherCreate(BaseModel):
    full_name: str
    department_id: int
    category_id: int
    degree_id: int
    title_id: int
    in_postgraduate: bool = False

class TeacherResponse(BaseModel):
    id: int
    full_name: str
    department_id: int
    department_name: Optional[str] = None
    category_id: int
    category_name: Optional[str] = None
    degree_id: int
    degree_name: Optional[str] = None
    title_id: int
    title_name: Optional[str] = None
    in_postgraduate: bool

    class Config:
        from_attributes = True


# --- Metadata Schemas ---
class IDNamePair(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class TeacherMetadataResponse(BaseModel):
    categories: List[IDNamePair]
    degrees: List[IDNamePair]
    titles: List[IDNamePair]
    departments: List[IDNamePair]


# --- Group Schemas ---
class GroupCreate(BaseModel):
    name: str
    course: int
    semester: int
    faculty_id: int
    admission_year: int

class GroupResponse(BaseModel):
    id: int
    name: str
    course: int
    semester: int
    faculty_id: int
    faculty_name: Optional[str] = None
    admission_year: int

    class Config:
        from_attributes = True


# --- Student Schemas ---
class StudentCreate(BaseModel):
    full_name: str
    group_id: Optional[int] = None
    gradebook_number: str

class StudentResponse(BaseModel):
    id: int
    full_name: str
    group_id: Optional[int] = None
    group_name: Optional[str] = None
    gradebook_number: str

    class Config:
        from_attributes = True


# --- Discipline Schemas ---
class DisciplineCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DisciplineResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


# --- Study Plan Element Schemas ---
class StudyPlanElementCreate(BaseModel):
    group_id: int
    discipline_id: int
    class_type_id: int
    course: int
    semester: int
    hours: int
    control_form_id: int

class StudyPlanElementResponse(BaseModel):
    id: int
    group_id: int
    group_name: Optional[str] = None
    discipline_id: int
    discipline_name: Optional[str] = None
    class_type_id: int
    class_type_name: Optional[str] = None
    course: int
    semester: int
    hours: int
    control_form_id: int
    control_form_name: Optional[str] = None

    class Config:
        from_attributes = True


# --- Department Assignment Schemas ---
class DepartmentAssignmentCreate(BaseModel):
    department_id: int
    study_plan_element_id: int

class DepartmentAssignmentResponse(BaseModel):
    id: int
    department_id: int
    department_name: Optional[str] = None
    study_plan_element_id: int
    study_plan_element_discipline: Optional[str] = None
    study_plan_element_group: Optional[str] = None
    study_plan_element_hours: Optional[int] = None
    study_plan_element_class_type: Optional[str] = None

    class Config:
        from_attributes = True


# --- Teacher Load Schemas ---
class TeacherLoadCreate(BaseModel):
    teacher_id: int
    assignment_id: int

class TeacherLoadResponse(BaseModel):
    id: int
    teacher_id: int
    teacher_name: str
    assignment_id: int
    discipline_name: str
    class_type_name: str
    hours: int
    semester: int

    class Config:
        from_attributes = True

class TeacherAssignmentValidationResponse(BaseModel):
    id: int
    full_name: str
    category_name: str
    title_name: str
    current_load_hours: int
    can_assign: bool
    reason: Optional[str] = None

    class Config:
        from_attributes = True


# --- Diploma Work Schemas ---
class DiplomaWorkCreate(BaseModel):
    student_id: int
    title: str
    supervisor_id: int

class DiplomaWorkResponse(BaseModel):
    student_id: int
    student_name: str
    title: str
    supervisor_id: int
    supervisor_name: str

    class Config:
        from_attributes = True


# --- Attestation Schemas ---
class AttestationCreate(BaseModel):
    student_id: int
    study_plan_element_id: int
    grade_id: int

class AttestationResponse(BaseModel):
    id: int
    student_id: int
    student_name: str
    study_plan_element_id: int
    grade_id: int
    grade_value: str
    date_assigned: str

    class Config:
        from_attributes = True

class AcceptableGradeResponse(BaseModel):
    id: int
    value: str
    control_form_id: int

    class Config:
        from_attributes = True
