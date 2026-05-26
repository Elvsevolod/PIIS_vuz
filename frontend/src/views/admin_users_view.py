import flet as ft
from api_client import api_client


class AdminUsersView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.padding = 0
        self.margin = 0

        # State
        self.users = []

        # UI controls
        self.user_list = ft.Column(spacing=8, scroll=ft.ScrollMode.ADAPTIVE)
        self.loading_indicator = ft.ProgressBar(visible=False, color=ft.colors.INDIGO_400)
        self.header = ft.Text("Пользователи системы", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)

        # Create user dialog fields
        self.username_field = ft.TextField(
            label="Логин",
            border_color=ft.colors.SURFACE_VARIANT,
            focused_border_color=ft.colors.INDIGO_400,
            width=300,
        )
        self.password_field = ft.TextField(
            label="Пароль",
            password=True,
            can_reveal_password=True,
            border_color=ft.colors.SURFACE_VARIANT,
            focused_border_color=ft.colors.INDIGO_400,
            width=300,
        )
        self.role_dropdown = ft.Dropdown(
            label="Роль",
            options=[
                ft.dropdown.Option("admin", "Администратор"),
                ft.dropdown.Option("dean", "Деканат"),
                ft.dropdown.Option("department_head", "Зав. кафедрой"),
                ft.dropdown.Option("teacher", "Преподаватель"),
            ],
            width=300,
            border_color=ft.colors.WHITE10,
            focused_border_color=ft.colors.INDIGO_400,
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
                                    ft.ElevatedButton(
                                        text="Добавить пользователя",
                                        icon=ft.icons.PERSON_ADD_ROUNDED,
                                        color=ft.colors.WHITE,
                                        bgcolor=ft.colors.INDIGO_600,
                                        on_click=self.show_create_user_dialog,
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Divider(color=ft.colors.WHITE10),
                            ft.Container(content=self.user_list, expand=True),
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

        self.load_data()

    def show_loading(self, show: bool):
        self.loading_indicator.visible = show
        self.page.update()

    def load_data(self):
        self.show_loading(True)
        try:
            resp = api_client.get("/api/v1/auth/users")
            if resp.status_code == 200:
                self.users = resp.json()
                self.render_users()
            else:
                self.show_snackbar("Ошибка загрузки пользователей", ft.colors.RED_400)
        except Exception as e:
            self.show_snackbar(f"Сетевая ошибка: {e}", ft.colors.RED_400)
        finally:
            self.show_loading(False)

    def render_users(self):
        self.user_list.controls.clear()

        if not self.users:
            self.user_list.controls.append(
                ft.Container(
                    content=ft.Text("Нет пользователей", color=ft.colors.WHITE38, size=13),
                    alignment=ft.alignment.center,
                    padding=20,
                )
            )
            self.page.update()
            return

        # Header row
        self.user_list.controls.append(
            ft.Row(
                controls=[
                    ft.Text("Логин", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE54, width=180),
                    ft.Text("Роль", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE54, width=180),
                    ft.Text("Linked ID", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE54, width=100),
                    ft.Text("", width=60),
                ],
                alignment=ft.MainAxisAlignment.START,
            )
        )
        self.user_list.controls.append(ft.Divider(color=ft.colors.WHITE10, height=1))

        role_names = {
            "admin": "Администратор",
            "dean": "Деканат",
            "department_head": "Зав. кафедрой",
            "teacher": "Преподаватель",
        }

        for u in self.users:
            row = ft.Row(
                controls=[
                    ft.Text(u["username"], size=14, color=ft.colors.WHITE, width=180, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(role_names.get(u["role"], u["role"]), size=14, color=ft.colors.WHITE70, width=180),
                    ft.Text(str(u["linked_entity_id"] or ""), size=14, color=ft.colors.WHITE54, width=100),
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE_ROUNDED,
                        icon_color=ft.colors.RED_300,
                        icon_size=18,
                        tooltip="Удалить пользователя",
                        on_click=lambda e, uid=u["id"], uname=u["username"]: self.delete_user(uid, uname),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            )
            self.user_list.controls.append(row)

        self.page.update()

    def show_create_user_dialog(self, e):
        self.username_field.value = ""
        self.password_field.value = ""
        self.role_dropdown.value = "teacher"

        def save(e):
            username = self.username_field.value.strip()
            password = self.password_field.value.strip()
            role = self.role_dropdown.value

            if not username or not password:
                self.show_snackbar("Заполните все поля", ft.colors.AMBER_400)
                return

            resp = api_client.post(
                "/api/v1/auth/users",
                {"username": username, "password": password, "role": role},
            )
            if resp.status_code == 201:
                dialog.open = False
                self.page.update()
                self.load_data()
                self.show_snackbar("Пользователь создан", ft.colors.GREEN_400)
            else:
                detail = resp.json().get("detail", "Ошибка")
                self.show_snackbar(f"Ошибка: {detail}", ft.colors.RED_400)

        dialog = ft.AlertDialog(
            title=ft.Text("Новый пользователь"),
            content=ft.Column(
                controls=[
                    self.username_field,
                    self.password_field,
                    self.role_dropdown,
                ],
                spacing=10,
                width=300,
            ),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton("Создать", on_click=save, bgcolor=ft.colors.INDIGO_600, color=ft.colors.WHITE),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def delete_user(self, user_id: int, username: str):
        def confirm(e):
            resp = api_client.delete(f"/api/v1/auth/users/{user_id}")
            if resp.status_code in (204, 200):
                dialog.open = False
                self.page.update()
                self.load_data()
                self.show_snackbar(f"Пользователь {username} удалён", ft.colors.GREEN_400)
            else:
                detail = resp.json().get("detail", "Ошибка")
                self.show_snackbar(f"Ошибка: {detail}", ft.colors.RED_400)
                dialog.open = False
                self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"Удалить пользователя {username}?"),
            content=ft.Text("Это действие нельзя отменить."),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton("Удалить", on_click=confirm, bgcolor=ft.colors.RED_600, color=ft.colors.WHITE),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

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
