import flet as ft
from api_client import api_client


class AdminDirectoriesView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.padding = 0
        self.margin = 0

        # State
        self.faculties = []
        self.departments = []
        self.selected_faculty = None

        # UI controls
        self.faculty_list = ft.Column(spacing=8, scroll=ft.ScrollMode.ADAPTIVE)
        self.dept_list = ft.Column(spacing=8, scroll=ft.ScrollMode.ADAPTIVE)
        self.loading_indicator = ft.ProgressBar(visible=False, color=ft.colors.INDIGO_400)

        self.faculty_header = ft.Text("Факультеты", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
        self.dept_header = ft.Text("Кафедры факультета", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)

        # Create faculty dialog fields
        self.faculty_name_field = ft.TextField(
            label="Название факультета",
            border_color=ft.colors.SURFACE_VARIANT,
            focused_border_color=ft.colors.INDIGO_400,
            width=300,
        )

        # Create department dialog fields
        self.dept_name_field = ft.TextField(
            label="Название кафедры",
            border_color=ft.colors.SURFACE_VARIANT,
            focused_border_color=ft.colors.INDIGO_400,
            width=300,
        )

        # Add department button (saved reference to avoid magic indices)
        self.add_dept_btn = ft.IconButton(
            icon=ft.icons.ADD_ROUNDED,
            icon_color=ft.colors.INDIGO_300,
            tooltip="Добавить кафедру",
            on_click=self.show_create_dept_dialog,
            visible=False,
        )

        # Layout
        self.content = ft.Column(
            controls=[
                self.loading_indicator,
                ft.Row(
                    controls=[
                        # Left: Faculties
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            self.faculty_header,
                                            ft.IconButton(
                                                icon=ft.icons.ADD_ROUNDED,
                                                icon_color=ft.colors.INDIGO_300,
                                                tooltip="Добавить факультет",
                                                on_click=self.show_create_faculty_dialog,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    ft.Divider(color=ft.colors.WHITE10),
                                    ft.Container(content=self.faculty_list, expand=True),
                                ],
                                spacing=10,
                            ),
                            width=340,
                            bgcolor=ft.colors.SURFACE,
                            border_radius=12,
                            border=ft.border.all(1, ft.colors.WHITE10),
                            padding=20,
                            expand=False,
                        ),
                        # Right: Departments
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            self.dept_header,
                                            self.add_dept_btn,
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    ft.Divider(color=ft.colors.WHITE10),
                                    ft.Container(content=self.dept_list, expand=True),
                                ],
                                spacing=10,
                            ),
                            expand=True,
                            bgcolor=ft.colors.SURFACE,
                            border_radius=12,
                            border=ft.border.all(1, ft.colors.WHITE10),
                            padding=20,
                        ),
                    ],
                    expand=True,
                    spacing=20,
                )
            ],
            expand=True,
            spacing=10,
        )

        self.load_data()

    def show_loading(self, show: bool):
        self.loading_indicator.visible = show
        self.page.update()

    def load_data(self):
        self.show_loading(True)
        try:
            resp = api_client.get("/api/v1/faculties/")
            if resp.status_code == 200:
                self.faculties = resp.json()
                self.render_faculties()
            else:
                self.show_snackbar("Ошибка загрузки факультетов", ft.colors.RED_400)
        except Exception as e:
            self.show_snackbar(f"Сетевая ошибка: {e}", ft.colors.RED_400)
        finally:
            self.show_loading(False)

    def render_faculties(self):
        self.faculty_list.controls.clear()

        if not self.faculties:
            self.faculty_list.controls.append(
                ft.Container(
                    content=ft.Text("Нет факультетов", color=ft.colors.WHITE38, size=13),
                    alignment=ft.alignment.center,
                    padding=20,
                )
            )
            self.page.update()
            return

        for f in self.faculties:
            is_selected = self.selected_faculty and self.selected_faculty["id"] == f["id"]

            card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(f["name"], size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE, expand=True),
                        ft.IconButton(
                            icon=ft.icons.DELETE_OUTLINE_ROUNDED,
                            icon_color=ft.colors.RED_300,
                            icon_size=18,
                            tooltip="Удалить факультет",
                            on_click=lambda e, fid=f["id"]: self.delete_faculty(fid),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=12,
                border_radius=8,
                border=ft.border.all(1, ft.colors.INDIGO_500 if is_selected else ft.colors.WHITE10),
                bgcolor=ft.colors.SURFACE_VARIANT if is_selected else ft.colors.TRANSPARENT,
                on_click=lambda e, fac=f: self.select_faculty(fac),
            )
            self.faculty_list.controls.append(card)

        self.page.update()

    def select_faculty(self, faculty):
        self.selected_faculty = faculty
        self.render_faculties()
        self.dept_header.value = f"Кафедры — {faculty['name']}"
        self.add_dept_btn.visible = True
        self.load_departments()

    def load_departments(self):
        if not self.selected_faculty:
            return
        self.show_loading(True)
        try:
            resp = api_client.get("/api/v1/departments/")
            if resp.status_code == 200:
                all_depts = resp.json()
                self.departments = [d for d in all_depts if d["faculty_id"] == self.selected_faculty["id"]]
                self.render_departments()
            else:
                self.show_snackbar("Ошибка загрузки кафедр", ft.colors.RED_400)
        except Exception as e:
            self.show_snackbar(f"Сетевая ошибка: {e}", ft.colors.RED_400)
        finally:
            self.show_loading(False)

    def render_departments(self):
        self.dept_list.controls.clear()

        if not self.departments:
            self.dept_list.controls.append(
                ft.Container(
                    content=ft.Text("Нет кафедр на этом факультете", color=ft.colors.WHITE38, size=13),
                    alignment=ft.alignment.center,
                    padding=20,
                )
            )
            self.page.update()
            return

        for d in self.departments:
            card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(d["name"], size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE, expand=True),
                        ft.IconButton(
                            icon=ft.icons.DELETE_OUTLINE_ROUNDED,
                            icon_color=ft.colors.RED_300,
                            icon_size=18,
                            tooltip="Удалить кафедру",
                            on_click=lambda e, did=d["id"]: self.delete_department(did),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=12,
                border_radius=8,
                border=ft.border.all(1, ft.colors.WHITE10),
                bgcolor=ft.colors.TRANSPARENT,
            )
            self.dept_list.controls.append(card)

        self.page.update()

    # --- Faculty CRUD ---

    def show_create_faculty_dialog(self, e):
        self.faculty_name_field.value = ""

        def save(e):
            name = self.faculty_name_field.value.strip()
            if not name:
                self.show_snackbar("Введите название факультета", ft.colors.AMBER_400)
                return
            resp = api_client.post("/api/v1/faculties/", {"name": name})
            if resp.status_code == 201:
                dialog.open = False
                self.page.update()
                self.load_data()
                self.show_snackbar("Факультет создан", ft.colors.GREEN_400)
            else:
                detail = resp.json().get("detail", "Ошибка")
                self.show_snackbar(f"Ошибка: {detail}", ft.colors.RED_400)

        dialog = ft.AlertDialog(
            title=ft.Text("Новый факультет"),
            content=self.faculty_name_field,
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton("Создать", on_click=save, bgcolor=ft.colors.INDIGO_600, color=ft.colors.WHITE),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def delete_faculty(self, faculty_id: int):
        def confirm(e):
            resp = api_client.delete(f"/api/v1/faculties/{faculty_id}")
            if resp.status_code in (204, 200):
                dialog.open = False
                self.page.update()
                self.selected_faculty = None
                self.dept_list.controls.clear()
                self.dept_header.value = "Кафедры факультета"
                self.add_dept_btn.visible = False
                self.load_data()
                self.show_snackbar("Факультет удалён", ft.colors.GREEN_400)
            else:
                detail = resp.json().get("detail", "Ошибка")
                self.show_snackbar(f"Ошибка: {detail}", ft.colors.RED_400)
                dialog.open = False
                self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Удалить факультет?"),
            content=ft.Text("Это действие нельзя отменить. Все связанные кафедры и группы также будут затронуты."),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton("Удалить", on_click=confirm, bgcolor=ft.colors.RED_600, color=ft.colors.WHITE),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    # --- Department CRUD ---

    def show_create_dept_dialog(self, e):
        self.dept_name_field.value = ""

        def save(e):
            name = self.dept_name_field.value.strip()
            if not name:
                self.show_snackbar("Введите название кафедры", ft.colors.AMBER_400)
                return
            if not self.selected_faculty:
                self.show_snackbar("Выберите факультет", ft.colors.AMBER_400)
                return
            resp = api_client.post("/api/v1/departments/", {"name": name, "faculty_id": self.selected_faculty["id"]})
            if resp.status_code == 201:
                dialog.open = False
                self.page.update()
                self.load_departments()
                self.show_snackbar("Кафедра создана", ft.colors.GREEN_400)
            else:
                detail = resp.json().get("detail", "Ошибка")
                self.show_snackbar(f"Ошибка: {detail}", ft.colors.RED_400)

        dialog = ft.AlertDialog(
            title=ft.Text(f"Новая кафедра — {self.selected_faculty['name']}" if self.selected_faculty else "Новая кафедра"),
            content=self.dept_name_field,
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton("Создать", on_click=save, bgcolor=ft.colors.INDIGO_600, color=ft.colors.WHITE),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def delete_department(self, dept_id: int):
        def confirm(e):
            resp = api_client.delete(f"/api/v1/departments/{dept_id}")
            if resp.status_code in (204, 200):
                dialog.open = False
                self.page.update()
                self.load_departments()
                self.show_snackbar("Кафедра удалена", ft.colors.GREEN_400)
            else:
                detail = resp.json().get("detail", "Ошибка")
                self.show_snackbar(f"Ошибка: {detail}", ft.colors.RED_400)
                dialog.open = False
                self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Удалить кафедру?"),
            content=ft.Text("Это действие нельзя отменить."),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton("Удалить", on_click=confirm, bgcolor=ft.colors.RED_600, color=ft.colors.WHITE),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    # --- Helpers ---

    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()

    def show_snackbar(self, message: str, color: str):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=color),
            bgcolor=ft.colors.SURFACE_VARIANT,
            duration=3000,
        )
        self.page.snack_bar.open = True
        self.page.update()
