import flet as ft
from controllers.auth_controller import auth_controller

class ProfileView:
    def __init__(self, page: ft.Page):
        self.page = page

    def view(self):
        user = auth_controller.current_user
        if not user:
            self.page.go("/")
            return ft.View("/profile", controls=[])

        username_field = ft.TextField(label="Nuevo Usuario", value=user["username"], width=300)
        password_field = ft.TextField(label="Nueva Contraseña", password=True, can_reveal_password=True, width=300)
        status_text = ft.Text()

        def update_click(e):
            new_user = username_field.value if username_field.value != user["username"] else None
            new_pass = password_field.value if password_field.value else None
            
            if not new_user and not new_pass:
                status_text.value = "No se hicieron cambios"
                status_text.color = "orange"
                status_text.update()
                return

            success, message = auth_controller.update_user(user["id"], new_user, new_pass)
            status_text.value = message
            status_text.color = "green" if success else "red"
            status_text.update()
            if success and new_user:
                user["username"] = new_user # Update local reference

        return ft.View(
            "/profile",
            controls=[
                ft.AppBar(title=ft.Text("Perfil"), bgcolor="surface_variant"),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(name="person", size=64),
                            ft.Text(f"Usuario: {user['username']}", size=20, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Text("Editar Perfil", size=16),
                            username_field,
                            password_field,
                            ft.ElevatedButton("Actualizar Perfil", on_click=update_click),
                            status_text,
                            ft.ElevatedButton("Volver al Dashboard", on_click=lambda _: self.page.go("/dashboard")),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=20,
                    expand=True
                )
            ]
        )

