import flet as ft
from api_client import api_client

class DeptDiplomasView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.padding = 0
        self.margin = 0
        
        # State
        self.students = []
        self.teachers = []
        self.diplomas_map = {}
        self.selected_student = None
        
        self.current_dept_id = 1
        
        # UI controls
        self.student_list = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        self.detail_area = ft.Column(spacing=20, scroll=ft.ScrollMode.ADAPTIVE)
        self.loading_indicator = ft.ProgressBar(visible=False, color=ft.colors.INDIGO_400)
        
        # Header text
        self.student_header = ft.Text("Студенты для руководства", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
        self.detail_header = ft.Text("Руководство дипломной работой", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
        
        # Dropdown for department selection (visible for Admin)
        self.dept_dropdown = ft.Dropdown(
            label="Кафедра",
            options=[],
            width=220,
            height=46,
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
            on_change=self.handle_dept_change,
            visible=False
        )
        
        # Main Layout
        self.content = ft.Column(
            controls=[
                self.loading_indicator,
                ft.Row(
                    controls=[
                        # Left Panel - Students
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            self.student_header,
                                            self.dept_dropdown
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Divider(color=ft.colors.WHITE10),
                                    ft.Container(
                                        content=self.student_list,
                                        expand=True
                                    )
                                ],
                                spacing=10
                            ),
                            width=360,
                            bgcolor=ft.colors.SURFACE,
                            border_radius=12,
                            border=ft.border.all(1, ft.colors.WHITE10),
                            padding=20,
                            expand=False
                        ),
                        # Right Panel - Diploma Assignment Details
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    self.detail_header,
                                    ft.Divider(color=ft.colors.WHITE10),
                                    ft.Container(
                                        content=self.detail_area,
                                        expand=True
                                    )
                                ],
                                spacing=10
                            ),
                            expand=True,
                            bgcolor=ft.colors.SURFACE,
                            border_radius=12,
                            border=ft.border.all(1, ft.colors.WHITE10),
                            padding=20
                        )
                    ],
                    expand=True,
                    spacing=20
                )
            ],
            expand=True,
            spacing=10
        )
        
        self.load_data()

    def show_loading(self, show: bool):
        self.loading_indicator.visible = show
        self.page.update()

    def load_data(self):
        self.show_loading(True)
        try:
            # 1. Check if user is admin
            role = api_client.current_user.get("role") if api_client.current_user else "guest"
            if role == "admin":
                self.dept_dropdown.visible = True
                resp_depts = api_client.get("/api/v1/departments/")
                if resp_depts.status_code == 200:
                    depts = resp_depts.json()
                    self.dept_dropdown.options = [
                        ft.dropdown.Option(text=d["name"], key=str(d["id"])) for d in depts
                    ]
                    if depts:
                        self.dept_dropdown.value = str(depts[0]["id"])
                        self.current_dept_id = depts[0]["id"]
            
            self.load_students_and_teachers()
            
        except Exception as e:
            self.show_snackbar(f"Сетевая ошибка: {e}", ft.colors.RED_400)
        finally:
            self.show_loading(False)

    def load_students_and_teachers(self):
        try:
            # Load teachers of the department
            resp_teachers = api_client.get(f"/api/v1/teachers/?department_id={self.current_dept_id}")
            # Load all students (in a real app, we filter by faculty, but since we have a demo, load all students is fine)
            resp_students = api_client.get("/api/v1/students/")
            # Load active diplomas
            resp_diplomas = api_client.get("/api/v1/grades/diplomas")
            
            if resp_teachers.status_code == 200 and resp_students.status_code == 200 and resp_diplomas.status_code == 200:
                self.teachers = resp_teachers.json()
                self.students = resp_students.json()
                
                # Map diplomas by student_id
                self.diplomas_map = {d["student_id"]: d for d in resp_diplomas.json()}
                
                self.render_students()
            else:
                self.show_snackbar("Ошибка загрузки данных", ft.colors.RED_400)
        except Exception as e:
            self.show_snackbar(f"Сбой: {e}", ft.colors.RED_400)

    def handle_dept_change(self, e):
        self.current_dept_id = int(self.dept_dropdown.value)
        self.selected_student = None
        self.detail_area.controls.clear()
        self.load_students_and_teachers()

    def render_students(self):
        self.student_list.controls.clear()
        
        if not self.students:
            self.student_list.controls.append(
                ft.Container(
                    content=ft.Text("Нет зачисленных студентов", color=ft.colors.WHITE38, size=13),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
            self.page.update()
            return
            
        for s in self.students:
            is_selected = self.selected_student and self.selected_student["id"] == s["id"]
            dip = self.diplomas_map.get(s["id"])
            
            status_text = "Руководитель не назначен"
            status_color = ft.colors.AMBER_400
            
            if dip:
                status_text = f"Рук: {dip['supervisor_name']}"
                status_color = ft.colors.INDIGO_300
                
            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(s["full_name"], size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                                ft.Icon(name=ft.icons.ASSIGNMENT_ROUNDED, color=ft.colors.GREEN_400 if dip else ft.colors.WHITE24, size=16)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Text(f"Группа: {s['group_name'] or 'Без группы'} | Зачетка: {s['gradebook_number']}", size=11, color=ft.colors.WHITE54),
                        ft.Text(status_text, size=11, color=status_color, weight=ft.FontWeight.W_500, overflow=ft.TextOverflow.ELLIPSIS)
                    ],
                    spacing=3
                ),
                padding=12,
                border_radius=8,
                border=ft.border.all(1, ft.colors.INDIGO_500 if is_selected else ft.colors.WHITE10),
                bgcolor=ft.colors.SURFACE_VARIANT if is_selected else ft.colors.TRANSPARENT,
                on_click=lambda ev, student=s: self.select_student(student),
                on_hover=self.on_hover_card,
                data=s["id"]
            )
            self.student_list.controls.append(card)
            
        self.page.update()

    def select_student(self, student):
        self.selected_student = student
        self.render_students()
        self.render_detail_area()

    def render_detail_area(self):
        self.detail_area.controls.clear()
        
        if not self.selected_student:
            self.detail_area.controls.append(
                ft.Container(
                    content=ft.Text("Выберите студента слева для назначения руководителя диплома", color=ft.colors.WHITE38, size=13),
                    alignment=ft.alignment.center,
                    padding=40
                )
            )
            self.page.update()
            return
            
        dip = self.diplomas_map.get(self.selected_student["id"])
        
        # UI controls for form
        title_input = ft.TextField(
            label="Тема дипломной работы",
            value=dip["title"] if dip else "",
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
            expand=True
        )
        
        supervisor_dropdown = ft.Dropdown(
            label="Научный руководитель",
            options=[ft.dropdown.Option(text=t["full_name"], key=str(t["id"])) for t in self.teachers],
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
            value=str(dip["supervisor_id"]) if dip else (str(self.teachers[0]["id"]) if self.teachers else None)
        )
        
        def save_diploma(ev):
            if not title_input.value.strip():
                title_input.error_text = "Тема диплома не может быть пустой!"
                self.page.update()
                return
            if not supervisor_dropdown.value:
                self.show_snackbar("Выберите руководителя!", ft.colors.AMBER_600)
                return
                
            self.show_loading(True)
            try:
                payload = {
                    "student_id": self.selected_student["id"],
                    "title": title_input.value.strip(),
                    "supervisor_id": int(supervisor_dropdown.value)
                }
                resp = api_client.post("/api/v1/grades/diplomas", json_data=payload)
                if resp.status_code == 201:
                    self.show_snackbar("Руководитель дипломной работы успешно назначен!", ft.colors.GREEN_600)
                    self.load_students_and_teachers()
                    self.selected_student = None
                    self.detail_area.controls.clear()
                else:
                    err = resp.json().get("detail", "Ошибка сохранения")
                    self.show_snackbar(f"Ошибка: {err}", ft.colors.RED_400)
            except Exception as e:
                self.show_snackbar(f"Сбой: {e}", ft.colors.RED_400)
            finally:
                self.show_loading(False)
                
        def delete_diploma(ev):
            self.show_loading(True)
            try:
                resp = api_client.delete(f"/api/v1/grades/diplomas/{self.selected_student['id']}")
                if resp.status_code == 204:
                    self.show_snackbar("Назначение диплома аннулировано!", ft.colors.GREEN_600)
                    self.load_students_and_teachers()
                    self.selected_student = None
                    self.detail_area.controls.clear()
                else:
                    self.show_snackbar("Не удалось аннулировать", ft.colors.RED_400)
            except Exception as e:
                self.show_snackbar(f"Сбой: {e}", ft.colors.RED_400)
            finally:
                self.show_loading(False)
                
        # Build view
        self.detail_area.controls.extend([
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(f"Студент: {self.selected_student['full_name']}", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ft.Text(f"Группа: {self.selected_student['group_name'] or 'Без группы'} | Номер зачетки: {self.selected_student['gradebook_number']}", size=12, color=ft.colors.WHITE54),
                    ],
                    spacing=5
                ),
                padding=15,
                bgcolor=ft.colors.SURFACE_VARIANT,
                border_radius=10
            ),
            title_input,
            supervisor_dropdown,
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        text="Сохранить назначение",
                        icon=ft.icons.SAVE_ROUNDED,
                        bgcolor=ft.colors.INDIGO_600,
                        color=ft.colors.WHITE,
                        on_click=save_diploma,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                    ),
                    ft.ElevatedButton(
                        text="Аннулировать",
                        icon=ft.icons.DELETE_FOREVER_ROUNDED,
                        bgcolor=ft.colors.RED_600,
                        color=ft.colors.WHITE,
                        visible=dip is not None,
                        on_click=delete_diploma,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                    )
                ],
                spacing=10
            )
        ])
        
        self.page.update()

    def on_hover_card(self, e):
        if e.data == "true":
            is_selected = self.selected_student and self.selected_student["id"] == e.control.data
            e.control.border = ft.border.all(1, ft.colors.INDIGO_400 if is_selected else ft.colors.WHITE38)
            e.control.bgcolor = ft.colors.WHITE10
        else:
            is_selected = self.selected_student and self.selected_student["id"] == e.control.data
            e.control.border = ft.border.all(1, ft.colors.INDIGO_500 if is_selected else ft.colors.WHITE10)
            e.control.bgcolor = ft.colors.SURFACE_VARIANT if is_selected else ft.colors.TRANSPARENT
        e.control.update()

    def show_snackbar(self, text: str, color: str):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(text, color=ft.colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=color,
            duration=3000
        )
        self.page.snack_bar.open = True
        self.page.update()
