from pydantic import BaseModel
from typing import Optional, List

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

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
