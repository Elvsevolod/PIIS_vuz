import flet as ft
from api_client import api_client

class TeacherGradesView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.padding = 0
        self.margin = 0
        
        # State
        self.teachers = []
        self.selected_teacher_id = None
        self.loads = []
        self.selected_load = None
        self.students = []
        self.grades = []
        self.attestations = {} # student_id -> attestation object
        
        # Sync indicator states
        self.sync_indicators = {} # student_id -> Icon control
        
        # UI controls
        self.load_list = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        self.gradebook_table = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        self.loading_indicator = ft.ProgressBar(visible=False, color=ft.colors.INDIGO_400)
        
        # Header text
        self.load_header = ft.Text("Моя нагрузка (группы и предметы)", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
        self.gradebook_header = ft.Text("Электронная ведомость аттестации", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
        
        # Teacher selector (visible for Admin to select which teacher's workload to view)
        self.teacher_dropdown = ft.Dropdown(
            label="Выберите преподавателя для ведомости",
            options=[],
            width=320,
            height=46,
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
            on_change=self.handle_teacher_change,
            visible=False
        )
        
        # Layout Column
        self.content = ft.Column(
            controls=[
                self.loading_indicator,
                ft.Row(
                    controls=[
                        # Left side - Workloads list
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    self.teacher_dropdown,
                                    self.load_header,
                                    ft.Divider(color=ft.colors.WHITE10),
                                    ft.Container(
                                        content=self.load_list,
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
                        # Right side - Gradebook table
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    self.gradebook_header,
                                    ft.Divider(color=ft.colors.WHITE10),
                                    ft.Container(
                                        content=self.gradebook_table,
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
        
        self.load_initial_data()

    def show_loading(self, show: bool):
        self.loading_indicator.visible = show
        self.page.update()

    def load_initial_data(self):
        self.show_loading(True)
        try:
            # 1. If admin, load teacher dropdown to let them test as different teachers
            role = api_client.current_user.get("role") if api_client.current_user else "guest"
            if role == "admin":
                self.teacher_dropdown.visible = True
                resp_teachers = api_client.get("/api/v1/teachers/")
                if resp_teachers.status_code == 200:
                    self.teachers = resp_teachers.json()
                    self.teacher_dropdown.options = [
                        ft.dropdown.Option(text=t["full_name"], key=str(t["id"])) for t in self.teachers
                    ]
                    if self.teachers:
                        self.teacher_dropdown.value = str(self.teachers[0]["id"])
                        self.selected_teacher_id = self.teachers[0]["id"]
            else:
                # If logged in as teacher, use their linked teacher ID
                self.selected_teacher_id = api_client.current_user.get("linked_entity_id")
            
            self.load_teacher_workloads()
            
        except Exception as e:
            self.show_snackbar(f"Сетевая ошибка: {e}", ft.colors.RED_400)
        finally:
            self.show_loading(False)

    def load_teacher_workloads(self):
        if not self.selected_teacher_id:
            self.load_list.controls.clear()
            self.load_list.controls.append(ft.Text("Нагрузка не найдена", color=ft.colors.WHITE38, size=13))
            self.page.update()
            return
            
        try:
            # Fetch load allocations
            resp = api_client.get("/api/v1/load/")
            if resp.status_code == 200:
                # Filter allocations by currently selected teacher
                self.loads = [l for l in resp.json() if l["teacher_id"] == self.selected_teacher_id]
                self.render_workloads()
            else:
                self.show_snackbar("Ошибка загрузки нагрузок", ft.colors.RED_400)
        except Exception as e:
            self.show_snackbar(f"Сбой: {e}", ft.colors.RED_400)

    def handle_teacher_change(self, e):
        self.selected_teacher_id = int(self.teacher_dropdown.value)
        self.selected_load = None
        self.gradebook_table.controls.clear()
        self.load_teacher_workloads()

    def render_workloads(self):
        self.load_list.controls.clear()
        
        if not self.loads:
            self.load_list.controls.append(
                ft.Container(
                    content=ft.Text("У этого преподавателя нет закрепленной нагрузки", color=ft.colors.WHITE38, size=13),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
            self.page.update()
            return
            
        for l in self.loads:
            is_selected = self.selected_load and self.selected_load["id"] == l["id"]
            
            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(l["discipline_name"], size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                                ft.Container(
                                    content=ft.Text(f"{l['hours']} ч", size=10, color=ft.colors.INDIGO_300, weight=ft.FontWeight.BOLD),
                                    bgcolor=ft.colors.INDIGO_900_O10,
                                    border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=6, vertical=2)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Text(f"Семестр: {l['semester']} | Вид: {l['class_type_name']}", size=11, color=ft.colors.WHITE54)
                    ],
                    spacing=3
                ),
                padding=12,
                border_radius=8,
                border=ft.border.all(1, ft.colors.INDIGO_500 if is_selected else ft.colors.WHITE10),
                bgcolor=ft.colors.SURFACE_VARIANT if is_selected else ft.colors.TRANSPARENT,
                on_click=lambda ev, workload=l: self.select_workload(workload),
                on_hover=self.on_hover_card,
                data=l["id"]
            )
            self.load_list.controls.append(card)
            
        self.page.update()

    def select_workload(self, workload):
        self.selected_load = workload
        self.render_workloads()
        
        # Load the electronic gradebook sheet
        self.load_gradebook()

    def load_gradebook(self):
        if not self.selected_load:
            return
            
        self.show_loading(True)
        try:
            # 1. Fetch study plan element of the load to get group ID and control form ID
            # First, fetch all study elements to extract it
            resp_elements = api_client.get(f"/api/v1/plans/elements?group_id=1") # baseline load group check
            # Wait, in api_client we can query details or retrieve from list!
            # Since selected_load has hours, semester, class_type, we can find the group ID and study plan element ID from the assignment details.
            # Actually, let's query all assignments to extract group ID and study plan element details!
            resp_assigns = api_client.get("/api/v1/plans/assignments")
            
            group_id = None
            study_plan_element_id = None
            control_form_id = None
            
            if resp_assigns.status_code == 200:
                for a in resp_assigns.json():
                    if a["id"] == self.selected_load["assignment_id"]:
                        study_plan_element_id = a["study_plan_element_id"]
                        # Fetch the study plan element details to get group_id and control_form_id
                        # We can fetch elements for group 1 or query the elements list.
                        # Wait! Since plans.py API endpoint elements is: GET /api/v1/plans/elements?group_id={group_id}
                        # We can fetch all elements for groups or deduce it.
                        # Let's write a python/SQL query in backend to check element by ID or let's inspect element_id.
                        # Actually, our plans.py elements endpoint returns StudyPlanElementResponse which contains group_id and control_form_id!
                        # We can query all elements for a group, or to make it extremely bulletproof:
                        # We fetch all study elements for the group of that assignment.
                        # How to get group of that assignment? It's in a["study_plan_element_group"] name!
                        # And we can fetch groups, match by name, get group ID, and fetch elements!
                        # This is a highly robust way to crawl:
                        resp_groups = api_client.get("/api/v1/students/groups")
                        if resp_groups.status_code == 200:
                            matched_group = next((g for g in resp_groups.json() if g["name"] == a["study_plan_element_group"]), None)
                            if matched_group:
                                group_id = matched_group["id"]
                                
                        # Fetch study elements for this group
                        if group_id:
                            resp_elems = api_client.get(f"/api/v1/plans/elements?group_id={group_id}")
                            if resp_elems.status_code == 200:
                                elem = next((e for e in resp_elems.json() if e["id"] == study_plan_element_id), None)
                                if elem:
                                    control_form_id = elem["control_form_id"]
            
            if group_id and study_plan_element_id and control_form_id:
                # 2. Fetch students of that group
                resp_students = api_client.get(f"/api/v1/students/?group_id={group_id}")
                # 3. Fetch acceptable grades for the control form
                resp_grades = api_client.get(f"/api/v1/grades/grades?control_form_id={control_form_id}")
                # 4. Fetch saved attestations
                resp_atts = api_client.get(f"/api/v1/grades/attestations?study_plan_element_id={study_plan_element_id}")
                
                if resp_students.status_code == 200 and resp_grades.status_code == 200 and resp_atts.status_code == 200:
                    self.students = resp_students.json()
                    self.grades = resp_grades.json()
                    
                    # Map attestations by student_id
                    self.attestations = {a["student_id"]: a for a in resp_atts.json()}
                    
                    self.selected_plan_element_id = study_plan_element_id
                    self.render_gradebook()
                else:
                    self.show_snackbar("Ошибка загрузки ведомости", ft.colors.RED_400)
            else:
                self.show_snackbar("Не удалось связать поручение с группой/формой контроля", ft.colors.RED_400)
                
        except Exception as e:
            self.show_snackbar(f"Сетевая ошибка: {e}", ft.colors.RED_400)
        finally:
            self.show_loading(False)

    def render_gradebook(self):
        self.gradebook_table.controls.clear()
        
        if not self.students:
            self.gradebook_table.controls.append(
                ft.Container(
                    content=ft.Text("В этой группе нет студентов для аттестации", color=ft.colors.WHITE38, size=13),
                    alignment=ft.alignment.center,
                    padding=40
                )
            )
            self.page.update()
            return
            
        # Draw Electronic Gradebook Table headers
        headers = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("ФИО Студента", size=12, color=ft.colors.WHITE38, weight=ft.FontWeight.BOLD, expand=4),
                    ft.Text("Номер зачетки", size=12, color=ft.colors.WHITE38, weight=ft.FontWeight.BOLD, expand=2),
                    ft.Text("Оценка / Зачет", size=12, color=ft.colors.WHITE38, weight=ft.FontWeight.BOLD, expand=3),
                    ft.Text("Статус синхронизации", size=12, color=ft.colors.WHITE38, weight=ft.FontWeight.BOLD, expand=2),
                ],
                spacing=10
            ),
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=6
        )
        self.gradebook_table.controls.append(headers)
        
        self.sync_indicators = {}
        
        for s in self.students:
            saved_att = self.attestations.get(s["id"])
            current_grade_id = str(saved_att["grade_id"]) if saved_att else None
            
            # Create grade dropdown for student
            grade_dropdown = ft.Dropdown(
                options=[ft.dropdown.Option(text=g["value"], key=str(g["id"])) for g in self.grades],
                width=180,
                height=38,
                border_color=ft.colors.WHITE10,
                focused_border_color=ft.colors.INDIGO_400,
                value=current_grade_id,
                on_change=lambda e, student_id=s["id"]: self.handle_autosave(student_id, e.control.value)
            )
            
            # Sync indicator (green check icon or empty/spinner)
            sync_icon = ft.Icon(
                name=ft.icons.CHECK_CIRCLE_OUTLINE_ROUNDED, 
                color=ft.colors.GREEN_400 if saved_att else ft.colors.TRANSPARENT, 
                size=16
            )
            self.sync_indicators[s["id"]] = sync_icon
            
            row = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(s["full_name"], size=13, color=ft.colors.WHITE, weight=ft.FontWeight.W_500, expand=4),
                        ft.Text(s["gradebook_number"], size=13, color=ft.colors.WHITE70, expand=2),
                        ft.Container(content=grade_dropdown, expand=3),
                        ft.Row(
                            controls=[
                                sync_icon,
                                ft.Text("Синхронизировано" if saved_att else "Нет оценки", size=11, color=ft.colors.WHITE38 if not saved_att else ft.colors.WHITE70)
                            ],
                            spacing=5,
                            expand=2
                        )
                    ],
                    spacing=10
                ),
                padding=ft.padding.symmetric(horizontal=15, vertical=5),
                border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.WHITE10))
            )
            self.gradebook_table.controls.append(row)
            
        self.page.update()

    def handle_autosave(self, student_id: int, grade_id: str):
        # Update sync icon to let user see autosave syncing in progress!
        self.sync_indicators[student_id].name = ft.icons.SYNC_ROUNDED
        self.sync_indicators[student_id].color = ft.colors.INDIGO_400
        self.sync_indicators[student_id].update()
        
        try:
            payload = {
                "student_id": student_id,
                "study_plan_element_id": self.selected_plan_element_id,
                "grade_id": int(grade_id)
            }
            resp = api_client.post("/api/v1/grades/attestations", json_data=payload)
            if resp.status_code == 201:
                # Autosave success - show green checkmark instantly!
                self.sync_indicators[student_id].name = ft.icons.CHECK_CIRCLE_OUTLINE_ROUNDED
                self.sync_indicators[student_id].color = ft.colors.GREEN_400
                self.show_snackbar("Оценка сохранена (автосохранение)!", ft.colors.GREEN_600)
            else:
                self.sync_indicators[student_id].name = ft.icons.ERROR_OUTLINE_ROUNDED
                self.sync_indicators[student_id].color = ft.colors.RED_400
                err = resp.json().get("detail", "Ошибка сохранения")
                self.show_snackbar(f"Ошибка автосохранения: {err}", ft.colors.RED_400)
        except Exception as e:
            self.sync_indicators[student_id].name = ft.icons.ERROR_OUTLINE_ROUNDED
            self.sync_indicators[student_id].color = ft.colors.RED_400
            self.show_snackbar(f"Сбой сети: {e}", ft.colors.RED_400)
            
        self.sync_indicators[student_id].update()
        # Refresh the sync label
        # To keep it simple, the dropdown change callback triggers update of sync indicator control directly.
        # Let's rebuild the table row state to update the text labels too
        self.load_gradebook()

    def on_hover_card(self, e):
        if e.data == "true":
            is_selected = self.selected_load and self.selected_load["id"] == e.control.data
            e.control.border = ft.border.all(1, ft.colors.INDIGO_400 if is_selected else ft.colors.WHITE38)
            e.control.bgcolor = ft.colors.WHITE10
        else:
            is_selected = self.selected_load and self.selected_load["id"] == e.control.data
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
