from sqlalchemy.orm import Session
from app.models.models import TeacherCategory, AcademicDegree, AcademicTitle, ClassType, ControlForm, AcceptableGrade, User
from app.core.security import get_password_hash

def seed_db(db: Session):
    # 1. Teacher Categories
    categories = ["ассистент", "преподаватель", "старший преподаватель", "доцент", "профессор"]
    for cat in categories:
        if not db.query(TeacherCategory).filter_by(name=cat).first():
            db.add(TeacherCategory(name=cat))
            
    # 2. Academic Degrees
    degrees = ["нет", "кандидат наук", "доктор наук"]
    for deg in degrees:
        if not db.query(AcademicDegree).filter_by(name=deg).first():
            db.add(AcademicDegree(name=deg))
            
    # 3. Academic Titles
    titles = ["нет", "доцент", "профессор"]
    for tit in titles:
        if not db.query(AcademicTitle).filter_by(name=tit).first():
            db.add(AcademicTitle(name=tit))
            
    # 4. Class Types
    classes = ["лекция", "семинар", "лабораторная работа", "консультация", "курсовая работа"]
    for cl in classes:
        if not db.query(ClassType).filter_by(name=cl).first():
            db.add(ClassType(name=cl))
            
    # 5. Control Forms & Grades
    db.commit() # Flush first to get IDs if needed
    
    exam_form = db.query(ControlForm).filter_by(name="экзамен").first()
    if not exam_form:
        exam_form = ControlForm(name="экзамен")
        db.add(exam_form)
        db.commit()
        
    zachet_form = db.query(ControlForm).filter_by(name="зачет").first()
    if not zachet_form:
        zachet_form = ControlForm(name="зачет")
        db.add(zachet_form)
        db.commit()
        
    exam_grades = ["Отлично", "Хорошо", "Удовлетворительно", "Неудовлетворительно"]
    for eg in exam_grades:
        if not db.query(AcceptableGrade).filter_by(value=eg, control_form_id=exam_form.id).first():
            db.add(AcceptableGrade(value=eg, control_form_id=exam_form.id))
            
    zachet_grades = ["Зачет", "Незачет"]
    for zg in zachet_grades:
        if not db.query(AcceptableGrade).filter_by(value=zg, control_form_id=zachet_form.id).first():
            db.add(AcceptableGrade(value=zg, control_form_id=zachet_form.id))
            
    # 6. Default Admin User
    if not db.query(User).filter_by(username="admin").first():
        hashed = get_password_hash("admin123")
        db.add(User(username="admin", hashed_password=hashed, role="admin"))
        
    db.commit()
