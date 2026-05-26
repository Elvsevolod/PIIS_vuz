import flet as ft
from api_client import api_client

class LoginView(ft.Container):
    def __init__(self, page: ft.Page, on_login_success):
        super().__init__()
        self.page = page
        self.on_login_success = on_login_success
        self.alignment = ft.alignment.center
        self.expand = True
        
        # UI Input fields styled with modern colors and typography
        self.username_input = ft.TextField(
            label="Имя пользователя",
            prefix_icon=ft.icons.PERSON,
            border_color=ft.colors.SURFACE_VARIANT,
            focused_border_color=ft.colors.INDIGO_400,
            width=320,
            height=50,
            text_size=14,
            on_submit=self.handle_login
        )
        
        self.password_input = ft.TextField(
            label="Пароль",
            prefix_icon=ft.icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_color=ft.colors.SURFACE_VARIANT,
            focused_border_color=ft.colors.INDIGO_400,
            width=320,
            height=50,
            text_size=14,
            on_submit=self.handle_login
        )
        
        self.error_text = ft.Text(
            value="",
            color=ft.colors.RED_400,
            size=12,
            weight=ft.FontWeight.BOLD,
            visible=False
        )
        
        self.login_btn = ft.ElevatedButton(
            text="Войти в систему",
            icon=ft.icons.LOGIN,
            width=320,
            height=46,
            style=ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor={
                    ft.MaterialState.DEFAULT: ft.colors.INDIGO_600, 
                    ft.MaterialState.HOVERED: ft.colors.INDIGO_700
                },
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=self.handle_login
        )
        
        self.progress_bar = ft.ProgressBar(width=320, visible=False, color=ft.colors.INDIGO_400)
        
        # Main login card (glassmorphism/sleek dark card container)
        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(name=ft.icons.SCHOOL_ROUNDED, size=56, color=ft.colors.INDIGO_400),
                    ft.Text(
                        value="ИС ВУЗа",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.WHITE
                    ),
                    ft.Text(
                        value="Управление учебным процессом",
                        size=12,
                        color=ft.colors.WHITE70
                    ),
                    ft.Container(height=20),
                    self.username_input,
                    ft.Container(height=5),
                    self.password_input,
                    ft.Container(height=5),
                    self.error_text,
                    ft.Container(height=5),
                    self.login_btn,
                    self.progress_bar,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.colors.SURFACE,
            border=ft.border.all(1, ft.colors.WHITE10),
            border_radius=16,
            padding=40,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.BLACK87,
                offset=ft.Offset(0, 5)
            )
        )

    def handle_login(self, e):
        username = self.username_input.value.strip()
        password = self.password_input.value.strip()
        
        if not username or not password:
            self.show_error("Пожалуйста, заполните все поля.")
            return
            
        self.error_text.visible = False
        self.login_btn.disabled = True
        self.progress_bar.visible = True
        self.update()
        
        # API call through api_client
        success, error_msg = api_client.login(username, password)
        
        self.progress_bar.visible = False
        self.login_btn.disabled = False
        
        if success:
            self.on_login_success()
        else:
            self.show_error(error_msg or "Неверное имя пользователя или пароль.")
            self.update()

    def show_error(self, message: str):
        self.error_text.value = message
        self.error_text.visible = True
        self.update()
