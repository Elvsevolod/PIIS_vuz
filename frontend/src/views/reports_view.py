import flet as ft
from api_client import api_client


class ReportsView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.padding = 0
        self.margin = 0

        # State
        self.groups = []
        self.report_type = "teacher-workload"

        # UI controls
        self.result_area = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        self.loading_indicator = ft.ProgressBar(visible=False, color=ft.colors.INDIGO_400)
        self.header = ft.Text("Отчёты", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)

        # Report type selector
        self.report_type_dropdown = ft.Dropdown(
            label="Тип отчёта",
            options=[
                ft.dropdown.Option("teacher-workload", "Нагрузка преподавателей"),
                ft.dropdown.Option("diploma-distribution", "Распределение дипломников"),
                ft.dropdown.Option("group-performance", "Успеваемость группы"),
            ],
            value="teacher-workload",
            width=300,
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
            on_change=self.handle_report_change,
        )

        # Filters
        self.semester_field = ft.TextField(
            label="Семестр (опционально)",
            border_color=ft.colors.SURFACE_VARIANT,
            focused_border_color=ft.colors.INDIGO_400,
            width=160,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.group_dropdown = ft.Dropdown(
            label="Группа",
            options=[],
            width=260,
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
            visible=False,
        )

        # Layout
        self.content = ft.Column(
            controls=[
                self.loading_indicator,
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    self.header,
                                    ft.Row(
                                        controls=[
                                            self.report_type_dropdown,
                                            self.semester_field,
                                            self.group_dropdown,
                                            ft.ElevatedButton(
                                                text="Сформировать",
                                                icon=ft.icons.REFRESH_ROUNDED,
                                                color=ft.colors.WHITE,
                                                bgcolor=ft.colors.INDIGO_600,
                                                on_click=self.generate_report,
                                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Divider(color=ft.colors.WHITE10),
                            ft.Container(content=self.result_area, expand=True),
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
            spacing=10,
        )

        self.load_groups()

    def show_loading(self, show: bool):
        self.loading_indicator.visible = show
        self.page.update()

    def load_groups(self):
        try:
            resp = api_client.get("/api/v1/students/groups")
            if resp.status_code == 200:
                self.groups = resp.json()
                self.group_dropdown.options = [
                    ft.dropdown.Option(text=g["name"], key=str(g["id"])) for g in self.groups
                ]
        except Exception:
            pass

    def handle_report_change(self, e):
        self.report_type = self.report_type_dropdown.value
        self.group_dropdown.visible = (self.report_type == "group-performance")
        self.semester_field.visible = (self.report_type != "diploma-distribution")
        self.result_area.controls.clear()
        self.page.update()

    def generate_report(self, e):
        self.show_loading(True)
        self.result_area.controls.clear()

        try:
            if self.report_type == "teacher-workload":
                self._load_teacher_workload()
            elif self.report_type == "diploma-distribution":
                self._load_diploma_distribution()
            elif self.report_type == "group-performance":
                self._load_group_performance()
        except Exception as e:
            self.show_snackbar(f"Ошибка: {e}", ft.colors.RED_400)
        finally:
            self.show_loading(False)

    def _load_teacher_workload(self):
        params = {}
        sem = (self.semester_field.value or "").strip()
        if sem:
            params["semester"] = int(sem)

        resp = api_client.get("/api/v1/reports/teacher-workload", params=params if params else None)
        if resp.status_code != 200:
            self.show_snackbar("Ошибка загрузки отчёта", ft.colors.RED_400)
            return

        data = resp.json()
        items = data.get("items", [])

        self.result_area.controls.append(
            ft.Row(
                controls=[
                    ft.Text(f"Всего часов: {data['total_hours']}", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_300),
                    ft.Text(f"Преподавателей: {data['teachers_count']}", size=14, color=ft.colors.WHITE70),
                ],
                spacing=20,
            )
        )
        self.result_area.controls.append(ft.Divider(color=ft.colors.WHITE10))

        # Header
        self.result_area.controls.append(
            ft.Row(
                controls=[
                    ft.Text("Преподаватель", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE54, width=200),
                    ft.Text("Дисциплина", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE54, width=180),
                    ft.Text("Вид", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE54, width=120),
                    ft.Text("Сем", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE54, width=50),
                    ft.Text("Часы", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_300, width=60),
                ],
            )
        )

        for item in items:
            self.result_area.controls.append(
                ft.Row(
                    controls=[
                        ft.Text(item["teacher_name"], size=13, color=ft.colors.WHITE, width=200, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(item["discipline_name"], size=13, color=ft.colors.WHITE70, width=180, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(item["class_type_name"], size=13, color=ft.colors.WHITE70, width=120),
                        ft.Text(str(item["semester"]), size=13, color=ft.colors.WHITE54, width=50),
                        ft.Text(str(item["hours"]), size=13, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_300, width=60),
                    ],
                )
            )

        self.page.update()

    def _load_diploma_distribution(self):
        resp = api_client.get("/api/v1/reports/diploma-distribution")
        if resp.status_code != 200:
            self.show_snackbar("Ошибка загрузки отчёта", ft.colors.RED_400)
            return

        data = resp.json()

        # Summary section
        self.result_area.controls.append(
            ft.Text(f"Всего дипломных работ: {data['total_diplomas']}", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_300)
        )
        self.result_area.controls.append(ft.Divider(color=ft.colors.WHITE10))

        summary = data.get("summary", [])
        self.result_area.controls.append(
            ft.Text("По кафедрам:", size=13, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE54)
        )
        for row in summary:
            self.result_area.controls.append(
                ft.Row(
                    controls=[
                        ft.Text(row["department_name"], size=13, color=ft.colors.WHITE, width=300),
                        ft.Text(str(row["diploma_count"]), size=13, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_300),
                    ],
                )
            )

        # Details
        details = data.get("details", [])
        self.result_area.controls.append(ft.Divider(color=ft.colors.WHITE10, height=20))
        self.result_area.controls.append(
            ft.Text("Детальный список:", size=13, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE54)
        )

        self.result_area.controls.append(
            ft.Row(
                controls=[
                    ft.Text("Студент", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE54, width=200),
                    ft.Text("Тема", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE54, width=250),
                    ft.Text("Руководитель", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE54, width=200),
                ],
            )
        )
        for d in details:
            self.result_area.controls.append(
                ft.Row(
                    controls=[
                        ft.Text(d["student_name"], size=13, color=ft.colors.WHITE, width=200, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(d["title"], size=13, color=ft.colors.WHITE70, width=250, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(d["supervisor_name"], size=13, color=ft.colors.WHITE54, width=200, overflow=ft.TextOverflow.ELLIPSIS),
                    ],
                )
            )

        self.page.update()

    def _load_group_performance(self):
        group_id = self.group_dropdown.value
        if not group_id:
            self.show_snackbar("Выберите группу", ft.colors.AMBER_400)
            return

        params = {"group_id": int(group_id)}
        sem = (self.semester_field.value or "").strip()
        if sem:
            params["semester"] = int(sem)

        resp = api_client.get("/api/v1/reports/group-performance", params=params)
        if resp.status_code != 200:
            self.show_snackbar("Ошибка загрузки отчёта", ft.colors.RED_400)
            return

        data = resp.json()

        self.result_area.controls.append(
            ft.Row(
                controls=[
                    ft.Text(f"Группа: {data['group_name']}", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ft.Text(f"Студентов: {data['total_students']}", size=14, color=ft.colors.WHITE70),
                    ft.Text(f"Дисциплин: {data['total_elements']}", size=14, color=ft.colors.WHITE70),
                ],
                spacing=20,
            )
        )
        self.result_area.controls.append(ft.Divider(color=ft.colors.WHITE10))

        for student in data["students"]:
            pct_color = ft.colors.GREEN_400 if student["completion_pct"] >= 50 else ft.colors.RED_400

            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(student["student_name"], size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                ft.Text(f"{student['completion_pct']}%", size=14, weight=ft.FontWeight.BOLD, color=pct_color),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(f"Зачётка: {student['gradebook_number']}", size=11, color=ft.colors.WHITE54),
                    ]
                    + [
                        ft.Row(
                            controls=[
                                ft.Text(g["discipline_name"], size=12, color=ft.colors.WHITE70, width=200, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(g["control_form_name"], size=12, color=ft.colors.WHITE54, width=80),
                                ft.Text(
                                    g["grade"],
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.GREEN_400 if g["grade"] not in ("Не аттестован", "Неудовлетворительно") else ft.colors.RED_400,
                                    width=170,
                                ),
                            ],
                        )
                        for g in student["grades"]
                    ],
                    spacing=4,
                ),
                padding=12,
                border_radius=8,
                border=ft.border.all(1, ft.colors.WHITE10),
                bgcolor=ft.colors.SURFACE_VARIANT,
            )
            self.result_area.controls.append(card)

        self.page.update()

    def show_snackbar(self, message: str, color: str):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=color),
            bgcolor=ft.colors.SURFACE_VARIANT,
            duration=3000,
        )
        self.page.snack_bar.open = True
        self.page.update()
