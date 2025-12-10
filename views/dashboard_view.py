import flet as ft
from controllers.auth_controller import auth_controller

class DashboardView:
    def __init__(self, page: ft.Page):
        self.page = page

    def view(self):
        def logout_click(e):
            auth_controller.logout()
            self.page.go("/")

        return ft.View(
            "/dashboard",
            controls=[
                ft.AppBar(title=ft.Text("Panel Principal"), bgcolor="surface_variant", actions=[
                    ft.IconButton("logout", on_click=logout_click)
                ]),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("¡Bienvenido!", size=24),
                            ft.ElevatedButton("Detectar Antracnosis", icon="camera_alt", on_click=lambda _: self.page.go("/detection"), width=250),
                            ft.ElevatedButton("Ver Informes", icon="assessment", on_click=lambda _: self.page.go("/report"), width=250),
                            ft.ElevatedButton("Mi Perfil", icon="person", on_click=lambda _: self.page.go("/profile"), width=250),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20
                    ),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ]
        )

