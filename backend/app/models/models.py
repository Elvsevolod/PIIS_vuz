from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class Faculty(Base):
    __tablename__ = "faculties"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    deans = relationship("Dean", back_populates="faculty")
    departments = relationship("Department", back_populates="faculty")
    groups = relationship("Group", back_populates="faculty")

class Dean(Base):
    __tablename__ = "deans"
    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, ForeignKey("faculties.id"), unique=True, nullable=False)
    
    faculty = relationship("Faculty", back_populates="deans")

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculties.id"), nullable=False)
    
    faculty = relationship("Faculty", back_populates="departments")
    teachers = relationship("Teacher", back_populates="department")
    assignments = relationship("DepartmentAssignment", back_populates="department")

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    course = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculties.id"), nullable=False)
    admission_year = Column(Integer, nullable=False)
    
    faculty = relationship("Faculty", back_populates="groups")
    students = relationship("Student", back_populates="group")
    study_plans = relationship("StudyPlanElement", back_populates="group")

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="SET NULL"), nullable=True)
    gradebook_number = Column(String(50), unique=True, nullable=False)
    
    group = relationship("Group", back_populates="students")
    attestations = relationship("Attestation", back_populates="student")
    diploma = relationship("DiplomaWork", back_populates="student", uselist=False)

class TeacherCategory(Base):
    __tablename__ = "teacher_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

class AcademicDegree(Base):
    __tablename__ = "academic_degrees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

class AcademicTitle(Base):
    __tablename__ = "academic_titles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("teacher_categories.id"), nullable=False)
    degree_id = Column(Integer, ForeignKey("academic_degrees.id"), nullable=False)
    title_id = Column(Integer, ForeignKey("academic_titles.id"), nullable=False)
    in_postgraduate = Column(Boolean, default=False)
    
    department = relationship("Department", back_populates="teachers")
    category = relationship("TeacherCategory")
    degree = relationship("AcademicDegree")
    title = relationship("AcademicTitle")
    load = relationship("TeacherLoad", back_populates="teacher")
    diplomas = relationship("DiplomaWork", back_populates="supervisor")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False) # admin, dean, department_head, teacher
    linked_entity_id = Column(Integer, nullable=True) # ID of teacher or dean if linked

class Discipline(Base):
    __tablename__ = "disciplines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=True)
    
    study_plan_elements = relationship("StudyPlanElement", back_populates="discipline")

class ClassType(Base):
    __tablename__ = "class_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(25), nullable=False, unique=True)

class ControlForm(Base):
    __tablename__ = "control_forms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(25), nullable=False, unique=True)
    
    grades = relationship("AcceptableGrade", back_populates="control_form")

class AcceptableGrade(Base):
    __tablename__ = "acceptable_grades"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String(25), nullable=False)
    control_form_id = Column(Integer, ForeignKey("control_forms.id"), nullable=False)
    
    control_form = relationship("ControlForm", back_populates="grades")

class StudyPlanElement(Base):
    __tablename__ = "study_plan_elements"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    discipline_id = Column(Integer, ForeignKey("disciplines.id"), nullable=False)
    class_type_id = Column(Integer, ForeignKey("class_types.id"), nullable=False)
    course = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    hours = Column(Integer, nullable=False)
    control_form_id = Column(Integer, ForeignKey("control_forms.id"), nullable=False)
    
    group = relationship("Group", back_populates="study_plans")
    discipline = relationship("Discipline", back_populates="study_plan_elements")
    class_type = relationship("ClassType")
    control_form = relationship("ControlForm")
    assignments = relationship("DepartmentAssignment", back_populates="study_plan_element", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('group_id', 'discipline_id', 'class_type_id', 'semester', name='_group_discipline_class_semester_uc'),
    )

class DepartmentAssignment(Base):
    __tablename__ = "department_assignments"
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    study_plan_element_id = Column(Integer, ForeignKey("study_plan_elements.id", ondelete="CASCADE"), nullable=False)
    
    department = relationship("Department", back_populates="assignments")
    study_plan_element = relationship("StudyPlanElement", back_populates="assignments")
    teacher_loads = relationship("TeacherLoad", back_populates="assignment", cascade="all, delete-orphan")

class TeacherLoad(Base):
    __tablename__ = "teacher_load"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("department_assignments.id", ondelete="CASCADE"), nullable=False)
    
    teacher = relationship("Teacher", back_populates="load")
    assignment = relationship("DepartmentAssignment", back_populates="teacher_loads")
    
    __table_args__ = (
        UniqueConstraint('teacher_id', 'assignment_id', name='_teacher_assignment_uc'),
    )

class Attestation(Base):
    __tablename__ = "attestations"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    study_plan_element_id = Column(Integer, ForeignKey("study_plan_elements.id"), nullable=False)
    grade_id = Column(Integer, ForeignKey("acceptable_grades.id"), nullable=False)
    date_assigned = Column(Date, nullable=False)
    
    student = relationship("Student", back_populates="attestations")
    study_plan_element = relationship("StudyPlanElement")
    grade = relationship("AcceptableGrade")

class DiplomaWork(Base):
    __tablename__ = "diploma_works"
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
    title = Column(String(255), nullable=False)
    supervisor_id = Column(Integer, ForeignKey("teachers.id", ondelete="RESTRICT"), nullable=False)
    
    student = relationship("Student", back_populates="diploma")
    supervisor = relationship("Teacher", back_populates="diplomas")
