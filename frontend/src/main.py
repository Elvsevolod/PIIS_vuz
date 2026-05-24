import sys
import os
import flet as ft

# Add current folder to sys.path to support local imports correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views.login_view import LoginView
from views.main_shell import MainShell

def main(page: ft.Page):
    page.title = "Информационная Система ВУЗа (ИС ВУЗа)"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1100
    page.window_height = 720
    page.window_min_width = 950
    page.window_min_height = 650
    page.window_resizable = True
    page.padding = 0
    page.spacing = 0

    # Theme customization matching our design tokens in HSL
    page.theme = ft.Theme(
        color_scheme_seed=ft.colors.INDIGO_500,
        color_scheme=ft.ColorScheme(
            background="#0c0e12",       # HSL(220, 15%, 7%) - Slate Background
            surface="#121620",          # HSL(220, 12%, 11%) - Slate Card Surface
            surface_variant="#181e2b",  # HSL(220, 12%, 16%) - Dark Slate Header
            primary=ft.colors.INDIGO_500,
            on_primary=ft.colors.WHITE,
        )
    )

    def show_login():
        page.clean()
        login_view = LoginView(page, on_login_success=show_main_shell)
        page.add(login_view)
        page.update()

    def show_main_shell():
        page.clean()
        main_shell = MainShell(page, on_logout=show_login)
        page.add(main_shell)
        page.update()

    # Load initial Login Screen
    show_login()

if __name__ == "__main__":
    # To run as desktop, change view to ft.AppView.FLET_APP (or omit view and port)
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8500, web_renderer="html")
