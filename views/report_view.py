import flet as ft
from controllers.auth_controller import auth_controller
from controllers.detection_controller import detection_controller

class ReportView:
    def __init__(self, page: ft.Page):
        self.page = page

    def view(self):
        user = auth_controller.current_user
        if not user:
            self.page.go("/")
            return ft.View("/report", controls=[])

        detections = detection_controller.get_user_detections(user["id"])
        
        list_view = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=False)
        
        if not detections:
            list_view.controls.append(ft.Text("No se encontraron detecciones.", italic=True))
        else:
            for d in detections:
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.ListTile(
                                    leading=ft.Icon("image"),
                                    title=ft.Text(f"{d['status']} - {d['phase']}"),
                                    subtitle=ft.Text(f"Confianza: {d['confidence']:.2f} | {d['timestamp']}"),
                                ),
                                ft.Container(
                                    content=ft.Text(f"Tratamiento: {d['treatment']}", size=12),
                                    padding=10
                                )
                            ]
                        ),
                        padding=10
                    )
                )
                list_view.controls.append(card)

        return ft.View(
            "/report",
            controls=[
                ft.AppBar(title=ft.Text("Historial de Informes"), bgcolor="surface_variant"),
                list_view,
                ft.ElevatedButton("Volver", on_click=lambda _: self.page.go("/dashboard")),
            ]
        )

