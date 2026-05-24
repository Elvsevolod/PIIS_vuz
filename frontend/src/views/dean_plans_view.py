import flet as ft
from api_client import api_client

class DeanPlansView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.padding = 0
        self.margin = 0
        
        # State
        self.groups = []
        self.selected_group = None
        self.disciplines = []
        self.class_types = []
        self.control_forms = []
        self.departments = []
        self.study_plans = []
        self.assignments = {} # study_plan_element_id -> assignment object
        
        # UI controls
        self.group_list = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        self.plan_table = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        self.loading_indicator = ft.ProgressBar(visible=False, color=ft.colors.INDIGO_400)
        
        # Top-level headers
        self.group_header = ft.Text("Группы", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
        self.plan_header = ft.Text("Учебный план группы (выберите группу)", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
        
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
                                    self.group_header,
                                    ft.Divider(color=ft.colors.WHITE10),
                                    ft.Container(
                                        content=self.group_list,
                                        expand=True
                                    )
                                ],
                                spacing=10
                            ),
                            width=280,
                            bgcolor=ft.colors.SURFACE,
                            border_radius=12,
                            border=ft.border.all(1, ft.colors.WHITE10),
                            padding=20,
                            expand=False
                        ),
                        # Right side - Study plans & Assignments
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            self.plan_header,
                                            ft.Row(
                                                controls=[
                                                    ft.ElevatedButton(
                                                        text="Новая дисциплина",
                                                        icon=ft.icons.LIBRARY_BOOKS_ROUNDED,
                                                        color=ft.colors.WHITE,
                                                        bgcolor=ft.colors.SURFACE_VARIANT,
                                                        on_click=self.show_create_discipline_dialog,
                                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                                                    ),
                                                    ft.ElevatedButton(
                                                        text="Добавить в план",
                                                        icon=ft.icons.ADD_ROUNDED,
                                                        color=ft.colors.WHITE,
                                                        bgcolor=ft.colors.INDIGO_600,
                                                        on_click=self.show_create_plan_element_dialog,
                                                        visible=False,
                                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                                                    )
                                                ],
                                                spacing=10
                                            )
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Divider(color=ft.colors.WHITE10),
                                    ft.Container(
                                        content=self.plan_table,
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
            # 1. Fetch metadata (class types, control forms)
            resp_meta = api_client.get("/api/v1/plans/metadata")
            if resp_meta.status_code == 200:
                meta = resp_meta.json()
                self.class_types = meta.get("class_types", [])
                self.control_forms = meta.get("control_forms", [])
            
            # 2. Fetch disciplines catalog
            resp_disc = api_client.get("/api/v1/plans/disciplines")
            if resp_disc.status_code == 200:
                self.disciplines = resp_disc.json()
                
            # 3. Fetch departments for assignments dropdown
            resp_dept = api_client.get("/api/v1/departments/")
            if resp_dept.status_code == 200:
                self.departments = resp_dept.json()
            
            # 4. Fetch groups
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
            
            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(g["name"], size=15, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                ft.Text(f"{g['course']} курс", size=10, color=ft.colors.INDIGO_300)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Text(f"Семестр: {g['semester']}", size=11, color=ft.colors.WHITE54)
                    ],
                    spacing=3
                ),
                padding=12,
                border_radius=8,
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
        self.render_groups()
        
        # Show "Add to plan" button
        self.content.controls[1].controls[1].content.controls[0].controls[1].controls[1].visible = True
        self.plan_header.value = f"Учебный план группы {group['name']}"
        
        # Load plans & assignments
        self.load_plans()

    def load_plans(self):
        if not self.selected_group:
            return
            
        self.show_loading(True)
        try:
            # 1. Fetch study plan elements
            resp_plans = api_client.get(f"/api/v1/plans/elements?group_id={self.selected_group['id']}")
            
            # 2. Fetch all department assignments
            resp_assigns = api_client.get("/api/v1/plans/assignments")
            
            if resp_plans.status_code == 200 and resp_assigns.status_code == 200:
                self.study_plans = resp_plans.json()
                
                # Map assignments by study_plan_element_id
                self.assignments = {}
                for a in resp_assigns.json():
                    self.assignments[a["study_plan_element_id"]] = a
                    
                self.render_plans()
            else:
                self.show_snackbar("Ошибка загрузки планов/поручений", ft.colors.RED_400)
        except Exception as e:
            self.show_snackbar(f"Сетевая ошибка: {e}", ft.colors.RED_400)
        finally:
            self.show_loading(False)

    def render_plans(self):
        self.plan_table.controls.clear()
        
        if not self.study_plans:
            self.plan_table.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(name=ft.icons.MENU_BOOK_ROUNDED, size=48, color=ft.colors.WHITE24),
                            ft.Text("Учебный план пока не заполнен", color=ft.colors.WHITE38, size=13),
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
            
        # Draw a custom premium table style
        headers = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("Дисциплина", size=12, color=ft.colors.WHITE38, weight=ft.FontWeight.BOLD, expand=3),
                    ft.Text("Семестр", size=12, color=ft.colors.WHITE38, weight=ft.FontWeight.BOLD, expand=1),
                    ft.Text("Вид занятия", size=12, color=ft.colors.WHITE38, weight=ft.FontWeight.BOLD, expand=2),
                    ft.Text("Часы", size=12, color=ft.colors.WHITE38, weight=ft.FontWeight.BOLD, expand=1),
                    ft.Text("Форма контроля", size=12, color=ft.colors.WHITE38, weight=ft.FontWeight.BOLD, expand=2),
                    ft.Text("Исполнитель (Кафедра)", size=12, color=ft.colors.WHITE38, weight=ft.FontWeight.BOLD, expand=3),
                    ft.Text("Действие", size=12, color=ft.colors.WHITE38, weight=ft.FontWeight.BOLD, expand=2),
                ],
                spacing=10
            ),
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=6
        )
        self.plan_table.controls.append(headers)
        
        # Sort study plans by semester
        sorted_plans = sorted(self.study_plans, key=lambda x: (x["semester"], x["discipline_name"]))
        
        for e in sorted_plans:
            assign = self.assignments.get(e["id"])
            dept_text = assign["department_name"] if assign else "Не поручено"
            dept_color = ft.colors.GREEN_400 if assign else ft.colors.AMBER_400
            
            row = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(e["discipline_name"], size=13, color=ft.colors.WHITE, weight=ft.FontWeight.W_500, expand=3),
                        ft.Text(f"Сем. {e['semester']}", size=13, color=ft.colors.WHITE70, expand=1),
                        ft.Text(e["class_type_name"], size=13, color=ft.colors.WHITE70, expand=2),
                        ft.Text(f"{e['hours']} ч", size=13, color=ft.colors.WHITE70, expand=1),
                        ft.Text(e["control_form_name"], size=13, color=ft.colors.WHITE70, expand=2),
                        ft.Text(dept_text, size=13, color=dept_color, weight=ft.FontWeight.BOLD, expand=3, overflow=ft.TextOverflow.ELLIPSIS),
                        # Action button (Assign or Reassign)
                        ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.icons.ASSIGNMENT_IND_ROUNDED,
                                    icon_color=ft.colors.INDIGO_300,
                                    icon_size=18,
                                    tooltip="Поручить кафедре" if not assign else "Изменить кафедру",
                                    on_click=lambda ev, element=e, current_assign=assign: self.show_assign_department_dialog(element, current_assign)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE_OUTLINE_ROUNDED,
                                    icon_color=ft.colors.RED_300,
                                    icon_size=18,
                                    tooltip="Удалить из плана",
                                    on_click=lambda ev, element=e: self.delete_plan_element(element)
                                )
                            ],
                            spacing=2,
                            expand=2
                        )
                    ],
                    spacing=10
                ),
                padding=ft.padding.symmetric(horizontal=15, vertical=8),
                border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.WHITE10))
            )
            self.plan_table.controls.append(row)
            
        self.page.update()

    def on_hover_card(self, e):
        if e.data == "true":
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
    
    def show_create_discipline_dialog(self, e):
        name_input = ft.TextField(label="Название дисциплины", border_color=ft.colors.WHITE10, focused_border_color=ft.colors.INDIGO_400)
        desc_input = ft.TextField(label="Описание (необязательно)", border_color=ft.colors.WHITE10, focused_border_color=ft.colors.INDIGO_400)
        
        def save_new_discipline(ev):
            if not name_input.value.strip():
                name_input.error_text = "Введите название!"
                dialog.update()
                return
                
            try:
                payload = {
                    "name": name_input.value.strip(),
                    "description": desc_input.value.strip() or None
                }
                resp = api_client.post("/api/v1/plans/disciplines", json_data=payload)
                if resp.status_code == 201:
                    self.show_snackbar("Дисциплина создана и добавлена в справочник!", ft.colors.GREEN_600)
                    dialog.open = False
                    
                    # Refresh disciplines catalog list
                    self.disciplines.append(resp.json())
                    self.page.update()
                else:
                    err = resp.json().get("detail", "Ошибка сохранения")
                    self.show_snackbar(f"Ошибка: {err}", ft.colors.RED_400)
            except Exception as ex:
                self.show_snackbar(f"Сбой: {ex}", ft.colors.RED_400)
                
        dialog = ft.AlertDialog(
            title=ft.Text("Добавить дисциплину в каталог", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[name_input, desc_input],
                spacing=12,
                height=140,
                width=320
            ),
            actions=[
                ft.TextButton("Отмена", on_click=lambda ev: self.close_dialog(dialog)),
                ft.ElevatedButton("Создать", bgcolor=ft.colors.INDIGO_600, color=ft.colors.WHITE, on_click=save_new_discipline)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_create_plan_element_dialog(self, e):
        if not self.disciplines:
            self.show_snackbar("Сначала создайте хотя бы одну дисциплину в каталоге!", ft.colors.AMBER_600)
            return
            
        disc_dropdown = ft.Dropdown(
            label="Дисциплина",
            options=[ft.dropdown.Option(text=d["name"], key=str(d["id"])) for d in self.disciplines],
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
            value=str(self.disciplines[0]["id"])
        )
        
        class_dropdown = ft.Dropdown(
            label="Вид занятия",
            options=[ft.dropdown.Option(text=c["name"], key=str(c["id"])) for c in self.class_types],
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
            value=str(self.class_types[0]["id"]) if self.class_types else None
        )
        
        hours_input = ft.TextField(label="Количество часов", value="36", border_color=ft.colors.WHITE10, focused_border_color=ft.colors.INDIGO_400)
        
        semester_dropdown = ft.Dropdown(
            label="Семестр в плане",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 13)],
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
            value=str(self.selected_group["semester"])
        )
        
        control_dropdown = ft.Dropdown(
            label="Форма контроля",
            options=[ft.dropdown.Option(text=cf["name"], key=str(cf["id"])) for cf in self.control_forms],
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
            value=str(self.control_forms[0]["id"]) if self.control_forms else None
        )
        
        def save_new_plan_element(ev):
            try:
                # Basic hours validation
                hours = int(hours_input.value.strip())
                if hours <= 0:
                    raise ValueError()
            except ValueError:
                hours_input.error_text = "Число > 0!"
                dialog.update()
                return
                
            try:
                payload = {
                    "group_id": self.selected_group["id"],
                    "discipline_id": int(disc_dropdown.value),
                    "class_type_id": int(class_dropdown.value),
                    "course": int((int(semester_dropdown.value) + 1) // 2), # compute course based on semester
                    "semester": int(semester_dropdown.value),
                    "hours": hours,
                    "control_form_id": int(control_dropdown.value)
                }
                
                resp = api_client.post("/api/v1/plans/elements", json_data=payload)
                if resp.status_code == 201:
                    self.show_snackbar("Предмет добавлен в учебный план группы!", ft.colors.GREEN_600)
                    dialog.open = False
                    self.load_plans()
                else:
                    err = resp.json().get("detail", "Ошибка добавления")
                    self.show_snackbar(f"Ошибка: {err}", ft.colors.RED_400)
            except Exception as ex:
                self.show_snackbar(f"Сбой: {ex}", ft.colors.RED_400)
                
        dialog = ft.AlertDialog(
            title=ft.Text(f"Добавить в план группы {self.selected_group['name']}", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[disc_dropdown, class_dropdown, hours_input, semester_dropdown, control_dropdown],
                spacing=12,
                height=340,
                width=320
            ),
            actions=[
                ft.TextButton("Отмена", on_click=lambda ev: self.close_dialog(dialog)),
                ft.ElevatedButton("Добавить", bgcolor=ft.colors.INDIGO_600, color=ft.colors.WHITE, on_click=save_new_plan_element)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_assign_department_dialog(self, element, current_assign):
        if not self.departments:
            self.show_snackbar("Сначала создайте хотя бы одну кафедру в справочниках!", ft.colors.AMBER_600)
            return
            
        dept_dropdown = ft.Dropdown(
            label="Выберите кафедру-исполнителя",
            options=[ft.dropdown.Option(text=d["name"], key=str(d["id"])) for d in self.departments],
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
            value=str(current_assign["department_id"]) if current_assign else str(self.departments[0]["id"])
        )
        
        def save_assignment(ev):
            try:
                # If there's an existing assignment, delete it first to avoid duplicate assignments
                if current_assign:
                    api_client.delete(f"/api/v1/plans/assignments/{current_assign['id']}")
                    
                payload = {
                    "department_id": int(dept_dropdown.value),
                    "study_plan_element_id": element["id"]
                }
                
                resp = api_client.post("/api/v1/plans/assignments", json_data=payload)
                if resp.status_code == 201:
                    self.show_snackbar("Поручение успешно направлено кафедре!", ft.colors.GREEN_600)
                    dialog.open = False
                    self.load_plans()
                else:
                    err = resp.json().get("detail", "Ошибка распределения")
                    self.show_snackbar(f"Ошибка: {err}", ft.colors.RED_400)
            except Exception as ex:
                self.show_snackbar(f"Сбой: {ex}", ft.colors.RED_400)
                
        dialog = ft.AlertDialog(
            title=ft.Text("Направить поручение кафедре", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[
                    ft.Text(f"Предмет: {element['discipline_name']} ({element['class_type_name']})", size=13, color=ft.colors.WHITE70),
                    ft.Text(f"Объем: {element['hours']} часов", size=13, color=ft.colors.WHITE70),
                    ft.Container(height=10),
                    dept_dropdown
                ],
                spacing=5,
                height=180,
                width=320
            ),
            actions=[
                ft.TextButton("Отмена", on_click=lambda ev: self.close_dialog(dialog)),
                ft.ElevatedButton("Поручить", bgcolor=ft.colors.INDIGO_600, color=ft.colors.WHITE, on_click=save_assignment)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def delete_plan_element(self, element):
        def confirm_delete(ev):
            try:
                resp = api_client.delete(f"/api/v1/plans/elements/{element['id']}")
                if resp.status_code == 204:
                    self.show_snackbar("Предмет удален из плана!", ft.colors.GREEN_600)
                    dialog.open = False
                    self.load_plans()
                else:
                    self.show_snackbar("Не удалось удалить элемент плана", ft.colors.RED_400)
            except Exception as ex:
                self.show_snackbar(f"Сбой: {ex}", ft.colors.RED_400)
                
        dialog = ft.AlertDialog(
            title=ft.Text("Подтвердите действие", weight=ft.FontWeight.BOLD),
            content=ft.Text(f"Вы действительно хотите удалить {element['discipline_name']} ({element['class_type_name']}) из учебного плана?", size=14, color=ft.colors.WHITE70),
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
