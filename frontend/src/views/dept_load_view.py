import flet as ft
from api_client import api_client

class DeptLoadView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.padding = 0
        self.margin = 0
        
        # State
        self.assignments = []
        self.teachers_validation = []
        self.selected_assignment = None
        
        # Determine department ID from user context
        role = api_client.current_user.get("role") if api_client.current_user else "guest"
        linked_id = api_client.current_user.get("linked_entity_id") if api_client.current_user else None
        if role == "department_head" and linked_id:
            self.current_dept_id = linked_id
        else:
            self.current_dept_id = 1
        
        # UI controls
        self.assign_list = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        self.teacher_list = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        self.loading_indicator = ft.ProgressBar(visible=False, color=ft.colors.INDIGO_400)
        
        # Header text
        self.assign_header = ft.Text("Поручения кафедры", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
        self.teacher_header = ft.Text("Распределение нагрузки преподавателей", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
        
        # Department selector (visible for Admin to demonstrate different departments!)
        self.dept_dropdown = ft.Dropdown(
            label="Кафедра",
            options=[],
            width=240,
            height=46,
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
            on_change=self.handle_dept_change,
            visible=False
        )
        
        # Content Layout
        self.content = ft.Column(
            controls=[
                self.loading_indicator,
                ft.Row(
                    controls=[
                        # Left side - Assignments
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            self.assign_header,
                                            self.dept_dropdown
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Divider(color=ft.colors.WHITE10),
                                    ft.Container(
                                        content=self.assign_list,
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
                        # Right side - Teachers & Validation Engine status
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    self.teacher_header,
                                    ft.Divider(color=ft.colors.WHITE10),
                                    ft.Container(
                                        content=self.teacher_list,
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
            # 1. If admin, load departments list to let them select
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
            
            # 2. Fetch assignments
            self.load_assignments()
            
        except Exception as e:
            self.show_snackbar(f"Сетевая ошибка: {e}", ft.colors.RED_400)
        finally:
            self.show_loading(False)

    def load_assignments(self):
        try:
            # Fetch department assignments
            resp = api_client.get(f"/api/v1/plans/assignments?department_id={self.current_dept_id}")
            # Fetch teacher load maps to match currently assigned teachers
            resp_loads = api_client.get(f"/api/v1/load/?department_id={self.current_dept_id}")
            
            if resp.status_code == 200 and resp_loads.status_code == 200:
                self.assignments = resp.json()
                
                # Map load details by assignment_id
                self.loads_map = {l["assignment_id"]: l for l in resp_loads.json()}
                
                self.render_assignments()
            else:
                self.show_snackbar("Ошибка загрузки поручений", ft.colors.RED_400)
        except Exception as e:
            self.show_snackbar(f"Сбой: {e}", ft.colors.RED_400)

    def handle_dept_change(self, e):
        self.current_dept_id = int(self.dept_dropdown.value)
        self.selected_assignment = None
        self.teacher_list.controls.clear()
        self.load_assignments()

    def render_assignments(self):
        self.assign_list.controls.clear()
        
        if not self.assignments:
            self.assign_list.controls.append(
                ft.Container(
                    content=ft.Text("Нет поручений для этой кафедры", color=ft.colors.WHITE38, size=13),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
            self.page.update()
            return
            
        for a in self.assignments:
            is_selected = self.selected_assignment and self.selected_assignment["id"] == a["id"]
            load_detail = self.loads_map.get(a["id"])
            
            status_text = "Не распределено"
            status_color = ft.colors.AMBER_400
            assigned_row = None
            
            if load_detail:
                status_text = f"Исполнитель: {load_detail['teacher_name']}"
                status_color = ft.colors.INDIGO_300
                assigned_row = ft.Row(
                    controls=[
                        ft.Icon(name=ft.icons.CHECK_CIRCLE_OUTLINE_ROUNDED, color=ft.colors.GREEN_400, size=14),
                        ft.Text(status_text, size=12, color=ft.colors.WHITE70, weight=ft.FontWeight.W_500, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.IconButton(
                            icon=ft.icons.REMOVE_CIRCLE_OUTLINE_ROUNDED,
                            icon_color=ft.colors.RED_300,
                            icon_size=16,
                            tooltip="Снять нагрузку",
                            on_click=lambda ev, load_id=load_detail["id"]: self.delete_load(load_id)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            else:
                assigned_row = ft.Text(status_text, size=12, color=status_color, weight=ft.FontWeight.BOLD)
                
            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(a["study_plan_element_discipline"], size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                                ft.Container(
                                    content=ft.Text(f"{a['study_plan_element_hours']} ч", size=10, color=ft.colors.INDIGO_300, weight=ft.FontWeight.BOLD),
                                    bgcolor=ft.colors.INDIGO_900_O10,
                                    border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=6, vertical=2)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Text(f"Группа: {a['study_plan_element_group']} | Вид: {a['study_plan_element_class_type']}", size=11, color=ft.colors.WHITE54),
                        ft.Divider(color=ft.colors.WHITE10, height=10),
                        assigned_row
                    ],
                    spacing=3
                ),
                padding=15,
                border_radius=10,
                border=ft.border.all(1, ft.colors.INDIGO_500 if is_selected else ft.colors.WHITE10),
                bgcolor=ft.colors.SURFACE_VARIANT if is_selected else ft.colors.TRANSPARENT,
                on_click=lambda ev, assign=a: self.select_assignment(assign),
                on_hover=self.on_hover_card,
                data=a["id"]
            )
            self.assign_list.controls.append(card)
            
        self.page.update()

    def select_assignment(self, assignment):
        self.selected_assignment = assignment
        self.render_assignments()
        self.teacher_header.value = f"Распределение: {assignment['study_plan_element_discipline']} ({assignment['study_plan_element_class_type']})"
        self.load_teachers_validation()

    def load_teachers_validation(self):
        if not self.selected_assignment:
            return
            
        self.show_loading(True)
        try:
            # Query the backend validation endpoint
            resp = api_client.get(
                f"/api/v1/load/teachers-validation?assignment_id={self.selected_assignment['id']}&department_id={self.current_dept_id}"
            )
            if resp.status_code == 200:
                self.teachers_validation = resp.json()
                self.render_teachers()
            else:
                self.show_snackbar("Ошибка валидации списка преподавателей", ft.colors.RED_400)
        except Exception as e:
            self.show_snackbar(f"Сетевая ошибка: {e}", ft.colors.RED_400)
        finally:
            self.show_loading(False)

    def render_teachers(self):
        self.teacher_list.controls.clear()
        
        if not self.teachers_validation:
            self.teacher_list.controls.append(
                ft.Container(
                    content=ft.Text("Нет преподавателей на этой кафедре", color=ft.colors.WHITE38, size=13),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
            self.page.update()
            return
            
        # Draw each teacher as a premium card
        for t in self.teachers_validation:
            can_assign = t["can_assign"]
            hours = t["current_load_hours"]
            
            # Select workload gauge color
            if hours < 150:
                bar_color = ft.colors.GREEN_400
            elif hours <= 300:
                bar_color = ft.colors.AMBER_400
            else:
                bar_color = ft.colors.RED_400
                
            progress_value = min(1.0, hours / 400.0) # max baseline is 400 hours
            
            # Validation rule layout
            error_row = None
            if not can_assign:
                error_row = ft.Row(
                    controls=[
                        ft.Icon(name=ft.icons.LOCK_ROUNDED, color=ft.colors.RED_400, size=14),
                        ft.Text(f"Недоступен: {t['reason']}", size=11, color=ft.colors.RED_400, weight=ft.FontWeight.W_500, overflow=ft.TextOverflow.CLIP, expand=True)
                    ],
                    spacing=5
                )
                
            teacher_card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            name=ft.icons.PERSON_2_ROUNDED if not can_assign else ft.icons.PERSON_ROUNDED, 
                                            color=ft.colors.WHITE24 if not can_assign else ft.colors.INDIGO_300, 
                                            size=24
                                        ),
                                        ft.Column(
                                            controls=[
                                                ft.Text(t["full_name"], size=14, weight=ft.FontWeight.W_500, color=ft.colors.WHITE if can_assign else ft.colors.WHITE38),
                                                ft.Text(f"{t['category_name']} | Звание: {t['title_name']}", size=11, color=ft.colors.WHITE30 if not can_assign else ft.colors.WHITE54)
                                            ],
                                            spacing=2
                                        )
                                    ],
                                    spacing=12
                                ),
                                # Button or Locked visual indicator
                                ft.ElevatedButton(
                                    text="Назначить",
                                    bgcolor=ft.colors.INDIGO_600,
                                    color=ft.colors.WHITE,
                                    disabled=not can_assign,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                                    on_click=lambda ev, teacher_id=t["id"]: self.assign_teacher(teacher_id)
                                ) if can_assign else ft.Icon(name=ft.icons.LOCK_ROUNDED, color=ft.colors.WHITE24, size=20)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        # Load progress bar
                        ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text("Текущая нагрузка:", size=11, color=ft.colors.WHITE54),
                                        ft.Text(f"{hours} / 400 ч", size=11, color=bar_color, weight=ft.FontWeight.BOLD)
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                                ft.ProgressBar(value=progress_value, color=bar_color, bgcolor=ft.colors.WHITE10, height=4)
                            ],
                            spacing=3
                        ),
                        # Error message if blocked
                        error_row
                    ].copy() if error_row is None else [
                        ft.Row(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(name=ft.icons.PERSON_2_ROUNDED, color=ft.colors.WHITE24, size=24),
                                        ft.Column(
                                            controls=[
                                                ft.Text(t["full_name"], size=14, weight=ft.FontWeight.W_500, color=ft.colors.WHITE38),
                                                ft.Text(f"{t['category_name']} | Звание: {t['title_name']}", size=11, color=ft.colors.WHITE30)
                                            ],
                                            spacing=2
                                        )
                                    ],
                                    spacing=12
                                ),
                                ft.Icon(name=ft.icons.LOCK_ROUNDED, color=ft.colors.WHITE24, size=20)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text("Текущая нагрузка:", size=11, color=ft.colors.WHITE38),
                                        ft.Text(f"{hours} / 400 ч", size=11, color=ft.colors.WHITE38)
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                                ft.ProgressBar(value=progress_value, color=ft.colors.WHITE24, bgcolor=ft.colors.WHITE10, height=4)
                            ],
                            spacing=3
                        ),
                        error_row
                    ],
                    spacing=8
                ),
                padding=15,
                border_radius=8,
                bgcolor=ft.colors.SURFACE_VARIANT if can_assign else ft.colors.TRANSPARENT,
                border=ft.border.all(1, ft.colors.WHITE10 if can_assign else ft.colors.RED_900_O20),
                opacity=1.0 if can_assign else 0.5
            )
            self.teacher_list.controls.append(teacher_card)
            
        self.page.update()

    def assign_teacher(self, teacher_id):
        if not self.selected_assignment:
            return
            
        self.show_loading(True)
        try:
            payload = {
                "teacher_id": teacher_id,
                "assignment_id": self.selected_assignment["id"]
            }
            resp = api_client.post("/api/v1/load/", json_data=payload)
            if resp.status_code == 201:
                self.show_snackbar("Нагрузка успешно распределена на преподавателя!", ft.colors.GREEN_600)
                self.selected_assignment = None
                self.teacher_list.controls.clear()
                self.load_assignments()
            else:
                err = resp.json().get("detail", "Ошибка сохранения")
                self.show_snackbar(f"Ошибка: {err}", ft.colors.RED_400)
        except Exception as e:
            self.show_snackbar(f"Сбой: {e}", ft.colors.RED_400)
        finally:
            self.show_loading(False)

    def delete_load(self, load_id):
        self.show_loading(True)
        try:
            resp = api_client.delete(f"/api/v1/load/{load_id}")
            if resp.status_code == 24 or resp.status_code == 204:
                self.show_snackbar("Распределение нагрузки успешно аннулировано!", ft.colors.GREEN_600)
                self.selected_assignment = None
                self.teacher_list.controls.clear()
                self.load_assignments()
            else:
                self.show_snackbar("Не удалось снять нагрузку", ft.colors.RED_400)
        except Exception as e:
            self.show_snackbar(f"Сбой: {e}", ft.colors.RED_400)
        finally:
            self.show_loading(False)

    def on_hover_card(self, e):
        if e.data == "true":
            is_selected = self.selected_assignment and self.selected_assignment["id"] == e.control.data
            e.control.border = ft.border.all(1, ft.colors.INDIGO_400 if is_selected else ft.colors.WHITE38)
            e.control.bgcolor = ft.colors.WHITE10
        else:
            is_selected = self.selected_assignment and self.selected_assignment["id"] == e.control.data
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
