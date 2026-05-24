import flet as ft
from api_client import api_client
from views.dean_students_view import DeanStudentsView
from views.dean_plans_view import DeanPlansView
from views.dept_load_view import DeptLoadView

class MainShell(ft.Row):
    def __init__(self, page: ft.Page, on_logout):
        super().__init__()
        self.page = page
        self.on_logout_callback = on_logout
        self.expand = True
        self.spacing = 0
        
        # User details
        self.username = api_client.current_user.get("username", "Пользователь") if api_client.current_user else "Пользователь"
        self.role = api_client.current_user.get("role", "guest") if api_client.current_user else "guest"
        
        # Content view container
        self.content_container = ft.Container(
            content=self.get_welcome_view(),
            expand=True,
            padding=30,
            bgcolor=ft.colors.SURFACE,
        )
        
        # Active view label in header
        self.section_title = ft.Text(
            value="🧭 Панель управления",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.WHITE
        )
        
        # Header bar
        self.header = ft.Container(
            content=ft.Row(
                controls=[
                    self.section_title,
                    ft.Row(
                        controls=[
                            ft.Icon(name=ft.icons.ACCOUNT_CIRCLE_ROUNDED, size=24, color=ft.colors.INDIGO_300),
                            ft.Text(
                                value=f"{self.username} ({self.get_role_display(self.role)})",
                                size=14,
                                color=ft.colors.WHITE70,
                                weight=ft.FontWeight.W_500
                            ),
                        ],
                        spacing=8
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            height=60,
            padding=ft.padding.only(left=30, right=30),
            border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.WHITE10)),
            bgcolor=ft.colors.SURFACE_VARIANT
        )
        
        # Build Navigation Sidebar based on user role
        self.sidebar = self.build_sidebar()
        
        # Main client area combines header and content
        self.main_area = ft.Column(
            controls=[
                self.header,
                self.content_container
            ],
            expand=True,
            spacing=0
        )
        
        # Add to Row
        self.controls = [
            self.sidebar,
            ft.VerticalDivider(width=1, color=ft.colors.WHITE10),
            self.main_area
        ]

    def get_role_display(self, role: str) -> str:
        roles = {
            "admin": "Администратор",
            "dean": "Деканат",
            "department_head": "Зав. Кафедрой",
            "teacher": "Преподаватель"
        }
        return roles.get(role, "Пользователь")

    def build_sidebar(self) -> ft.Container:
        sidebar_items = []
        
        # Overview (All roles)
        sidebar_items.append(
            self.create_nav_item("🧭 Обзор", ft.icons.DASHBOARD_ROUNDED, "overview", active=True)
        )
        
        # Admin section (Admin only)
        if self.role == "admin":
            sidebar_items.append(
                ft.Container(
                    content=ft.Text("АДМИНИСТРИРОВАНИЕ", size=11, color=ft.colors.WHITE38, weight=ft.FontWeight.BOLD),
                    margin=ft.margin.only(top=15, left=10, bottom=5)
                )
            )
            sidebar_items.append(self.create_nav_item("📁 Справочники", ft.icons.FOLDER_ROUNDED, "admin_directories"))
            sidebar_items.append(self.create_nav_item("👥 Пользователи", ft.icons.PEOPLE_ROUNDED, "admin_users"))
            
        # Dean section (Dean or Admin)
        if self.role in ["admin", "dean"]:
            sidebar_items.append(
                ft.Container(
                    content=ft.Text("ДЕКАНАТ", size=11, color=ft.colors.WHITE38, weight=ft.FontWeight.BOLD),
                    margin=ft.margin.only(top=15, left=10, bottom=5)
                )
            )
            sidebar_items.append(self.create_nav_item("📅 Учебные планы", ft.icons.PLAYLIST_ADD_CHECK_ROUNDED, "dean_plans"))
            sidebar_items.append(self.create_nav_item("👨‍🎓 Группы и студенты", ft.icons.SCHOOL_ROUNDED, "dean_students"))
            
        # Zavkhaf section (Department Head or Admin)
        if self.role in ["admin", "department_head"]:
            sidebar_items.append(
                ft.Container(
                    content=ft.Text("КАФЕДРА", size=11, color=ft.colors.WHITE38, weight=ft.FontWeight.BOLD),
                    margin=ft.margin.only(top=15, left=10, bottom=5)
                )
            )
            sidebar_items.append(self.create_nav_item("💼 Распределение нагрузки", ft.icons.ASSIGNMENT_IND_ROUNDED, "dept_load"))
            sidebar_items.append(self.create_nav_item("🎓 Дипломные работы", ft.icons.ASSIGNMENT_ROUNDED, "dept_diplomas"))
            
        # Teacher section (Teacher or Admin)
        if self.role in ["admin", "teacher"]:
            sidebar_items.append(
                ft.Container(
                    content=ft.Text("ПРЕПОДАВАТЕЛЬ", size=11, color=ft.colors.WHITE38, weight=ft.FontWeight.BOLD),
                    margin=ft.margin.only(top=15, left=10, bottom=5)
                )
            )
            sidebar_items.append(self.create_nav_item("📝 Моя нагрузка", ft.icons.TASK_ROUNDED, "teacher_load"))
            sidebar_items.append(self.create_nav_item("📊 Аттестация", ft.icons.GRADING_ROUNDED, "teacher_grades"))
            
        # Footer spacer & Logout
        sidebar_items.append(ft.Container(expand=True))
        sidebar_items.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(name=ft.icons.LOGOUT_ROUNDED, color=ft.colors.RED_300, size=20),
                        ft.Text("Выйти из системы", color=ft.colors.RED_300, size=14, weight=ft.FontWeight.W_500)
                    ],
                    spacing=12
                ),
                padding=ft.padding.all(12),
                border_radius=8,
                on_click=self.handle_logout,
                on_hover=self.on_hover_btn,
                margin=ft.margin.only(bottom=15)
            )
        )
        
        # Sidebar container with modern look
        return ft.Container(
            content=ft.Column(
                controls=sidebar_items,
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH
            ),
            width=260,
            bgcolor=ft.colors.BACKGROUND,
            padding=ft.padding.all(15),
            expand=False
        )

    def create_nav_item(self, text: str, icon: str, key: str, active: bool = False) -> ft.Container:
        bg_color = ft.colors.WHITE10 if active else ft.colors.TRANSPARENT
        text_color = ft.colors.INDIGO_300 if active else ft.colors.WHITE70
        icon_color = ft.colors.INDIGO_300 if active else ft.colors.WHITE38
        
        nav_item = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(name=icon, color=icon_color, size=20),
                    ft.Text(text, color=text_color, size=14, weight=ft.FontWeight.W_500 if active else ft.FontWeight.NORMAL)
                ],
                spacing=12
            ),
            padding=ft.padding.all(12),
            border_radius=8,
            bgcolor=bg_color,
            on_click=lambda e: self.navigate_to(key, text),
            on_hover=self.on_hover_nav,
            data=key
        )
        return nav_item

    def on_hover_btn(self, e):
        e.control.bgcolor = ft.colors.WHITE10 if e.data == "true" else ft.colors.TRANSPARENT
        e.control.update()

    def on_hover_nav(self, e):
        if e.data == "true":
            e.control.bgcolor = ft.colors.WHITE10
        else:
            is_active = False
            if isinstance(e.control.content, ft.Row) and len(e.control.content.controls) >= 2:
                is_active = (e.control.content.controls[1].color == ft.colors.INDIGO_300)
            if not is_active:
                e.control.bgcolor = ft.colors.TRANSPARENT
        e.control.update()

    def navigate_to(self, key: str, title: str):
        # Update active state in sidebar
        for item in self.sidebar.content.controls:
            if isinstance(item, ft.Container) and item.data:
                is_active = (item.data == key)
                item.bgcolor = ft.colors.WHITE10 if is_active else ft.colors.TRANSPARENT
                row = item.content
                row.controls[0].color = ft.colors.INDIGO_300 if is_active else ft.colors.WHITE38
                row.controls[1].color = ft.colors.INDIGO_300 if is_active else ft.colors.WHITE70
                row.controls[1].weight = ft.FontWeight.W_500 if is_active else ft.FontWeight.NORMAL
        
        self.section_title.value = title
        
        # Load appropriate view
        if key == "overview":
            self.content_container.content = self.get_welcome_view()
        elif key == "dean_students":
            self.content_container.content = DeanStudentsView(self.page)
        elif key == "dean_plans":
            self.content_container.content = DeanPlansView(self.page)
        elif key == "dept_load":
            self.content_container.content = DeptLoadView(self.page)
        else:
            # Placeholder for future views
            self.content_container.content = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(name=ft.icons.CONSTRUCTION_ROUNDED, size=64, color=ft.colors.WHITE38),
                        ft.Text(f"Модуль '{title}' в разработке", size=18, color=ft.colors.WHITE70, weight=ft.FontWeight.BOLD),
                        ft.Text("Этот экран будет реализован в соответствии с планом спринта.", size=12, color=ft.colors.WHITE38)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                ),
                alignment=ft.alignment.center,
                expand=True
            )
            
        self.page.update()

    def get_welcome_view(self) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(f"Добро пожаловать в ИС ВУЗа, {self.username}!", size=24, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Ваша текущая роль в системе: {self.get_role_display(self.role)}", size=14, color=ft.colors.INDIGO_300),
                    ft.Divider(color=ft.colors.WHITE10, height=30),
                    ft.Text("Для начала работы выберите нужный раздел в левом меню.", size=14, color=ft.colors.WHITE70),
                    ft.Container(height=20),
                    ft.Row(
                        controls=[
                            self.create_info_card("👨‍🎓 Студенты", "Мониторинг групп и успеваемости студентов в реальном времени.", ft.icons.PEOPLE_ROUNDED),
                            self.create_info_card("💼 Учебная нагрузка", "Интеллектуальный контроль распределения часов и видов занятий.", ft.icons.ASSIGNMENT_IND_ROUNDED),
                            self.create_info_card("📊 Сессия и зачеты", "Удобное выставление оценок в электронные аттестационные ведомости.", ft.icons.GRADING_ROUNDED),
                        ],
                        spacing=20,
                        alignment=ft.MainAxisAlignment.START
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=5
            ),
            expand=True
        )

    def create_info_card(self, title: str, desc: str, icon: str) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(name=icon, color=ft.colors.INDIGO_300, size=32),
                    ft.Text(title, size=16, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                    ft.Text(desc, size=12, color=ft.colors.WHITE54)
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START
            ),
            width=240,
            height=160,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border=ft.border.all(1, ft.colors.WHITE10),
            border_radius=12,
            padding=20
        )

    def handle_logout(self, e):
        api_client.clear_auth()
        self.on_logout_callback()
