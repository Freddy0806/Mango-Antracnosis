import flet as ft
from controllers.auth_controller import auth_controller

class LoginView:
    def __init__(self, page: ft.Page):
        self.page = page

    def view(self):
        username_field = ft.TextField(label="Usuario", width=300)
        password_field = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)
        error_text = ft.Text(color="red")

        def login_click(e):
            if not username_field.value or not password_field.value:
                error_text.value = "Por favor complete todos los campos"
                error_text.update()
                return

            success, message = auth_controller.login_user(username_field.value, password_field.value)
            if success:
                self.page.go("/dashboard")
            else:
                error_text.value = message
                error_text.update()

        return ft.View(
            "/",
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Detector de Antracnosis", size=24, weight=ft.FontWeight.BOLD),
                            ft.Icon(name="eco", size=64, color="green"),
                            ft.Text("Iniciar Sesión", size=20),
                            username_field,
                            password_field,
                            ft.ElevatedButton("Entrar", on_click=login_click, width=300),
                            ft.TextButton("Crear Cuenta", on_click=lambda _: self.page.go("/register")),
                            error_text
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ],
            bgcolor="white"
        )

