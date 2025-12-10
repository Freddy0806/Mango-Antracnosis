import flet as ft
from controllers.auth_controller import auth_controller

class RegisterView:
    def __init__(self, page: ft.Page):
        self.page = page

    def view(self):
        username_field = ft.TextField(label="Usuario", width=300)
        password_field = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)
        confirm_password_field = ft.TextField(label="Confirmar Contraseña", password=True, width=300)
        error_text = ft.Text(color="red")

        def register_click(e):
            if not username_field.value or not password_field.value:
                error_text.value = "Por favor complete todos los campos"
                error_text.update()
                return
            
            if password_field.value != confirm_password_field.value:
                error_text.value = "Las contraseñas no coinciden"
                error_text.update()
                return

            success, message = auth_controller.register_user(username_field.value, password_field.value)
            if success:
                self.page.snack_bar = ft.SnackBar(ft.Text("¡Registro exitoso! Por favor inicie sesión."))
                self.page.snack_bar.open = True
                self.page.go("/")
            else:
                error_text.value = message
                error_text.update()

        return ft.View(
            "/register",
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Crear Cuenta", size=24, weight=ft.FontWeight.BOLD),
                            username_field,
                            password_field,
                            confirm_password_field,
                            ft.ElevatedButton("Registrarse", on_click=register_click, width=300),
                            ft.TextButton("Volver al Inicio", on_click=lambda _: self.page.go("/")),
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

