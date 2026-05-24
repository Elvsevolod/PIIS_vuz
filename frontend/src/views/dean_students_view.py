import flet as ft
from api_client import api_client

class DeanStudentsView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.padding = 0
        self.margin = 0
        
        # State
        self.groups = []
        self.students = []
        self.selected_group = None
        self.faculties = []
        
        # UI controls
        self.group_list = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        self.student_list = ft.Column(spacing=8, scroll=ft.ScrollMode.ADAPTIVE)
        self.loading_indicator = ft.ProgressBar(visible=False, color=ft.colors.INDIGO_400)
        
        # Top-level info panels
        self.group_header_text = ft.Text("Группы", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
        self.student_header_text = ft.Text("Студенты группы (выберите группу)", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
        
        # Main layout structure
        self.content = ft.Column(
            controls=[
                self.loading_indicator,
                ft.Row(
                    controls=[
                        # Left side - Groups list
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            self.group_header_text,
                                            ft.IconButton(
                                                icon=ft.icons.ADD_ROUNDED,
                                                icon_color=ft.colors.INDIGO_300,
                                                tooltip="Создать новую группу",
                                                on_click=self.show_create_group_dialog
                                            )
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Divider(color=ft.colors.WHITE10),
                                    ft.Container(
                                        content=self.group_list,
                                        expand=True
                                    )
                                ],
                                spacing=10
                            ),
                            width=320,
                            bgcolor=ft.colors.SURFACE,
                            border_radius=12,
                            border=ft.border.all(1, ft.colors.WHITE10),
                            padding=20,
                            expand=False
                        ),
                        # Right side - Students list
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            self.student_header_text,
                                            ft.IconButton(
                                                icon=ft.icons.PERSON_ADD_ROUNDED,
                                                icon_color=ft.colors.INDIGO_300,
                                                tooltip="Зачислить нового студента",
                                                on_click=self.show_create_student_dialog,
                                                visible=False
                                            )
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
        
        # Load initial data
        self.load_data()

    def show_loading(self, show: bool):
        self.loading_indicator.visible = show
        self.page.update()

    def load_data(self):
        self.show_loading(True)
        try:
            # 1. Fetch faculties for dropdowns
            resp_fac = api_client.get("/api/v1/faculties/")
            if resp_fac.status_code == 200:
                self.faculties = resp_fac.json()
            
            # 2. Fetch groups
            resp_groups = api_client.get("/api/v1/students/groups")
            if resp_groups.status_code == 200:
                self.groups = resp_groups.json()
                self.render_groups()
            else:
                self.show_snackbar("Ошибка загрузки групп", ft.colors.RED_400)
        except Exception as e:
            self.show_snackbar(f"Сетевая ошибка: {e}", ft.colors.RED_400)
        finally:
            self.show_loading(False)

    def render_groups(self):
        self.group_list.controls.clear()
        
        if not self.groups:
            self.group_list.controls.append(
                ft.Container(
                    content=ft.Text("Нет созданных групп", color=ft.colors.WHITE38, size=13),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
            self.page.update()
            return
            
        for g in self.groups:
            is_selected = self.selected_group and self.selected_group["id"] == g["id"]
            
            # Card styling matching design tokens
            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(g["name"], size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                ft.Container(
                                    content=ft.Text(f"{g['course']} курс", size=10, color=ft.colors.INDIGO_300, weight=ft.FontWeight.BOLD),
                                    bgcolor=ft.colors.INDIGO_900_O10,
                                    border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=6, vertical=2)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Text(f"Семестр: {g['semester']} | Поступление: {g['admission_year']}", size=11, color=ft.colors.WHITE54),
                        ft.Text(g["faculty_name"] or "Без факультета", size=11, color=ft.colors.WHITE38, overflow=ft.TextOverflow.ELLIPSIS)
                    ],
                    spacing=5
                ),
                padding=15,
                border_radius=10,
                border=ft.border.all(1, ft.colors.INDIGO_500 if is_selected else ft.colors.WHITE10),
                bgcolor=ft.colors.SURFACE_VARIANT if is_selected else ft.colors.TRANSPARENT,
                on_click=lambda e, group=g: self.select_group(group),
                on_hover=self.on_hover_card,
                data=g["id"]
            )
            self.group_list.controls.append(card)
            
        self.page.update()

    def select_group(self, group):
        self.selected_group = group
        
        # Redraw group selection border
        self.render_groups()
        
        # Enable student addition button in header
        self.content.controls[1].controls[1].content.controls[0].controls[1].visible = True
        self.student_header_text.value = f"Студенты группы {group['name']}"
        
        # Load students for selected group
        self.load_students()

    def load_students(self):
        if not self.selected_group:
            return
            
        self.show_loading(True)
        try:
            resp = api_client.get(f"/api/v1/students/?group_id={self.selected_group['id']}")
            if resp.status_code == 200:
                self.students = resp.json()
                self.render_students()
            else:
                self.show_snackbar("Ошибка загрузки студентов", ft.colors.RED_400)
        except Exception as e:
            self.show_snackbar(f"Сетевая ошибка: {e}", ft.colors.RED_400)
        finally:
            self.show_loading(False)

    def render_students(self):
        self.student_list.controls.clear()
        
        if not self.students:
            self.student_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(name=ft.icons.PEOPLE_OUTLINE_ROUNDED, size=48, color=ft.colors.WHITE24),
                            ft.Text("В группе пока нет студентов", color=ft.colors.WHITE38, size=13),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10
                    ),
                    alignment=ft.alignment.center,
                    padding=40
                )
            )
            self.page.update()
            return
            
        for s in self.students:
            student_card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(name=ft.icons.ACCOUNT_CIRCLE_ROUNDED, color=ft.colors.INDIGO_300, size=24),
                                ft.Column(
                                    controls=[
                                        ft.Text(s["full_name"], size=14, weight=ft.FontWeight.W_500, color=ft.colors.WHITE),
                                        ft.Text(f"Номер зачетки: {s['gradebook_number']}", size=11, color=ft.colors.WHITE54),
                                    ],
                                    spacing=2
                                )
                            ],
                            spacing=12
                        ),
                        ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.icons.EDIT_ROUNDED,
                                    icon_color=ft.colors.WHITE38,
                                    icon_size=18,
                                    tooltip="Редактировать",
                                    on_click=lambda e, student=s: self.show_edit_student_dialog(student)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE_OUTLINE_ROUNDED,
                                    icon_color=ft.colors.RED_300,
                                    icon_size=18,
                                    tooltip="Удалить",
                                    on_click=lambda e, student=s: self.delete_student(student)
                                )
                            ],
                            spacing=5
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=12,
                border_radius=8,
                bgcolor=ft.colors.SURFACE_VARIANT,
                border=ft.border.all(1, ft.colors.WHITE10)
            )
            self.student_list.controls.append(student_card)
            
        self.page.update()

    def on_hover_card(self, e):
        if e.data == "true":
            # Highlight border slightly on hover if not selected
            is_selected = self.selected_group and self.selected_group["id"] == e.control.data
            e.control.border = ft.border.all(1, ft.colors.INDIGO_400 if is_selected else ft.colors.WHITE38)
            e.control.bgcolor = ft.colors.WHITE10
        else:
            is_selected = self.selected_group and self.selected_group["id"] == e.control.data
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

    # --- Dialog Actions ---
    
    def show_create_group_dialog(self, e):
        if not self.faculties:
            self.show_snackbar("Сначала создайте хотя бы один факультет!", ft.colors.AMBER_600)
            return
            
        name_input = ft.TextField(label="Название группы (например: 301-ПИ)", border_color=ft.colors.WHITE10, focused_border_color=ft.colors.INDIGO_400)
        course_input = ft.Dropdown(
            label="Курс",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 7)],
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
            value="1"
        )
        semester_input = ft.Dropdown(
            label="Семестр",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 13)],
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
            value="1"
        )
        faculty_input = ft.Dropdown(
            label="Факультет",
            options=[ft.dropdown.Option(text=f["name"], key=str(f["id"])) for f in self.faculties],
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
            value=str(self.faculties[0]["id"])
        )
        year_input = ft.TextField(label="Год поступления", value="2026", border_color=ft.colors.WHITE10, focused_border_color=ft.colors.INDIGO_400)
        
        def save_new_group(ev):
            if not name_input.value.strip():
                name_input.error_text = "Введите название!"
                dialog.update()
                return
            
            try:
                payload = {
                    "name": name_input.value.strip(),
                    "course": int(course_input.value),
                    "semester": int(semester_input.value),
                    "faculty_id": int(faculty_input.value),
                    "admission_year": int(year_input.value)
                }
                
                resp = api_client.post("/api/v1/students/groups", json_data=payload)
                if resp.status_code == 201:
                    self.show_snackbar("Группа успешно создана!", ft.colors.GREEN_600)
                    dialog.open = False
                    self.load_data()
                else:
                    err = resp.json().get("detail", "Ошибка сохранения")
                    self.show_snackbar(f"Ошибка: {err}", ft.colors.RED_400)
            except Exception as ex:
                self.show_snackbar(f"Сбой: {ex}", ft.colors.RED_400)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Создать новую группу", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[name_input, course_input, semester_input, faculty_input, year_input],
                spacing=12,
                height=340,
                width=320
            ),
            actions=[
                ft.TextButton("Отмена", on_click=lambda ev: self.close_dialog(dialog)),
                ft.ElevatedButton("Создать", bgcolor=ft.colors.INDIGO_600, color=ft.colors.WHITE, on_click=save_new_group)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_create_student_dialog(self, e):
        if not self.selected_group:
            return
            
        name_input = ft.TextField(label="ФИО Студента", border_color=ft.colors.WHITE10, focused_border_color=ft.colors.INDIGO_400)
        gradebook_input = ft.TextField(label="Номер зачетки", border_color=ft.colors.WHITE10, focused_border_color=ft.colors.INDIGO_400)
        
        def save_new_student(ev):
            if not name_input.value.strip():
                name_input.error_text = "Введите ФИО!"
                dialog.update()
                return
            if not gradebook_input.value.strip():
                gradebook_input.error_text = "Введите номер зачетки!"
                dialog.update()
                return
                
            try:
                payload = {
                    "full_name": name_input.value.strip(),
                    "group_id": self.selected_group["id"],
                    "gradebook_number": gradebook_input.value.strip()
                }
                
                resp = api_client.post("/api/v1/students/", json_data=payload)
                if resp.status_code == 201:
                    self.show_snackbar("Студент успешно зачислен!", ft.colors.GREEN_600)
                    dialog.open = False
                    self.load_students()
                else:
                    err = resp.json().get("detail", "Ошибка зачисления")
                    self.show_snackbar(f"Ошибка: {err}", ft.colors.RED_400)
            except Exception as ex:
                self.show_snackbar(f"Сбой: {ex}", ft.colors.RED_400)
                
        dialog = ft.AlertDialog(
            title=ft.Text(f"Зачислить студента в {self.selected_group['name']}", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[name_input, gradebook_input],
                spacing=12,
                height=140,
                width=320
            ),
            actions=[
                ft.TextButton("Отмена", on_click=lambda ev: self.close_dialog(dialog)),
                ft.ElevatedButton("Зачислить", bgcolor=ft.colors.INDIGO_600, color=ft.colors.WHITE, on_click=save_new_student)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_edit_student_dialog(self, student):
        name_input = ft.TextField(label="ФИО Студента", value=student["full_name"], border_color=ft.colors.WHITE10, focused_border_color=ft.colors.INDIGO_400)
        gradebook_input = ft.TextField(label="Номер зачетки", value=student["gradebook_number"], border_color=ft.colors.WHITE10, focused_border_color=ft.colors.INDIGO_400)
        
        def update_existing_student(ev):
            if not name_input.value.strip():
                name_input.error_text = "Поле пустое!"
                dialog.update()
                return
            if not gradebook_input.value.strip():
                gradebook_input.error_text = "Поле пустое!"
                dialog.update()
                return
                
            try:
                payload = {
                    "full_name": name_input.value.strip(),
                    "group_id": student["group_id"],
                    "gradebook_number": gradebook_input.value.strip()
                }
                
                resp = api_client.post(f"/api/v1/students/{student['id']}", json_data=payload) # PUT request simulation in endpoint or use explicit PUT method
                # Wait, our update_student endpoint uses PUT /api/v1/students/{student_id}!
                # Let's call api_client.post using custom request, or since api_client doesn't have put method, let's look at api_client.py. It has post, get, delete, but not put!
                # Wait, we can implement put in api_client or use post, or let's use api_client.post/put.
                # Let's implement PUT in api_client or use standard HTTP request inside the handler.
                # Actually, let's check: our update_student endpoint in students.py uses PUT, and we can make a direct put request using requests, or extend APIClient.
                # Let's write the PUT request directly using requests inside live views. It's safer and avoids modifying other files unless necessary.
                import requests
                headers = api_client._get_headers()
                resp = requests.put(f"{api_client.base_url}/api/v1/students/{student['id']}", headers=headers, json=payload, timeout=5)
                
                if resp.status_code == 200:
                    self.show_snackbar("Данные студента изменены!", ft.colors.GREEN_600)
                    dialog.open = False
                    self.load_students()
                else:
                    err = resp.json().get("detail", "Ошибка изменения")
                    self.show_snackbar(f"Ошибка: {err}", ft.colors.RED_400)
            except Exception as ex:
                self.show_snackbar(f"Сбой: {ex}", ft.colors.RED_400)
                
        dialog = ft.AlertDialog(
            title=ft.Text("Редактировать студента", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[name_input, gradebook_input],
                spacing=12,
                height=140,
                width=320
            ),
            actions=[
                ft.TextButton("Отмена", on_click=lambda ev: self.close_dialog(dialog)),
                ft.ElevatedButton("Сохранить", bgcolor=ft.colors.INDIGO_600, color=ft.colors.WHITE, on_click=update_existing_student)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def delete_student(self, student):
        def confirm_delete(ev):
            try:
                resp = api_client.delete(f"/api/v1/students/{student['id']}")
                if resp.status_code == 204:
                    self.show_snackbar("Студент отчислен/удален!", ft.colors.GREEN_600)
                    dialog.open = False
                    self.load_students()
                else:
                    self.show_snackbar("Не удалось удалить студента", ft.colors.RED_400)
            except Exception as ex:
                self.show_snackbar(f"Сбой: {ex}", ft.colors.RED_400)
                
        dialog = ft.AlertDialog(
            title=ft.Text("Подтвердите действие", weight=ft.FontWeight.BOLD),
            content=ft.Text(f"Вы действительно хотите отчислить студента {student['full_name']}?", size=14, color=ft.colors.WHITE70),
            actions=[
                ft.TextButton("Отмена", on_click=lambda ev: self.close_dialog(dialog)),
                ft.ElevatedButton("Удалить", bgcolor=ft.colors.RED_600, color=ft.colors.WHITE, on_click=confirm_delete)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
